# Bérold vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/berold/build.py) —
# la garde disciplinée, l'attaque de base « Estoc de l'hoplite », l'attaque spéciale « Bouclier de la phalange » —
# dans le style lisse de l'interface (comme Kael : heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/berold/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/berold/)
#   python3 refonte-graphique/ui-moderne/heros/berold/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#
# Méthode : chaque image redessine berold.py dans une POSE (buste qui respire et se penche depuis les hanches, tête,
# cimier dont le haut se balance et dont la queue répond à contretemps, pans de la cape, jupe de languettes ; le bras
# proche suit le poing par cinématique inverse (épaule → coude → poignet), le poing tient la lance : plantée au repos
# (le poing glisse le long de la hampe au souffle), tenue pendant les attaques ; le bouclier se déplace avec le bras
# lointain). Les poses clés reprennent celles du pixel art (mêmes poings, mêmes angles de lance, mêmes temps : un
# soldat, gestes nets, tenues courtes et dures), reliées par des courbes douces sans dépassement, 24 images/s.
# Les effets (filets d'air de l'estoc, éclat de feu, braises, fumée, poussière, couronne de feu, voile de feu doré,
# anneau de feu au sol, lueur rouge du défi et sa marque) : dégradés, un seul contour, aucun flou SVG ; jamais de
# rayons droits répétés.
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
import berold as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'berold')
TMP = os.environ.get('BEROLD_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-52, -34, 272, 153.0)        # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
FINK = '#3a0c18'                     # le contour du feu (comme la crinière de Kael)
LAVA = K.LAVA
G0, A0, GD0 = K.G0, K.ANG0, K.GD0
U0 = K.unit(A0)


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


PAIRS = {'head': ('headx', 'heady'), 'G': ('gx', 'gy'), 'sh': ('shx', 'shy')}
SCAL = ['crouch', 'lean', 'tilt', 'ct', 'cq', 'cpl', 'cpr', 'pg', 'cri', 'ang', 'gd', 'stretch', 'hot', 'srot', 'shot',
        'inhale']
STEP = ['grip', 'behind']            # ce qui bascule d'un coup (le poing change de prise, la lance passe derrière)
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, ct=0, cq=0, cpl=0, cpr=0, pg=0, cri=0, ang=A0, gd=GD0, stretch=0, hot=0,
             srot=0, shot=0, inhale=0, headx=0, heady=0, gx=G0[0], gy=G0[1], shx=0, shy=0, grip=0, behind=0)
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        elif key == 'ad':                       # la lance levée de (dx, dy), même angle
            d['gx'], d['gy'] = G0[0] + v[0], G0[1] + v[1]
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés ; les bascules (prise,
    lance derrière) prennent la valeur de la clé la plus proche."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    out = {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}
    near = min(range(len(ts)), key=lambda i: abs(ts[i] - t) + (0 if ts[i] <= t else 1e-6))
    for n in STEP:
        out[n] = fl[near][n]
    return out


# ======================================================================== les actions (poses clés, comme le pixel art)
# Le pixel art donne le point de prise (le milieu du poing) en pixels du dessin, et l'angle de la lance (90 = droit vers
# le haut) : ici l'angle est compté comme l'écran (−90 = vers le haut, 0 = vers l'ennemi).
H1 = dict(grip=1)
# 2) « Estoc de l'hoplite » : il lève la lance, la fait basculer par-dessus sa tête (derrière le cimier), l'arme à
# l'horizontale à hauteur d'épaule (poing près de l'oreille, buste en arrière, tenu), ESTOC par-dessus le bord du
# bouclier, impact (bras tendu, fente, le bouclier pousse, la pointe rougeoie, arrêt), il ramène, repasse par-dessus
# sa tête et replante.
ATTACK = [
    (0, {}),
    (90, dict(ad=(0, -4), crouch=1, head=(0, 1), ct=1, cq=1)),
    (150, dict(G=(35.5, 47.5), ang=-38, behind=1, crouch=1, lean=-1, head=(0, 1), ct=1, cq=1, cpl=1, **H1)),
    (210, dict(G=(38.8, 55.4), ang=2, crouch=1, lean=-2, head=(-1, 1), tilt=-2, ct=-1, cq=1, cpl=1, cpr=1, pg=1, **H1)),
    (370, dict(G=(39.2, 55.6), ang=2, crouch=1.2, lean=-2.3, head=(-1.2, 1.2), tilt=-2.4, ct=-1, cq=1.2, cpl=1, cpr=1, pg=1, **H1)),
    (420, dict(G=(62.5, 56.2), ang=3, stretch=6, crouch=1, lean=2, head=(1, 0), ct=-1, cq=-1, cpl=-1, cpr=-1, sh=(1, 0), pg=-1, **H1)),
    (460, dict(G=(72.5, 56.8), ang=4, hot=2, stretch=2, crouch=2, lean=3, head=(1, 0), tilt=2, ct=-2, cq=-1, cpl=-1, cpr=-1, sh=(2, 0), pg=-2, **H1)),
    (590, dict(G=(72.2, 56.8), ang=4, hot=2, crouch=2, lean=3, head=(1, 0), tilt=2, ct=-1.5, cq=-1, cpl=-1, cpr=-1, sh=(2, 0), pg=-1.5, **H1)),
    (690, dict(G=(71.5, 56.8), ang=4, hot=1, crouch=2, lean=3, head=(1, 0), ct=-1, cq=-1, cpl=0, cpr=-1, sh=(2, 0), pg=-1, **H1)),
    (780, dict(G=(48.5, 56.0), ang=0, crouch=1, lean=1, cpl=1, sh=(1, 0), **H1)),
    (840, dict(G=(34.5, 48.5), ang=-48, behind=1, crouch=1, head=(0, 1), ct=1, cq=1, cpl=1, cpr=1, **H1)),
    (930, dict(ad=(0, -3), crouch=1, head=(0, 1), ct=1, cpr=1)),
    (1040, dict(crouch=1, cq=-1)),
    (1170, {}),
]
ATTACK_HIT = 460

# 3) « Bouclier de la phalange » (sort d'équipe) : il lève la lance et la PLANTE (poussière, couronne de feu au pied),
# l'emblème chauffe, il LÈVE HAUT son bouclier embrasé : un voile de feu doré en naît et l'enveloppe (arrêt sur la
# bulle), qui s'ouvre en ANNEAU de feu posé au sol tout autour de lui ; puis le défi : il frappe deux fois son bouclier
# de sa lance en criant (lueur rouge, la marque bat au-dessus du casque), et revient en garde.
SH_HALF, SH_HIGH = (9, -11), (17, -22)
ARMED = dict(G=(36.5, 47.5), ang=-32, behind=1, **H1)
STRIKE = dict(G=(62.5, 62.5), ang=6, **H1)
SPECIAL = [
    (0, {}),
    (80, dict(ad=(0, -5), crouch=1, head=(0, 1), ct=1, cq=1, shot=1)),
    (170, dict(crouch=2, head=(0, 1), ct=-1, cq=1, cpl=1, cpr=1, shot=2)),
    (250, dict(crouch=1, ct=1, cpr=1, sh=SH_HALF, srot=-6, shot=3)),
    (340, dict(inhale=1, head=(0, -1), tilt=-1, ct=-1, cq=-1, sh=SH_HIGH, srot=-10, shot=3)),
    (410, dict(inhale=1, head=(0, -1), tilt=-1, cq=-1, cpl=-1, sh=SH_HIGH, srot=-10, shot=3)),
    (480, dict(inhale=1, head=(0, -1.2), tilt=-1.4, ct=1, cpl=-1, cpr=-1, sh=SH_HIGH, srot=-10, shot=3)),
    (680, dict(inhale=1, head=(0, -1), tilt=-1, cq=1, cpr=-1, sh=SH_HIGH, srot=-10, shot=3)),
    (750, dict(inhale=0.5, ct=-1, cq=1, cpl=1, sh=SH_HIGH, srot=-10, shot=2)),
    (820, dict(ad=(0, -4), crouch=1, head=(0, 1), cpl=1, cpr=1, sh=SH_HALF, srot=-5, shot=2)),
    (890, dict(G=(35.5, 47.5), ang=-38, behind=1, crouch=1, lean=-1, head=(0, 1), ct=1, cq=1, cpl=1, shot=1, **H1)),
    (950, dict(crouch=1, lean=-2, head=(-1, 1), tilt=-2, ct=-1, cq=1, cpl=1, cpr=1, shot=1, **ARMED)),
    (1030, dict(crouch=1.2, lean=-2.3, head=(-1.2, 1.2), tilt=-2.4, ct=-1, cq=1, cpl=1, cpr=1, shot=1, **ARMED)),
    (1070, dict(crouch=2, lean=1, head=(1, 0), tilt=1, ct=-2, cq=-1, cpl=-1, cpr=-1, sh=(-1, 0), shot=2, cri=1, **STRIKE)),
    (1160, dict(G=(38.5, 49.5), ang=-24, behind=1, crouch=1, lean=-1, head=(0, 1), ct=0, cq=0, shot=1, cri=0.4, **H1)),
    (1230, dict(crouch=2, lean=1, head=(1, -1), tilt=2, ct=-2, cq=-2, cpl=-1, cpr=-1, sh=(-1, 0), shot=2, cri=1, **STRIKE)),
    (1430, dict(crouch=2, lean=1, head=(1, -0.6), tilt=1.6, ct=-1.6, cq=-1.6, cpl=-1, cpr=-1, sh=(-1, 0), shot=2, cri=1, **STRIKE)),
    (1540, dict(crouch=2, lean=1, head=(1, 0), ct=-1, cq=-1, cpr=-1, shot=1, cri=0.8, **STRIKE)),
    (1620, dict(G=(48.5, 56.0), ang=0, crouch=1, lean=1, cpl=1, **H1)),
    (1680, dict(G=(34.5, 48.5), ang=-48, behind=1, crouch=1, head=(0, 1), ct=1, cq=1, cpl=1, cpr=1, **H1)),
    (1770, dict(ad=(0, -3), crouch=1, head=(0, 1), ct=1, cpr=1)),
    (1870, dict(crouch=1, cq=-1)),
    (2000, {}),
]
SP_PLANT, SP_BUBBLE, SP_RING, SP_HIT1, SP_HIT2 = 170, 480, 680, 1070, 1230


# ======================================================================== la respiration (en boucle)
IDLE = 1.46                          # la durée d'un souffle (s), le rythme du pixel art


def idle_offsets(T):
    """Immobile comme un soldat : le souffle soulève le buste, à l'expiration il se tasse un peu ; la tête suit avec
    retard, le haut du cimier se balance (deux temps de retard), sa queue répond à contretemps ; les pans de la cape
    et la jupe ondulent à peine. Le poing glisse le long de la hampe plantée."""
    u = 2 * math.pi * T / IDLE
    br = 0.5 - 0.5 * math.cos(u)
    cr = 0.6 * (0.5 + 0.5 * math.cos(u + 0.5))
    d = dict(breath=br, crouch=cr, heady=0.35 * math.sin(u - 0.9), tilt=0.5 * math.sin(u - 1.1),
             ct=0.9 * math.sin(u - 1.7), cq=0.8 * math.sin(u - 2.8), cpl=0.6 * math.sin(u - 1.3),
             cpr=0.6 * math.sin(u - 2.1), pg=0.4 * math.sin(u - 1.0))
    # le poing suit l'épaule (le long de la hampe, qui ne bouge pas)
    dy = cr * 0.85 - 0.55 * br
    t = -dy / abs(U0[1])
    d['gx'], d['gy'], d['gd'] = U0[0] * t, U0[1] * t, t
    return d


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
        w = min(1.0, max(0.0, 1 - tl / 90), max(0.0, (tl - (dur - 200)) / 200))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or keyed([(0, {}), (1, {})], 0)
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath'] + P.pop('inhale')
    for n in STEP:
        P[n] = src[n]
    P['behind'] = bool(P['behind'] > 0.5)
    for k, (a, b) in PAIRS.items():
        P[k] = (P.pop(a), P.pop(b))
    P['blink'] = 1.0 if (w > 0.95 and 0.95 <= (T % 3.6) < 1.03) else 0.0
    return P, tl


# ======================================================================== les effets (un seul contour, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour ; une 4e valeur = pas de silhouette (reflet peint)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, gold=False):
    """Une langue de feu posée : large et pâle à la base, fine et rouge au bout, en S (comme Kael)."""
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
    if gold:
        gout = g_lin(fig, p0, p3, [(0, LAVA[0]), (0.4, LAVA[1]), (0.8, LAVA[2]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95, 'n')], w=1.2, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def fireball(fig, c, r, seed=0, op=1.0, hot=1.0):
    """Un éclat de feu : quelques boules réunies sous un contour, coeur blanc-jaune en haut à droite, bord rouge."""
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
    return outlined([(ellipse(x, y, rr, rr), gr, 1) for x, y, rr in balls], w=1.2, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules sous un contour doux, éclairées en haut à droite (comme Kael)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def dust(fig, cx, cy, r, op=1.0):
    """Un petit nuage de poussière soulevé au sol (beige)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy - 0.4 * r, r), (cx + 0.9 * r, cy, 0.7 * r), (cx - 0.9 * r, cy + 0.1 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f6e4c0'), (0.55, '#d6b68a'), (1, '#9c7c64')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#5a3e46" stroke="#5a3e46" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def sparkle(fig, c, R, op=1.0, rot=0.0):
    """L'éclat du choc (le bois sur le bord d'or) : une étoile à quatre branches courbes, coeur blanc."""
    if R < 0.4 or op <= 0.02:
        return ''
    cx, cy = c
    pts = []
    for i in range(8):
        a = math.radians(rot + 45 * i)
        r = R if i % 2 == 0 else R * 0.24
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.7)
    gr = g_rad(fig, c, R, [(0, '#ffffff'), (0.35, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


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


# ---- l'attaque de base
HIT = {}


def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        tip = ctx['tip']
        ang = P['ang']
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        n = (-u[1], u[0])
        # les filets d'air chaud de l'estoc : deux fuseaux pâles le long du fer, et un petit croissant devant
        s = env(tl, 372, 410, 450, 520)
        if s > 0:
            for side, col in ((1, '#ffffff'), (-1, '#d8e2f6')):
                p0 = (tip[0] - 34 * u[0] + side * 1.6 * n[0], tip[1] - 34 * u[1] + side * 1.6 * n[1])
                p1 = (tip[0] - 16 * u[0] + side * 4.6 * n[0], tip[1] - 16 * u[1] + side * 4.6 * n[1])
                p2 = (tip[0] - 2 * u[0] + side * 4.2 * n[0], tip[1] - 2 * u[1] + side * 4.2 * n[1])
                p3 = (tip[0] + 9 * u[0] + side * 0.6 * n[0], tip[1] + 9 * u[1] + side * 0.6 * n[1])
                from atelier import bez
                pts = bez(p0, p1, p2, p3, 16)
                ws = [0.15 + 1.7 * math.sin(math.pi * i / 16) for i in range(17)]
                fig.fx_back.append('<path d="%s" fill="%s" opacity="%g"/>' % (ribbon(pts, ws).d(), col, 0.75 * s))
        # l'impact : la pointe rougeoie, éclat de feu, braises, puis fumée
        if tl >= ATTACK_HIT - 10 and 'p' not in HIT:
            HIT['p'] = tip
        if 'p' in HIT and tl >= ATTACK_HIT - 10:
            T = HIT['p']
            k = (tl - ATTACK_HIT) / 1000.0
            fig.glow(T[0] + 2, T[1], 14, 14, '#ff8a2a', 0.45 * env(tl, ATTACK_HIT - 10, ATTACK_HIT + 20, 600, 760))
            fb = env(tl, ATTACK_HIT - 10, ATTACK_HIT + 30, 560, 700)
            fig.fx_front.append(fireball(fig, (T[0] + 3 + 10 * max(0, k), T[1] - 1 - 6 * max(0, k)), 4.6 * (0.6 + 0.4 * fb) * (1 + 0.6 * max(0, k)),
                                         seed=2, op=fb, hot=1.0 if tl < 600 else 0.0))
            for j, (vx, vy, r) in enumerate(((42, -30, 0.8), (54, 6, 0.7), (26, -46, 0.6), (60, -14, 0.9), (36, 18, 0.55))):
                if k > 0:
                    p = ballistic((T[0] + 3, T[1]), (vx, vy), 60, k)
                    fig.fx_front.append(ember(fig, p[0], p[1], r, op=env(tl, ATTACK_HIT, ATTACK_HIT + 40, 620, 900)))
            for j, (dx, dy, r0, t0) in enumerate(((5, -6, 2.0, 560), (10, -10, 1.6, 620), (2, -12, 1.4, 680))):
                kk = (tl - t0) / 500
                if 0 < kk < 1:
                    fig.fx_front.append(smoke(fig, T[0] + dx + 3 * kk, T[1] + dy - 10 * kk, r0 * (0.7 + 0.8 * kk), op=0.85 * env(kk, 0, 0.15, 0.5, 1)))
        if tl < 300:
            HIT.clear()
    return f


# ---- l'attaque spéciale
def ring_band(cx, cy, rx, ry, h, a0, a1, n=40):
    """Un morceau du mur de feu de l'anneau (posé au sol) : de l'angle a0 à a1 (degrés, 0 = à droite, 90 = devant)."""
    lo, hi = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        lo.append((x, y))
        hi.append((x, y - h))
    return sm(lo + hi[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.6)


def ring_line(cx, cy, rx, ry, a0, a1, w, n=40):
    pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    ws = [w * min(1, 4 * i / n, 4 * (n - i) / n) + 0.1 for i in range(n + 1)]
    return ribbon(pts, ws), pts


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        C = ctx['shield']
        butt = ctx['butt']
        # -- l'emblème chauffe : de petites flammes montent du bord du bouclier (côté ennemi et en haut)
        lv = env(tl, 60, 260, 470, 560)
        if lv > 0:
            spots = [(-66, 0.85), (-31, 1.0), (4, 0.6), (-100, 0.45)]
            for j, (a, hk) in enumerate(spots):
                ar = math.radians(a + P['srot'])
                bx = C[0] + K.SRX * 0.92 * math.cos(ar)
                by = C[1] + K.SRY * 0.92 * math.sin(ar)
                h = (4 + 9 * lv) * hk * (1 + 0.15 * math.sin(tl / 40 + j * 1.9))
                fig.fx_front.append(tongue(fig, (bx, by), h * 1.25, 3.4 + 2.0 * lv * hk, bend=0.8 if j % 2 else -0.7,
                                           lean=0.25 * math.cos(ar), op=min(1, 1.6 * lv)))
        # -- la lance plantée : poussière des deux côtés, petite couronne de feu, braises
        pk = (tl - SP_PLANT) / 1000.0
        if 0 <= pk < 0.6:
            x = butt[0]
            o = env(pk, 0, 0.03, 0.2, 0.6)
            fig.fx_front.append(dust(fig, x - 5 - 10 * pk, GR - 1.2, 1.8 + 3 * pk, op=o))
            fig.fx_back.append(dust(fig, x + 6 + 10 * pk, GR - 1.4, 1.6 + 2.6 * pk, op=o))
            fo = env(pk, 0, 0.02, 0.08, 0.22)
            for j, (dx, h, b) in enumerate(((-2.4, 6, -0.8), (0.4, 9, 0.5), (2.6, 7, 0.8))):
                fig.fx_back.append(tongue(fig, (x + dx, GR), h * (0.6 + 0.6 * fo), 3.0, bend=b, lean=dx * 0.06, op=fo))
            fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="1.2" fill="%s" opacity="%g"/>' % (
                fm(x), fm(GR), fm(7 - 3 * pk), LAVA[2], 0.8 * env(pk, 0, 0.02, 0.15, 0.5)))
            for j, (vx, vy) in enumerate(((-30, -50), (26, -62), (8, -76))):
                p = ballistic((x, GR - 2), (vx, vy), 120, pk)
                fig.fx_front.append(ember(fig, p[0], p[1], 0.6, op=env(pk, 0, 0.02, 0.3, 0.55)))
        # -- le voile de feu doré : il naît du bouclier levé et grandit jusqu'à l'envelopper tout entier
        grow = monotone([340, 410, 480, 680], [0.3, 0.68, 1.0, 1.0], tl) if 330 <= tl < 700 else None
        if grow is not None:
            o = 1.0 if tl < 680 else 0.0
            DC, DR = (68.0, GR - 58.0), (58.0, 66.0)
            cx = C[0] + (DC[0] - C[0]) * grow
            cy = C[1] + (DC[1] - C[1]) * grow
            rx = 15 + (DR[0] - 15) * grow
            ry = 17 + (DR[1] - 17) * grow
            veil(fig, cx, cy, rx, ry, tl, o, flash=env(tl, 470, 490, 520, 600))
        # -- l'anneau de feu doré posé au sol, tout autour de lui, qui s'éloigne, se défait en arcs et s'éteint
        rk = (tl - SP_RING) / 420.0
        if 0 <= rk < 1:
            ring(fig, rk)
        # -- le défi : chocs sur le bouclier, lueur rouge qui pulse, la marque au-dessus du casque
        for th in (SP_HIT1, SP_HIT2):
            k = (tl - th) / 1000.0
            if 0 <= k < 0.25:
                G = P['G']
                a = math.radians(P['ang'])
                xc = C[0] - K.SRX * 0.86
                pc = (xc, G[1] + (xc - G[0]) * math.tan(a))
                fig.fx_front.append(sparkle(fig, pc, 7.5 * (1 - 2 * k) if k < 0.4 else 0, op=env(k, 0, 0.01, 0.06, 0.16), rot=20 + 90 * k))
                for j, (vx, vy) in enumerate(((-30, -40), (24, -52), (-8, -60), (34, -20))):
                    p = ballistic(pc, (vx, vy), 160, k)
                    fig.fx_front.append(ember(fig, p[0], p[1], 0.55, op=env(k, 0, 0.01, 0.1, 0.25)))
        tint = monotone([SP_HIT1 - 10, SP_HIT1 + 30, SP_HIT2 - 20, SP_HIT2 + 30, 1430, 1560, 1700],
                        [0, 0.7, 0.45, 1.0, 0.9, 0.35, 0], tl) if SP_HIT1 - 10 <= tl < 1700 else 0
        if tint > 0.01:
            hx, hy = ctx['chest']
            fig.glow(hx, hy - 14, 46, 60, '#ff3c46', 0.5 * tint)
            fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="44" ry="60" fill="%s"/>' % (
                fm(hx), fm(hy - 10), g_rad(fig, (hx, hy - 10), 50, [(0, '#ff4650', 0.22 * tint), (0.6, '#ff3046', 0.12 * tint), (1, '#ff3046', 0)])))
        mk = env(tl, SP_HIT2 - 10, SP_HIT2 + 40, 1460, 1640)
        if mk > 0:
            hx, hy = ctx['head']
            pulse = 1 + 0.12 * math.sin((tl - SP_HIT2) / 45)
            mark(fig, (hx - 9, hy - 46), 5.2 * pulse * (0.7 + 0.3 * mk), mk)
        # -- le bouclier refroidit : de petites bouffées montent de l'emblème
        for j, t0 in enumerate((1430, 1500, 1580)):
            kk = (tl - t0) / 420
            if 0 < kk < 1:
                fig.fx_front.append(smoke(fig, C[0] + 3 - 2 * kk + j, C[1] - 18 - 10 * kk - 3 * j, 1.2 + 1.2 * kk, op=0.8 * env(kk, 0, 0.15, 0.5, 1)))
    return f


def veil(fig, cx, cy, rx, ry, tl, op, flash=0.0):
    """La bulle de feu doré, translucide : l'intérieur à peine teinté (derrière lui), le bord lumineux (plus épais et
    plus clair en haut à droite, plus rouge en bas à gauche), de petites langues de feu qui dansent sur le bord à des
    places irrégulières ; coupée par le sol."""
    if op <= 0.01:
        return
    clip = fig.uid('c')
    fig.defs.append('<clipPath id="%s"><rect x="-400" y="-400" width="900" height="%s"/></clipPath>' % (clip, fm(GR + 400)))
    inner = g_rad(fig, (cx + rx * 0.3, cy - ry * 0.35), max(rx, ry) * 1.2,
                  [(0, '#fff2b0', 0.16 + 0.12 * flash), (0.7, '#ffcc5a', 0.22 + 0.1 * flash), (1, '#ffb43a', 0.42)])
    fig.fx_back.append('<g clip-path="url(#%s)"><ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/></g>' % (
        clip, fm(cx), fm(cy), fm(rx), fm(ry), inner))
    # le bord : une couronne (anneau) de feu doré, plus épaisse en haut à droite
    outer = ellipse(cx, cy, rx, ry)
    inn = ellipse(cx + 1.6, cy - 1.0, rx - 2.6, ry - 2.6)
    band = Shape(outer.subs + inn.rev().subs)
    gb = g_lin(fig, (cx + rx * 0.7, cy - ry * 0.7), (cx - rx * 0.7, cy + ry * 0.7), [(0, '#ffffff'), (0.3, LAVA[1]), (0.7, LAVA[2]), (1, LAVA[3])])
    inn2 = ellipse(cx + 3.6, cy - 2.6, rx - 5.0, ry - 5.0)
    glow = Shape(outer.subs + inn2.rev().subs)
    fig.fx_front.append('<g clip-path="url(#%s)" opacity="%g"><path d="%s" fill="#ffe08a" opacity="0.28"/>'
                        '<path d="%s" fill="%s" opacity="0.9"/></g>' % (clip, op, glow.d(), band.d(), gb))
    # les langues de feu sur le bord (places irrégulières)
    for j, (a, hk) in enumerate(((-118, 0.8), (-74, 1.0), (-37, 0.7), (-160, 0.5), (12, 0.55))):
        ar = math.radians(a)
        bx, by = cx + rx * math.cos(ar), cy + ry * math.sin(ar)
        if by > GR - 2:
            continue
        h = (4.4 + 3.4 * hk) * (1 + 0.25 * math.sin(tl / 35 + j * 2.3)) * min(1, rx / 30)
        fig.fx_front.append(tongue(fig, (bx, by), h, 3.2, bend=0.7 if j % 2 else -0.6, lean=0.3 * math.cos(ar), op=op, gold=True))
    for j, (a, d) in enumerate(((-110, 6), (-50, 9), (-80, 12))):
        ar = math.radians(a)
        fig.fx_front.append(ember(fig, cx + (rx + d) * math.cos(ar), cy + (ry + d) * math.sin(ar) - 0.03 * tl % 6, 0.55, op=op * 0.8))


def ring(fig, k):
    """L'anneau de feu doré posé au sol tout autour de lui : il s'éloigne en s'abaissant ; à la fin il se défait en
    arcs (de longueurs inégales) et s'éteint en braises. La moitié lointaine passe derrière lui, la proche devant."""
    cx, cy = 66.0, GR
    e = 1 - (1 - k) ** 2
    rx = 34 + 58 * e
    ry = rx * 0.2
    h = 9 * (1 - k) ** 1.2 + 1
    op = env(k, 0, 0.05, 0.6, 1)
    # les arcs qui restent (il se défait en arcs) : (début, fin) en degrés ; 0 = à droite, 90 = devant
    if k < 0.5:
        arcs = [(0, 360)]
    else:
        g = (k - 0.5) / 0.5
        arcs = [(10 + 30 * g, 120 - 20 * g), (150 + 20 * g, 250 - 25 * g), (275 + 15 * g, 350 - 30 * g)]
    for a0, a1 in arcs:
        for lo_, hi_, layer in ((180, 360, fig.fx_back), (0, 180, fig.fx_front)):
            b0, b1 = max(a0, lo_), min(a1, hi_)
            if b1 - b0 < 4:
                continue
            wall = ring_band(cx, cy, rx, ry, h, b0, b1)
            gw = g_lin(fig, (cx, cy - h), (cx, cy), [(0, LAVA[1], 0.0), (0.6, LAVA[2], 0.35), (1, LAVA[1], 0.55)])
            line, pts = ring_line(cx, cy, rx, ry, b0, b1, 1.6 * (1 - 0.5 * k))
            gl = g_lin(fig, (cx + rx, cy - ry), (cx - rx, cy + ry), [(0, '#ffffff'), (0.4, LAVA[1]), (1, LAVA[2])])
            layer.append('<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (op, wall.d(), gw, line.d(), gl))
            # de petites langues de feu dorées le long de l'anneau, à des places irrégulières
            for j, a in enumerate((b0 + (b1 - b0) * t for t in (0.13, 0.41, 0.58, 0.86))):
                if (j + int(a)) % 3 == 0:
                    continue
                ar = math.radians(a)
                x, y = cx + rx * math.cos(ar), cy + ry * math.sin(ar)
                layer.append(tongue(fig, (x, y), (3.5 + 2 * math.sin(a)) * (1 - k), 2.2, bend=0.6, lean=0.1, op=op, gold=True))
    if k > 0.55:
        for j, a in enumerate((20, 75, 140, 200, 300, 330)):
            ar = math.radians(a)
            x, y = cx + rx * math.cos(ar), cy + ry * math.sin(ar)
            (fig.fx_front if math.sin(ar) > 0 else fig.fx_back).append(ember(fig, x, y - 3 - 8 * (k - 0.55), 0.6, op=env(k, 0.55, 0.65, 0.85, 1)))


def mark(fig, c, R, op):
    """La marque du défi (l'œil en amande des effets communs, inventée) : une amande rouge, une pupille fendue."""
    cx, cy = c
    alm = sm([(cx - R, cy), (cx - R * 0.4, cy - R * 0.5), (cx + R * 0.4, cy - R * 0.5), (cx + R, cy),
              (cx + R * 0.4, cy + R * 0.5), (cx - R * 0.4, cy + R * 0.5)], sharp=(0, 3), t=0.9)
    pupil = sm([(cx, cy - R * 0.42), (cx + R * 0.16, cy), (cx, cy + R * 0.42), (cx - R * 0.16, cy)], sharp=(0, 2), t=0.9)
    gr = g_rad(fig, (cx + R * 0.3, cy - R * 0.3), R * 1.2, [(0, '#ffb0a0'), (0.4, '#ff4a52'), (1, '#b81834')])
    fig.glow(cx, cy, R * 2.4, R * 1.8, '#ff3c46', 0.4 * op)
    fig.fx_front.append(outlined([(alm, gr, 1), (pupil, '#3a0818', 1, 'n'),
                                  (ellipse(cx + R * 0.35, cy - R * 0.2, R * 0.16, R * 0.1), '#ffffff', 0.9, 'n')], w=1.3, op=op))


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael)."""
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
    return im


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous le héros."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (63 + 0.4 * P['lean'] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 34 * k, fy - 2.6 * k, cx + 34 * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 0.4), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.0), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
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
        fx = [fx_attack(tl)]
    elif act == 'special':
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
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [0.7, a_s + 0.12, a_s + 0.25, a_s + 0.4, a_s + 0.48, a_s + 0.62, a_s + 0.8, a_s + 0.95,
                            s_s + 0.2, s_s + 0.42, s_s + 0.55, s_s + 0.75, s_s + 0.85, s_s + 1.0, s_s + 1.25, s_s + 1.45]
        # les images d'avant (traînées, impact figé) demandent l'histoire : on rend dans l'ordre
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
        out = os.environ.get('BEROLD_PLANCHE', os.path.join(TMP, 'planche.png'))
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
