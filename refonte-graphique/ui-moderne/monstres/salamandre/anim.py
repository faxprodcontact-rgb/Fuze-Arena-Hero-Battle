# La Salamandre vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# salamandre/build.py) — la respiration à l'affût, l'attaque de base (crachat de feu), l'attaque spéciale (souffle de
# feu) — dans le style lisse de l'interface (comme les héros vectoriels : heros/kael/anim.py, heros/tybalt/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/salamandre/anim.py               # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/salamandre/anim.py --planche [t…]  # une planche d'images clés
#
# Méthode : chaque image redessine salamandre.py dans une POSE. C'est une bête à quatre pattes : les QUATRE PIEDS restent
# collés au sol (cinématique inverse des pattes), c'est l'avant du corps qui bouge : le buste se dresse ou plonge
# autour des hanches (il se plie comme une colonne souple), la tête et la gueule (qui s'ouvre autour de la commissure),
# la crosse de la queue ; la crête de flammes vit sans arrêt et grandit quand elle se charge ; taches, crête, gorge et
# gueule s'allument quand le feu monte. Mêmes temps que le pixel art (attaque : elle se recule, gueule fermée, puis
# crache une boule de feu qui file jusqu'à l'ennemi, touche à 800 ms ; spéciale : elle se charge, crête dressée, puis
# souffle un long jet de feu, arrêt sur l'image quand il touche à 720 ms), reliées par des courbes douces, 24 images/s.
# Effets de feu des héros de feu vectoriels (Kael, Tybalt) : dégradés, un seul contour, aucun flou.
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
import salamandre as K  # noqa: E402
from atelier import lock, sm, ellipse, sides, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'salamandre')
TMP = os.environ.get('SALA_TMP', os.path.join('/tmp', 'salamandre-anim'))
FPS = 24
VIEW = (-16, -16, 262, 147.375)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
FINK = '#3a0c18'                     # le contour du feu
LAVA = K.LAVA
TARGET = (224.0, GR - 24.0)          # l'ennemi (comme le pixel art : 160 px devant ses pieds)


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


PAIRS = {'head': ('headx', 'heady')}
SCAL = ['lean', 'rise', 'tilt', 'gape', 'glow', 'q', 'qu', 'qw', 'charge', 'sway', 'inhale']
NUM = SCAL + [k for v in PAIRS.values() for k in v]
BASE = {'gape': 1.0}                 # la gueule entrouverte au repos


def flat(k):
    d = {n: BASE.get(n, 0.0) for n in NUM}
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
# 2) Le crachat de feu (pixel : ATTAQUE). Elle se recule, buste dressé, tête relevée, gueule FERMÉE (le feu monte : la
# gorge, les taches et la crête s'allument, la crosse se dresse) ; puis elle lance la tête en avant, gueule grande
# ouverte : une boule de feu éclôt devant ses dents et file jusqu'à l'ennemi (elle touche à 800 ms : éclat, braises,
# fumée). Un filet de fumée sort de sa gueule pendant qu'elle revient au repos.
HOLD = dict(lean=-3.0, rise=0.8, head=(-2.6, -1.8), tilt=-12, gape=-0.7, glow=1.6, charge=0.35, sway=0.25, qu=1.6, q=-0.6)
ATTACK = [
    (0, {}),
    (110, dict(lean=-0.8, head=(-0.6, -0.4), tilt=-2.5, gape=0.4, glow=0.4, charge=0.08, qu=0.4)),
    (240, dict(HOLD, lean=-2.4, head=(-2.0, -1.4), tilt=-9, glow=1.1, charge=0.25)),
    (440, dict(HOLD, lean=-3.2, head=(-2.9, -2.0), tilt=-13, glow=1.9, charge=0.4)),
    (500, dict(lean=2.6, head=(3.2, 1.0), tilt=6, gape=5.2, glow=2.0, charge=0.25, sway=-0.25, qu=-0.6, q=0.5)),
    (580, dict(lean=2.2, head=(2.8, 0.9), tilt=5, gape=4.6, glow=1.5, charge=0.15, sway=-0.15, qu=-0.3, q=0.4)),
    (800, dict(lean=1.0, head=(1.2, 0.4), tilt=2, gape=2.4, glow=0.6, q=0.2)),
    (1080, {}),
]
SPIT = 490                           # la boule de feu quitte la gueule
ATTACK_HIT = 800

# 3) Le souffle de feu (pixel : SPECIALE). Elle se charge : buste dressé, la crête grandit et blanchit, les taches et la
# gorge brûlent, des braises montent et sont aspirées vers sa gueule ; puis elle se jette en avant, gueule grande
# ouverte, et souffle un long jet de feu qui roule jusqu'à l'ennemi (arrêt sur l'image quand il touche, 720 ms) ;
# l'ennemi s'embrase ; le jet se détache de sa gueule et s'éteint en fumée ; elle revient au repos.
SPECIAL = [
    (0, {}),
    (110, dict(lean=-1.0, head=(-0.6, -0.6), tilt=-3, gape=0.3, glow=0.8, charge=0.3, qu=0.6)),
    (250, dict(lean=-2.6, rise=0.8, head=(-1.8, -1.8), tilt=-9, gape=-0.4, glow=2.0, charge=0.75, inhale=1.0, sway=0.15, qu=2.0, q=-0.6)),
    (450, dict(lean=-3.2, rise=1.1, head=(-2.6, -2.6), tilt=-13, gape=0.4, glow=3.0, charge=1.0, inhale=1.4, sway=0.25, qu=2.6, q=-0.8)),
    (630, dict(lean=-3.3, rise=1.1, head=(-2.8, -2.7), tilt=-14, gape=0.8, glow=3.0, charge=1.0, inhale=1.5, sway=0.25, qu=2.7, q=-0.8)),
    (700, dict(lean=3.0, rise=0.3, head=(3.4, 1.3), tilt=8, gape=6.6, glow=3.0, charge=0.8, sway=-0.3, qu=-0.6, q=0.6)),
    (1150, dict(lean=2.8, rise=0.2, head=(3.0, 1.2), tilt=7, gape=6.2, glow=2.6, charge=0.6, sway=-0.25, qu=-0.4, q=0.5)),
    (1380, dict(lean=1.4, head=(1.4, 0.6), tilt=3, gape=3.0, glow=1.2, charge=0.2, q=0.2)),
    (1940, {}),
]
SP_HIT = 720
SP_JET = (650, 1300)


# ======================================================================== la respiration (en boucle)
IDLE = 1.3                           # la durée d'un souffle (s), le rythme du pixel art (1,3 s)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, lean=-0.35 * br, heady=-0.35 * math.sin(u - 0.6), tilt=-0.9 * math.sin(u - 0.9),
                gape=0.25 * math.sin(u - 1.2), q=0.5 * math.sin(u - 0.4), qw=1.0 * math.sin(u - 1.5),
                qu=0.4 * math.sin(u - 2.0), sway=0.05 * math.sin(u + 0.8))


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
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ph'] = 2 * math.pi * T * 1.6
    P['blink'] = 1.0 if (w > 0.95 and 1.9 <= (T % 3.9) < 1.98) else 0.0
    return P, tl


# ======================================================================== les effets de feu (un seul contour, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour ; une 4e valeur = pas de silhouette (un reflet dedans)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0):
    """Une langue de feu posée : large et pâle à la base, fine et rouge au bout, en S."""
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


def comet(fig, c, r, v, seed=0, op=1.0):
    """La boule de feu crachée qui file : une traîne en langue de feu derrière elle (opposée à la marche v), puis la
    boule."""
    if r < 0.4 or op <= 0.02:
        return ''
    L = math.hypot(*v) or 1
    u = (v[0] / L, v[1] / L)
    nrm = (-u[1], u[0])
    tl_ = r * 4.6
    wob = 0.6 + 0.4 * math.sin(seed * 2.3)
    p0 = (c[0] + u[0] * r * 0.2, c[1] + u[1] * r * 0.2)
    p1 = (c[0] - u[0] * tl_ * 0.33 + nrm[0] * r * 0.6 * wob, c[1] - u[1] * tl_ * 0.33 + nrm[1] * r * 0.6 * wob)
    p2 = (c[0] - u[0] * tl_ * 0.66 - nrm[0] * r * 0.6 * wob, c[1] - u[1] * tl_ * 0.66 - nrm[1] * r * 0.6 * wob)
    p3 = (c[0] - u[0] * tl_ + nrm[0] * r * 0.3, c[1] - u[1] * tl_ + nrm[1] * r * 0.3 - r * 0.4)
    trail = lock(p0, p1, p2, p3, r * 1.9, n=12, bulge=0.15)
    gt = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.4, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])])
    out = outlined([(trail, gt, 1)], w=1.2, op=op)
    return out + fireball(fig, c, r, seed=seed, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


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
    """Un filet de fumée qui sort de la narine et monte en traînant vers l'arrière (k : 0 → 1)."""
    if k <= 0 or k >= 1:
        return
    x, y = ctx['nostril']
    o = op * env(k, 0, 0.15, 0.55, 1)
    fig.fx_front.append(smoke(fig, x + 0.6 - 3.0 * k, y - 1.5 - 9 * k, 0.7 + 1.5 * k, op=0.9 * o))
    if k > 0.3:
        k2 = (k - 0.3) / 0.7
        fig.fx_front.append(smoke(fig, x + 0.4 - 2.0 * k2, y - 1.0 - 5.5 * k2, 0.5 + 1.0 * k2, op=0.75 * o))


def burst(fig, X, Y, tg, size=1.0):
    """L'ennemi touché par le feu : un éclat, des langues de feu au sol, des braises qui retombent, de la fumée."""
    sc = env(tg, 0, 80, 300 * size, 700 * size)
    if sc > 0:
        for j, (dx, hh, ww, bd, ln) in enumerate(((0, 30, 10.0, 0.5, 0.05), (-9, 20, 7.0, -1.0, -0.4), (9, 22, 7.5, 1.0, 0.45),
                                                  (-17, 11, 4.6, -0.9, -0.8), (17, 12, 4.6, 0.9, 0.8))):
            if size < 1 and j >= 3:
                continue
            flick = 1 + 0.08 * math.sin(tg / 26.0 + j * 2.3)
            (fig.fx_front if j == 0 else fig.fx_back).append(
                tongue(fig, (X + dx * (0.7 + 0.3 * sc), GR), hh * size * sc * flick, ww * (0.6 + 0.4 * sc), bend=bd, lean=ln))
    if tg < 260:
        e = env(tg, 0, 30, 120, 260)
        fig.fx_front.append(fireball(fig, (X + 2, Y + 4), (7 + 4 * size) * e, seed=7, op=e))
    for j, (vx, vy) in enumerate(((-70, -140), (60, -160), (-110, -70), (110, -90), (-25, -190), (30, -180))):
        tau = (tg - 30 * (j % 3)) / 1000.0
        if 0 <= tau < 0.8:
            x, y = ballistic((X, Y + 4), (vx, vy), 300, tau)
            if y < GR - 0.5:
                fig.fx_front.append(ember(fig, x, y, 0.75 if j % 2 else 0.55, op=1 - tau / 0.8))
    smk = (tg - 180) / 1000.0
    if 0 < smk < 1.0:
        o = env(smk, 0, 0.15, 0.45, 1.0)
        for j, (dx, rr, sp) in enumerate(((-9, 4.2, 20), (2, 5.4, 28), (12, 4.0, 22))):
            fig.fx_back.append(smoke(fig, X + dx + 3 * smk, Y - 2 - sp * smk, rr * (0.7 + 0.6 * smk) * (0.8 + 0.2 * size), op=0.85 * o))


# ---- la respiration : un filet de fumée à la narine, un souffle sur deux

def fx_idle(T, w):
    def f(fig, ctx):
        if w < 0.5:
            return
        ph = (T / IDLE) % 1.0
        k = (ph - 0.4) / 0.6
        if 0 < k < 1 and int(T / IDLE) % 2 == 1:
            nostril_smoke(fig, ctx, k, 0.8)
    return f


# ---- l'attaque de base : le crachat de feu

def fx_attack(tl):
    def f(fig, ctx):
        M = ctx['mouth']
        g = ctx['P']['glow']
        if g > 0.3:
            h = ctx['throat']
            fig.under.append((h[0] + 2, h[1] - 4, 10 + 2 * g, 12 + 2 * g, '#ff7a1e', 0.06 * g, None))
        # la boule de feu éclôt devant les dents, puis file en ligne presque droite jusqu'à l'ennemi
        if SPIT - 40 <= tl < SPIT:
            k = (tl - (SPIT - 40)) / 40.0
            fig.fx_front.append(fireball(fig, (M[0] + 2.5 * k, M[1] + 0.4), 2.0 + 2.4 * k, seed=1, op=min(1, 2 * k)))
        if SPIT <= tl < ATTACK_HIT:
            k = (tl - SPIT) / (ATTACK_HIT - SPIT)
            if 'M0' not in HIT:
                HIT['M0'] = (M[0] + 2.5, M[1] + 0.4)
            P0 = HIT['M0']
            x = P0[0] + (TARGET[0] - P0[0]) * k
            y = P0[1] + (TARGET[1] - P0[1]) * k - 7.0 * math.sin(math.pi * k)
            vy = (TARGET[1] - P0[1]) - 7.0 * math.pi * math.cos(math.pi * k)
            fig.fx_front.append(comet(fig, (x, y), 4.4 + 0.6 * math.sin(tl / 40.0), (TARGET[0] - P0[0], vy), seed=int(tl / 40)))
            # des braises semées derrière elle
            for j in range(4):
                kk = k - 0.05 * (j + 1)
                if kk > 0:
                    xx = P0[0] + (TARGET[0] - P0[0]) * kk
                    yy = P0[1] + (TARGET[1] - P0[1]) * kk - 7.0 * math.sin(math.pi * kk) + 2.0 * math.sin(j * 2.1 + tl / 50.0) + 4 * j * (k - kk)
                    fig.fx_back.append(ember(fig, xx, yy, 0.6 - 0.1 * j, op=0.9 - 0.18 * j))
        # la fumée qui sort de la gueule après le crachat
        if 560 <= tl <= 1060:
            k = (tl - 560) / 500.0
            o = env(k, 0, 0.12, 0.5, 1)
            fig.fx_front.append(smoke(fig, M[0] + 1.5 - 3 * k, M[1] - 2 - 13 * k, 1.2 + 2.4 * k, op=0.8 * o))
        # l'ennemi touché
        if tl >= ATTACK_HIT:
            burst(fig, TARGET[0], TARGET[1], tl - ATTACK_HIT, 0.7)
    return f


HIT = {}


# ---- l'attaque spéciale : le souffle de feu

def jet(fig, M, T, d0, d1, ph, thick=1.0, op=1.0):
    """Le jet de feu : de la gueule M vers l'ennemi T, de la distance d0 à d1 ; un ruban qui ondule et s'évase (coeur
    blanc près de la gueule, bords rouges), bordé de boules de feu qui roulent, quelques langues courbes couchées vers
    l'arrière, une grosse boule de feu en tête."""
    vx, vy = T[0] - M[0], T[1] - M[1]
    L = math.hypot(vx, vy)
    u = (vx / L, vy / L)
    up = (u[1], -u[0])

    def at(d):
        amp = 0.3 + 2.2 * d / L
        s = amp * math.sin(d / 8.0 - ph)
        return (M[0] + d * u[0] + up[0] * s, M[1] + d * u[1] + up[1] * s)

    def wid(d):
        return thick * (3.6 + 17.0 * (d / L) ** 0.8)
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
    for k in range(14):
        d = (k * 12.5 + ph * 9.0) % (L + 10)
        if not (d0 + 6 < d < d1 - 4):
            continue
        side = 1 if k % 2 else -1
        size = 0.55 + 0.4 * ((k * 0.37) % 1)
        p = at(d)
        cpos = (p[0] + up[0] * side * wid(d) * 0.4, p[1] + up[1] * side * wid(d) * 0.4)
        fig.fx_front.append(fireball(fig, cpos, (0.9 + 0.2 * wid(d)) * size, seed=k, op=op, hot=0.6))
    for k, (fr, hk) in enumerate(((0.38, 0.9), (0.68, 1.25))):
        d = fr * L + (ph * 4.0) % 10.0
        if not (d0 + 8 < d < d1 - 8):
            continue
        p = at(d)
        b = (p[0] + up[0] * wid(d) * 0.35, p[1] + up[1] * wid(d) * 0.35)
        fig.fx_back.append(tongue(fig, b, (5 + 9 * d / L) * hk * thick, 3.6 + 3.0 * d / L, bend=-0.8, lean=-0.7, op=op))
    if d1 < L - 0.5 or d0 == 0:
        fig.fx_front.append(fireball(fig, at(d1), wid(d1) * 0.5 + 1.6, seed=int(ph * 3), op=op))


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        M = ctx['mouth']
        g = P['glow']
        if g > 0.3:
            h = ctx['throat']
            fig.under.append((h[0] - 6, h[1] - 6, 22 + 4 * g, 16 + 3 * g, '#ff7a1e', 0.06 * g, None))
        # la charge : des braises montent du dos et sont aspirées vers la gueule
        k = env(tl, 150, 260, 600, 690)
        if k > 0:
            for j in range(8):
                kk = ((tl - 150) / 460.0 + j / 8.0) % 1.0
                a = math.radians(j * 47 + 240 * kk)
                r = 22 * (1 - kk) + 2
                x, y = M[0] - 4 + r * math.cos(a), M[1] - 2 - r * math.sin(a) * 0.7
                fig.fx_front.append(ember(fig, x, y, 0.45 + 0.25 * (j % 3) / 2, op=k * min(1, kk * 4) * min(1, (1 - kk) * 6)))
        # la boule de feu qui éclôt devant la gueule
        b = env(tl, 640, 680, 730, 820)
        if b > 0:
            fig.fx_front.append(fireball(fig, (M[0] + 4 * b, M[1] + 0.5), 5.6 * b, seed=2, op=min(1, b * 1.5)))
        # le jet de feu
        T = TARGET
        L = math.dist(M, T)
        if SP_JET[0] + 20 <= tl < SP_JET[1]:
            reach = min(1.0, (tl - 670) / (SP_HIT - 670)) if tl < SP_HIT else 1.0
            start = 0.0 if tl < 1150 else min(1.0, (tl - 1150) / 150.0)
            thick = 1.0 if tl < 1080 else max(0.55, 1 - (tl - 1080) / 220.0)
            jet(fig, M, T, start * L, max(start * L + 1, reach * L), tl / 60.0, thick=thick,
                op=1.0 if tl < 1240 else 1 - (tl - 1240) / 60.0)
        # l'éclair de l'impact (arrêt sur l'image) : un éclat chaud qui part de l'ennemi
        fl = env(tl, SP_HIT - 10, SP_HIT, SP_HIT + 30, SP_HIT + 160)
        if fl > 0:
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(T[0]), fm(T[1]), fm(90), g_rad(
                fig, T, 90, [(0, '#fffbe4', 0.8 * fl), (0.15, '#ffe68a', 0.5 * fl), (0.5, '#ffb43a', 0.15 * fl), (1, '#ff7a1e', 0)])))
        if tl >= SP_HIT:
            burst(fig, T[0], T[1], tl - SP_HIT, 1.0 if tl < 1300 else 1.0)
        # la fumée qui sort de la gueule après le souffle, puis la narine
        if 1250 <= tl <= 1750:
            k = (tl - 1250) / 500.0
            o = env(k, 0, 0.12, 0.5, 1)
            fig.fx_front.append(smoke(fig, M[0] + 2 - 3 * k, M[1] - 2 - 14 * k, 1.6 + 2.6 * k, op=0.85 * o))
        if 1450 <= tl <= 1800:
            nostril_smoke(fig, ctx, (tl - 1450) / 350.0, 0.8)
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre."""
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


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre douce au sol sous la salamandre (des pieds arrière à la main avant)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    ImageDraw.Draw(sh).ellipse([(10 - x0) * k, fy - 2.6 * k, (112 - x0) * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 0.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.0), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
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
    if act == 'attack':
        if tl < SPIT:
            HIT.clear()
        fx = [fx_attack(tl)]
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
    subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu-lot.cjs'), jp], check=True)
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
        moments = extra or [0.5, 1.15, a_s + 0.25, a_s + 0.44, a_s + 0.5, a_s + 0.62, a_s + 0.8, a_s + 0.95,
                            s_s + 0.3, s_s + 0.6, s_s + 0.72, s_s + 0.9, s_s + 1.1, s_s + 1.25, s_s + 1.45, s_s + 1.7]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('SALA_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    bg.alpha_composite(shadow_layer(VW, VH, VIEW))
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
