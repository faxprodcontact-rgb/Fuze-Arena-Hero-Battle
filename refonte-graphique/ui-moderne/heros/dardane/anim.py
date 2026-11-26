# Dardane vectoriel ANIMÉ (refonte des héros du 26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/gabryel/build.py) — respiration (le dard qui menace), attaque de base « coup de
# dard » (la queue fouette par-dessus la tête et crache une goutte de venin), attaque spéciale « Dard des sables » (il
# s'enfonce dans le sable, la queue file sous le sol comme un aileron et jaillit sous l'ennemi) — dans le style lisse
# de l'interface, plus fluide (24 images par seconde).
#
#   python3 refonte-graphique/ui-moderne/heros/dardane/anim.py             # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/dardane/)
#   python3 refonte-graphique/ui-moderne/heros/dardane/anim.py --planche   # seulement une planche d'images clés (contrôle)
#
# Méthode (comme Kael) : chaque image redessine le héros (dardane.py) dans une POSE. Les poses clés sont celles du pixel
# art (mêmes temps : un scorpion, mouvements secs, images tenues puis départ brutal ; la queue part de la base et le
# bout suit avec du retard), reliées par des courbes douces sans dépassement. La queue est une ligne médiane pliée comme
# dans le pixel art (les anneaux glissent le long, jamais décrochés). Effets de terre et de venin dans le même style :
# dégradés, un seul contour, courbes ; aucun flou SVG.
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
import dardane as D  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = D.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'dardane')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-dardane/_images'
FPS = 24
VIEW = (-22, -20, 256, 144)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = D.GRD
FOE_X = 194.0                        # le pied de l'ennemi (comme le pixel art : 130 px devant lui)
VENOM_HIT = (190.0, 70.0)            # où la goutte de venin frappe l'ennemi
SINK = '#3a2230'                     # le contour du sable
VINK = '#173022'                     # le contour du venin
SANDC = ['#fff4d0', '#f0d49a', '#cfa66c', '#9c7052', '#6a4648']
VEN = D.VENOM

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


SG = [0, 0.15, 0.3, 0.45, 0.65, 0.8, 1.0]        # les points de la queue où l'on garde la pliure


def tb(a, b):
    """Pliure de la queue (comme le pixel art) : a = la queue entière (base → milieu), b = le bout (dard)."""
    return [(0, 0), (0.3, 0), (0.65, a), (1, a + b)]


ARM1 = [(0, 0), (0.15, 9), (0.45, 16), (0.8, 18), (1, 22)]
ARM2 = [(0, 0), (0.15, 20), (0.45, 35), (0.8, 40), (1, 50)]          # armé : la queue dressée en arrière
WHIP = [(0, 0), (0.15, -5), (0.45, 5), (0.8, 25), (1, 40)]           # le fouet passe par-dessus la tête
STRIKE = [(0, 0), (0.15, -26), (0.4, -30), (0.65, 10), (1, 20)]      # le dard frappe loin devant
FOLLOW = [(0, 0), (0.15, -32), (0.35, -34), (0.6, 0), (1, 8)]        # lancé, le bout continue vers le bas
RECOIL = [(0, 0), (0.15, -14), (0.4, -15), (0.7, -2), (1, 2)]
BOUNCE = [(0, 0), (0.3, 2), (0.65, 5), (1, 6)]


def bend_at(b, s):
    return D.interp([p[0] for p in b], [p[1] for p in b], s)


NUM = ['breath', 'crouch', 'lean', 'headx', 'heady', 'tilt', 'pan', 'pom', 'glow', 'sink'] + ['b%d' % i for i in range(len(SG))]
LEAN = 1.8                            # pixels de penché du pixel art → degrés autour des hanches


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key == 'bend':
            for i, s in enumerate(SG):
                d['b%d' % i] = bend_at(v, s)
        elif key == 'b':
            d['breath'] = v
        elif key == 'c':
            d['crouch'] = v * 1.1
        elif key == 'hy':
            d['heady'] = v * 0.8
        elif key == 'lean':
            d['lean'] = v * LEAN
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


def to_pose(d):
    P = dict(breath=max(0.0, d['breath']), crouch=d['crouch'], lean=d['lean'], head=(d['headx'], d['heady']),
             tilt=d['tilt'], pan=d['pan'], pom=d['pom'], glow=d['glow'], sink=max(0.0, d['sink']),
             bend=[(s, d['b%d' % i]) for i, s in enumerate(SG)])
    return P


# ======================================================================== les actions (poses clés du pixel art)
# 1) la pose : inspiration, expiration (il se tasse), la tête suit avec retard ; le dard se dresse lentement, tient,
# puis redescend d'un coup sec vers l'avant (une menace) et revient ; pans et pompon se balancent ; un clignement.
IDLE = [
    (0, dict(b=0, c=0, hy=0, bend=tb(0, 0), pan=0, pom=0)),
    (140, dict(b=1, c=0, hy=1, bend=tb(1, 1), pan=0, pom=0)),
    (270, dict(b=1, c=0, hy=0, bend=tb(2, 3), pan=1, pom=1)),
    (400, dict(b=1, c=0, hy=0, bend=tb(3, 5), pan=1, pom=1)),
    (600, dict(b=1, c=0, hy=0, bend=tb(3, 6), pan=1, pom=0)),
    (710, dict(b=0, c=0, hy=-1, bend=tb(0, -4), pan=0, pom=0)),
    (780, dict(b=0, c=1, hy=-1, bend=tb(-1, -6), pan=-1, pom=-1)),
    (930, dict(b=0, c=1, hy=0, bend=tb(-1, -4), pan=-1, pom=-1)),
    (1040, dict(b=0, c=1, hy=0, bend=tb(-1, -2), pan=0, pom=0)),
    (1180, dict(b=0, c=0, hy=1, bend=tb(0, -1), pan=0, pom=0)),
    (1310, dict(b=0, c=0, hy=0, bend=tb(0, 0), pan=0, pom=0)),
]
IDLE_MS = 1310
BLINK = (930, 1010)

# 2) l'attaque de base : il arme (la queue se dresse en arrière, le buste recule, les genoux plient), tient, la queue
# fouette par-dessus la tête, le dard frappe loin devant et crache une goutte de venin qui file sur l'ennemi.
ATTACK = [
    (0, dict(c=0, lean=0, bend=tb(0, 0))),
    (100, dict(c=1, lean=-1, bend=ARM1, pan=1, pom=1)),
    (190, dict(c=2, lean=-2, hy=1, bend=ARM2, pan=1, pom=1)),
    (400, dict(c=2.2, lean=-2.3, hy=1.2, bend=[(s, v * 1.06) for s, v in ARM2], pan=0.5, pom=0.5)),
    (450, dict(c=1, lean=1, bend=WHIP, pan=-1)),
    (490, dict(c=1, lean=3, bend=STRIKE, pan=-1.5, pom=-1)),
    (560, dict(c=1, lean=3, bend=FOLLOW, pan=-1, pom=-1.5)),
    (640, dict(c=1, lean=2, bend=RECOIL, pan=0, pom=-0.5)),
    (770, dict(c=1, lean=1, bend=BOUNCE, pan=0.5, pom=0.5)),
    (880, dict(c=0, lean=0, hy=-1, bend=tb(0, 1))),
    (1010, dict()),
]
ATTACK_MS = 1010
SPIT, HIT = 490, 630                  # la goutte part / frappe (ms)

# 3) l'attaque spéciale « Dard des sables » (temps du pixel art) : il arme la queue, le sable tourne autour de ses pieds
# et il s'enfonce d'un coup ; seule la queue dépasse, comme un aileron, et file sous le sable vers l'ennemi ; elle
# plonge ; le sol se bombe sous l'ennemi ; le dard jaillit du sable à la verticale et transperce (éclair, venin) ; la
# queue replonge ; Dardane ressort du sable chez lui, le sable coule de ses épaules, il se remet en garde.
SPECIAL = [
    (0, dict(c=0, bend=tb(0, 0))),
    (110, dict(c=2, lean=-1, hy=1, bend=ARM1, glow=1)),
    (200, dict(c=2, lean=-1, hy=1, bend=[(s, v * 1.3) for s, v in ARM1], glow=1)),
    (260, dict(c=2, lean=-1, bend=ARM2, sink=18, glow=1)),
    (340, dict(c=2, bend=ARM2, sink=52, glow=1)),
    (420, dict(c=2, bend=ARM2, sink=96, glow=1)),
    (1300, dict(c=2, bend=ARM1, sink=96, glow=1)),
    (1390, dict(c=2, bend=ARM1, sink=58, glow=1)),
    (1470, dict(c=2, bend=ARM1, sink=24, glow=0.5)),
    (1550, dict(c=2, lean=-1, hy=1, bend=BOUNCE, pan=1, pom=1)),
    (1660, dict(c=1, bend=tb(0, -2), pan=-0.5, pom=-0.5)),
    (1790, dict(c=0, hy=-1, bend=tb(0, 0))),
    (1930, dict()),
]
SPECIAL_MS = 1930
HIDE = (420, 1390)
FIN_K = [(420, 30, 0), (510, 66, 0), (580, 106, 0), (650, 146, 14), (720, 168, 46)]
RISE_K = [(860, 0.0), (890, 0.75), (950, 1.0), (1150, 1.0), (1220, 0.45), (1300, 0.0)]
ERUPT_PTS = [(FOE_X + 10, 172), (FOE_X + 8, 142), (FOE_X + 4, 116), (FOE_X - 2, 80), (FOE_X - 10, 46), (FOE_X - 22, 14)]


def fin_curve(X, depth):
    """L'aileron : la queue seule qui sort du sable en crochet, le dard en avant (X : où elle sort du sol)."""
    G = GR
    pts = [(X + 15, G - 26), (X + 9, G - 34), (X, G - 33), (X - 6, G - 24), (X - 10, G - 10), (X - 14, G + 10),
           (X - 18, G + 40), (X - 20, G + 80), (X - 21, G + 120)]
    C = D.by_step(D.catmull(pts), total=D.TAIL_L)[:D.NS][::-1]
    return [(x, y + depth) for x, y in C]


def erupt_curve(rise):
    C = D.tail_free(ERUPT_PTS)
    return [(x, y + (1 - rise) * 80.0) for x, y in C]


def idle_pose(tl):
    P = to_pose(keyed(IDLE, tl % IDLE_MS))
    P['blink'] = 1.0 if BLINK[0] <= tl % IDLE_MS < BLINK[1] else 0.0
    return P


def action_pose(action, tl):
    if action == 'attack':
        return to_pose(keyed(ATTACK, tl))
    P = to_pose(keyed(SPECIAL, tl))
    if HIDE[0] <= tl < HIDE[1]:
        P['hide'] = True
        P['clip'] = GR + 0.4
        P['sink'] = 0.0
        if tl < FIN_K[-1][0]:
            X = monotone([k[0] for k in FIN_K], [k[1] for k in FIN_K], tl)
            dp = monotone([k[0] for k in FIN_K], [k[2] for k in FIN_K], tl)
            P['tail'] = fin_curve(X, dp)
        elif RISE_K[0][0] <= tl < RISE_K[-1][0]:
            r = monotone([k[0] for k in RISE_K], [k[1] for k in RISE_K], tl)
            P['tail'] = erupt_curve(r)
            P['sting_flip'] = -1
        else:
            P['tail'] = None
            P['nothing'] = True
    return P


def pose_at(T, segs):
    """La pose au temps T (s) de la vidéo, l'action en cours et son temps local (ms)."""
    for a, s, e in segs:
        if s <= T < e:
            tl = (T - s) * 1000
            if a == 'idle':
                return idle_pose(tl), None, tl
            return action_pose(a, tl), a, tl
    a, s, e = segs[-1]
    return idle_pose((T - s) * 1000), None, 0


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=SINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
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


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def rnd(i):
    """Un hasard fixe (pour que chaque image redonne les mêmes grains)."""
    x = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


# ---- venin

def v_drop(fig, x, y, vx, vy, r=1.2, op=1.0):
    """Une goutte de venin : ronde devant, effilée derrière (dans le sens de sa course)."""
    a = math.atan2(vy, vx)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, VEN[1]), (0.5, VEN[2]), (1, VEN[3])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.3, y - r * 0.35, r * 0.38, r * 0.26), VEN[0], 0.95)], ink=VINK, w=1.0, op=op)


def v_blob(fig, c, r, lobes=7, seed=0, op=1.0, rot=0.0):
    """Une éclaboussure de venin : une tache aux lobes ronds et inégaux (jamais des rayons droits)."""
    pts = []
    n = lobes * 2
    for i in range(n):
        a = rot + 2 * math.pi * i / n
        rr = r * (1.0 + 0.25 * rnd(seed * 31 + i)) if i % 2 == 0 else r * (0.78 + 0.1 * rnd(seed * 17 + i))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a) * 0.9))
    sh = sm(pts, t=1.0)
    gr = g_rad(fig, (c[0] + r * 0.3, c[1] - r * 0.35), r * 1.6, [(0, VEN[0]), (0.35, VEN[1]), (0.75, VEN[2]), (1, VEN[3])])
    return outlined([(sh, gr, 1), (ellipse(c[0] + r * 0.25, c[1] - r * 0.3, r * 0.35, r * 0.22, -20), '#ffffff', 0.6)],
                    ink=VINK, w=1.2, op=op)


def v_splash(fig, c, tau, seed=0, size=1.0):
    """Le venin éclate sur l'ennemi : une tache qui s'ouvre puis se défait, des gouttes qui partent en cloche."""
    out_b, out_f = [], []
    e = env(tau, 0, 0.05, 0.14, 0.42)
    if e > 0:
        out_f.append(v_blob(fig, c, 7.5 * size * (0.55 + 0.45 * e), lobes=6, seed=seed, op=e, rot=0.3 * tau))
    for i, (vx, vy) in enumerate(((70, -90), (95, -30), (30, -120), (80, 25), (-40, -95), (110, -70), (-60, -40), (55, 60))):
        if tau < 0.6:
            x, y = ballistic(c, (vx * size, vy * size), 260, tau)
            if y < GR:
                (out_f if i % 2 else out_b).append(v_drop(fig, x, y, vx, vy + 260 * tau, 1.0 + 0.4 * (i % 3) / 2, op=max(0, 1 - tau / 0.6)))
    return out_b, out_f


# ---- sable

def puff(fig, cx, cy, r, op=1.0, seed=0):
    """Une bouffée de sable : quelques boules réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.8 * r, cy + 0.3 * r, 0.72 * r), (cx - 0.85 * r, cy + 0.32 * r, 0.68 * r),
             (cx + 0.2 * r, cy - 0.5 * r, 0.6 * r)]
    if seed % 2:
        balls.append((cx - 0.3 * r, cy + 0.55 * r, 0.6 * r))
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, SANDC[0]), (0.45, SANDC[1]), (1, SANDC[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def grain(fig, x, y, r=0.55, op=1.0, a=0.0):
    """Un grain de sable (un petit caillou clair, son ombre en bas à gauche)."""
    pts = [(x + r * math.cos(a + k * 2.1), y + r * 0.9 * math.sin(a + k * 2.1)) for k in range(3)]
    sh = sm(pts, t=0.8)
    return outlined([(sh, g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, SANDC[0]), (1, SANDC[2])]), 1)], w=0.7, op=op)


def mound(fig, cx, w, h, op=1.0):
    """Une bosse de sable posée au sol (le sable bombé), un seul contour."""
    if w < 1 or h < 0.3:
        return ''
    sh = sm([(cx - w, GR + 0.6), (cx - w * 0.55, GR - h * 0.55), (cx - w * 0.1, GR - h), (cx + w * 0.4, GR - h * 0.8),
             (cx + w * 0.8, GR - h * 0.3), (cx + w, GR + 0.6)], sharp=(0, 5), t=0.9)
    top = sm([(cx - w * 0.45, GR - h * 0.62), (cx - w * 0.05, GR - h * 0.98), (cx + w * 0.42, GR - h * 0.78),
              (cx + w * 0.62, GR - h * 0.5), (cx + w * 0.1, GR - h * 0.62)], t=0.9)
    gr = g_lin(fig, (cx + w * 0.4, GR - h), (cx - w * 0.6, GR), [(0, SANDC[1]), (0.5, SANDC[2]), (1, SANDC[3])])
    return outlined([(sh, gr, 1), (top, SANDC[0], 0.55)], w=1.3, op=op)


def swirl(fig, c, r0, a0, turn, w, cw=False, op=1.0, rise=0.0):
    """Une volute de sable (un ruban qui s'enroule en se rétrécissant), pointue aux deux bouts."""
    n = 18
    pts, ws = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (turn if not cw else -turn) * t)
        r = r0 * (1 - 0.55 * t)
        pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a) * 0.8 - rise * t))
        ws.append(w * math.sin(math.pi * min(1, 0.15 + t * 0.95)) ** 0.8 + 0.1)
    sh = ribbon(pts, ws)
    gr = g_lin(fig, pts[0], pts[-1], [(0, SANDC[1]), (1, SANDC[3])])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


def helix(fig, c, R, h, ph, w, op=1.0):
    """Un tourbillon de sable autour de lui : un ruban en spirale qui monte ; la moitié de devant passe devant lui."""
    back, front = [], []
    n = 40
    seg = []
    for i in range(n + 1):
        t = i / n
        a = 2 * math.pi * (ph + 1.25 * t)
        r = R * (1 - 0.25 * t)
        p = (c[0] + r * math.cos(a), c[1] - h * t + r * 0.28 * math.sin(a))
        seg.append((p, math.sin(a) > 0, t))
    # découpé en morceaux devant / derrière
    runs = []
    cur = [seg[0]]
    for s in seg[1:]:
        if s[1] == cur[-1][1]:
            cur.append(s)
        else:
            cur.append(s)
            runs.append(cur)
            cur = [s]
    runs.append(cur)
    for run in runs:
        if len(run) < 3:
            continue
        pts = [p for p, _, _ in run]
        ws = [w * math.sin(math.pi * min(1, max(0.0, t * 1.1))) ** 0.6 * (0.4 + 0.6 * math.sin(math.pi * k / (len(run) - 1)))
              + 0.15 for k, (_, _, t) in enumerate(run)]
        sh = ribbon(pts, ws)
        gr = g_lin(fig, (c[0] + R, c[1] - h), (c[0] - R, c[1]), [(0, SANDC[0]), (0.5, SANDC[1]), (1, SANDC[3])])
        (front if run[len(run) // 2][1] else back).append(outlined([(sh, gr, 1)], w=1.0, op=op))
    return back, front


def jet(fig, base, h, w, lean=0.0, bend=0.0, op=1.0):
    """Un jet de sable qui jaillit du sol : large à la base, fin au bout, en S (comme une langue de flamme, en sable)."""
    if h < 0.8:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.2)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock((bx + w * 0.15, by), q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.45, n=8, bulge=0.1)
    gout = g_lin(fig, (bx + w * 0.5, p3[1]), (bx - w * 0.5, by), [(0, SANDC[1]), (0.5, SANDC[2]), (1, SANDC[3])])
    return outlined([(sh, gout, 1), (core, SANDC[0], 0.6)], w=1.2, op=op)


def trail_ribbon(fig, pts, wmax, op=1.0):
    """La traînée du dard (un ruban courbe qui s'efface vers l'arrière), chitine claire et sable."""
    if len(pts) < 3 or math.dist(pts[0], pts[-1]) < 6:
        return ''
    n = len(pts)
    ws = [0.2 + wmax * (i / (n - 1)) ** 1.4 for i in range(n)]
    ws[-1] = wmax * 0.6
    sh = ribbon(pts, ws)
    g1 = g_lin(fig, pts[0], pts[-1], [(0, '#f6b070', 0), (0.55, '#e88a4a', 0.5 * op), (1, '#ffe2b8', 0.85 * op)])
    return '<path d="%s" fill="%s"/>' % (sh.d(), g1)


def flash(fig, c, r, e):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#fffff0', 0.9 * e), (0.15, '#f6ffc4', 0.6 * e), (0.5, '#c4f048', 0.15 * e), (1, '#7ac428', 0)]))


# ---- l'attaque de base

def tip_of(P):
    """Le bout de l'aiguillon pour une pose (sans dessiner)."""
    return D.build(pose=P).sting[0]


TIPS = {}


def fx_attack(tl, P_hist):
    def f(fig, ctx):
        tip, ang = ctx['sting']
        # la perle de venin au bout du dard pendant qu'il arme
        e = env(tl, 150, 230, 420, 460)
        if e > 0:
            a = math.radians(ang)
            fig.fx_front.append(v_drop(fig, tip[0] + math.cos(a) * 1.0, tip[1] + 1.4, 0, 1, 0.9 * e + 0.2))
        # la traînée du dard : ses dernières positions
        if 420 <= tl <= 600 and len(P_hist) > 2:
            fig.fx_back.append(trail_ribbon(fig, P_hist, 9.0, op=env(tl, 420, 450, 520, 600)))
        # la goutte qui file vers l'ennemi
        if SPIT <= tl < HIT:
            if 'spit' not in TIPS:
                TIPS['spit'] = tip
            p0 = TIPS['spit']
            u = 0.1 + 0.9 * (tl - SPIT) / (HIT - SPIT)
            mid = ((p0[0] + VENOM_HIT[0]) / 2, (p0[1] + VENOM_HIT[1]) / 2 - 12)

            def qb(t):
                return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mid[0] + t * t * VENOM_HIT[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * mid[1] + t * t * VENOM_HIT[1])
            x, y = qb(u)
            x2, y2 = qb(max(0, u - 0.05))
            fig.fx_front.append(v_drop(fig, x, y, x - x2, y - y2, 2.0))
            for j, du in enumerate((0.1, 0.17)):
                if u - du > 0.05:
                    xa, ya = qb(u - du)
                    fig.fx_front.append(v_drop(fig, xa, ya, x - x2, y - y2, 0.9 - 0.25 * j, op=0.8 - 0.25 * j))
            if tl < SPIT + 60:
                fig.fx_front.append(v_blob(fig, (p0[0] + 1, p0[1] + 1), 2.6 * (1 - (tl - SPIT) / 60), lobes=5, seed=3))
        if tl >= HIT:
            tau = (tl - HIT) / 1000.0
            fl = env(tau, 0, 0.02, 0.04, 0.12)
            if fl > 0:
                fig.fx_front.append(flash(fig, VENOM_HIT, 22, fl))
            b, fr = v_splash(fig, VENOM_HIT, tau, seed=1)
            fig.fx_back.extend(b)
            fig.fx_front.extend(fr)
    return f


# ---- l'attaque spéciale

def fx_special(tl):
    def f(fig, ctx):
        home = D.FEET[0]
        t = tl
        back, front = fig.fx_back, fig.fx_front
        # le sable frémit à ses pieds, puis tourne en tourbillon de plus en plus haut
        e0 = env(t, 0, 60, 180, 300)
        if e0 > 0:
            front.append(puff(fig, home - 17, GR - 1.5 - 1.5 * e0, 2.6 * e0, op=e0, seed=1))
            front.append(puff(fig, home + 19, GR - 1.5 - 1.2 * e0, 2.2 * e0, op=e0, seed=2))
            for i in range(8):
                front.append(grain(fig, home - 18 + 36 * rnd(i), GR - 1 - 6 * rnd(i + 9) - 0.02 * t * rnd(i + 3), 0.6, op=e0, a=i))
        ev = env(t, 110, 200, 400, 520)
        if ev > 0:
            k = min(1.0, (t - 110) / 310.0)
            R, h = 22 + 12 * k, 20 + 46 * k
            for j in range(2 + int(k * 1.6)):
                b, fr = helix(fig, (home, GR - 1), R * (1 - 0.15 * j), h * (1 - 0.18 * j), t / 420.0 + j * 0.37,
                              (3.4 - 0.6 * j) * ev, op=1.0 if ev > 0.12 else ev / 0.12)
                back.extend(b)
                front.extend(fr)
            for i in range(10):
                a = t / 160.0 + i * 0.63
                y = GR - 4 - h * ((i * 0.37 + t / 600.0) % 1)
                front.append(grain(fig, home + R * 0.9 * math.cos(a), y + 2 * math.sin(a), 0.6, op=ev * 0.9, a=i + t / 90.0))
        # la bosse de sable qui l'avale, chez lui
        em = env(t, 200, 330, 470, 560)
        if em > 0:
            front.append(mound(fig, home, 22 + 10 * em, 4 + 6 * em, op=1))
        # il disparaît : le sable retombe (bouffées, grains)
        ed = env(t, 400, 440, 520, 640)
        if ed > 0:
            k = (t - 400) / 240.0
            front.append(puff(fig, home - 12 - 4 * k, GR - 4 - 3 * k, 4 + 3 * k, op=ed, seed=1))
            front.append(puff(fig, home + 14 + 4 * k, GR - 3 - 2 * k, 3.6 + 2.6 * k, op=ed, seed=2))
            for i in range(14):
                x, y = ballistic((home - 18 + 36 * rnd(i + 40), GR - 20 - 20 * rnd(i + 41)), (20 * (rnd(i + 42) - 0.5), -20), 200, k * 0.4)
                if y < GR:
                    front.append(grain(fig, x, y, 0.55, op=ed, a=i))
        # l'aileron file sous le sable : une bosse qui le porte, une vague enroulée devant, un sillon derrière
        if 420 <= t < 760:
            X = monotone([k_[0] for k_ in FIN_K], [k_[1] for k_ in FIN_K], t)
            er = env(t, 420, 450, 650, 760)
            cx = X + 1
            front.append(mound(fig, cx, 15, 7 * er, op=1))
            # le sillon : de petites bosses qui retombent derrière
            for i in range(6):
                xi = cx - 18 - 13 * i
                if xi > home + 8:
                    hh = 3.2 * (1 - i / 6) * er
                    back.append(mound(fig, xi, 5.0, hh, op=1))
            if t > 480:
                front.append(puff(fig, cx + 15 + 2 * math.sin(t / 50.0), GR - 3, 3.4 * er, op=er, seed=int(t / 70)))
            for i in range(6):
                k = ((t / 300.0) + i * 0.17) % 1
                front.append(grain(fig, cx + 10 + 10 * k + 3 * rnd(i), GR - 7 - 9 * math.sin(math.pi * k), 0.55, op=er * (1 - k), a=i))
        # le sol se bombe sous l'ennemi (tenue), puis le dard jaillit
        eb = env(t, 690, 760, 900, 1300)
        if eb > 0:
            front.append(mound(fig, FOE_X, 19 - 6 * max(0, (t - 900) / 400.0), 9 * eb, op=1))
            if t < 920:
                front.append(puff(fig, FOE_X - 20, GR - 2, 2.8 * eb, op=eb, seed=1))
                front.append(puff(fig, FOE_X + 21, GR - 2, 2.6 * eb, op=eb, seed=2))
                for i in range(8):
                    front.append(grain(fig, FOE_X - 14 + 28 * rnd(i + 70), GR - 9 - 6 * rnd(i + 71) - 2 * math.sin(t / 40.0 + i), 0.6, op=eb, a=i))
        # la gerbe de sable autour du dard
        if 880 <= t < 1450:
            tg = (t - 880) / 1000.0
            sc = env(t, 880, 950, 1150, 1400)
            # la gerbe : des bouffées de sable qui montent en s'ouvrant de part et d'autre de la queue
            for j, (dx, vy, rr, dl) in enumerate(((-7, 70, 4.6, 0), (8, 62, 4.2, 30), (-13, 44, 3.6, 60), (14, 50, 3.8, 20),
                                                  (-3, 84, 3.4, 90), (4, 76, 3.0, 120))):
                k = (t - 880 - dl) / 420.0
                if 0 <= k < 1:
                    y = GR - 4 - vy * (1 - (1 - k) ** 2) * 0.6
                    back.append(puff(fig, FOE_X + dx * (1 + 1.2 * k), y, rr * (0.6 + 0.8 * k), op=1 - k ** 3, seed=j))
            if sc > 0.05:
                for j, (dx, dy, rr) in enumerate(((-12, -3, 4.2), (11, -3, 4.0), (-2, -2, 3.4), (-20, -1.5, 3.0), (20, -1.5, 3.2))):
                    front.append(puff(fig, FOE_X + dx * (0.8 + 0.2 * sc), GR + dy - 1.5 * sc, rr * (0.6 + 0.4 * sc), op=1, seed=j))
            for j, (vx, vy) in enumerate(((-60, -150), (55, -165), (-100, -90), (105, -100), (-20, -200), (25, -190),
                                          (-130, -40), (140, -50), (-75, -120), (85, -135))):
                tau = tg - 0.02 * (j % 3)
                if 0 <= tau < 0.75:
                    x, y = ballistic((FOE_X, GR - 6), (vx, vy), 300, tau)
                    if y < GR:
                        front.append(grain(fig, x, y, 0.75 if j % 2 else 1.0, op=1, a=j + tau * 9))
            sm_k = (t - 1000) / 1000.0
            if 0 < sm_k < 0.8:
                o = env(sm_k, 0, 0.1, 0.4, 0.8)
                for j, (dx, rr, sp) in enumerate(((-14, 4.5, 20), (2, 6.0, 26), (16, 4.6, 22), (-26, 3.4, 12), (27, 3.4, 13))):
                    back.append(puff(fig, FOE_X + dx + 4 * sm_k * (1 if dx > 0 else -1), GR - 5 - sp * sm_k, rr * (0.7 + 0.6 * sm_k), op=0.9 * o, seed=j))
        # l'éclair blanc-vert quand le dard transperce, puis le venin qui gicle derrière le dard
        fl = env(t, 885, 905, 930, 1010)
        if fl > 0:
            front.append(flash(fig, (FOE_X - 14, 30), 46, fl))
        if t < 900:
            TIPS.pop('sp', None)
        if 950 <= t < 1500:
            if 'sp' not in TIPS:
                TIPS['sp'] = ctx['sting'][0] if ctx.get('tail') else (FOE_X - 20, 30)
            tip = TIPS['sp']
            b, fr = v_splash(fig, (tip[0] + 2, tip[1] + 5), (t - 950) / 1000.0, seed=4, size=1.1)
            back.extend(b)
            back.extend(fr)
        # il ressort : la bosse chez lui, le sable coule de lui et retombe
        if 1300 <= t < 1900:
            er = env(t, 1300, 1390, 1500, 1640)
            if er > 0:
                front.append(mound(fig, home, 30 - 6 * max(0, (t - 1390) / 250.0), 10 * er, op=1))
                if t > 1380:
                    front.append(puff(fig, home - 30, GR - 3, 4.4 * er, op=er, seed=1))
                    front.append(puff(fig, home + 31, GR - 3, 4.0 * er, op=er, seed=2))
            eg = env(t, 1390, 1450, 1650, 1850)
            if eg > 0:
                k = (t - 1390) / 460.0
                for i in range(18):
                    x0 = home - 16 + 32 * rnd(i + 100)
                    y0 = 50 + 30 * rnd(i + 101)
                    x, y = ballistic((x0, y0), (14 * (rnd(i + 102) - 0.5), 10), 160, max(0.0, k - 0.3 * rnd(i + 103)) * 0.9)
                    if y < GR:
                        front.append(grain(fig, x, y, 0.55 if i % 3 else 0.75, op=eg, a=i + 3 * k))
            ec = env(t, 1540, 1620, 1720, 1900)
            if ec > 0:
                front.append(puff(fig, home - 30, GR - 3, 4.2, op=ec, seed=3))
                front.append(puff(fig, home + 32, GR - 3, 3.8, op=ec, seed=4))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous lui."""
    x0, y0, vw, vh = view
    k = w / vw
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    fy = int((floor_y + 0.5 - y0) * k)
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


def shadow_layer(w, h, view, sc=1.0):
    """L'ombre au sol sous ses pieds (elle s'efface quand il s'enfonce)."""
    x0, y0, vw, vh = view
    k = w / vw
    sh = Image.new('RGBA', (w, h))
    if sc <= 0.02:
        return sh
    sd = ImageDraw.Draw(sh)
    fy = (GR + 0.5 - y0) * k
    cx = (63 - x0) * k
    sd.ellipse([cx - 32 * k * sc, fy - 2.6 * k, cx + 32 * k * sc, fy + 2.6 * k], fill=(10, 4, 24, int(150 * sc)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : repos ×2, attaque, repos, attaque, repos, spéciale, repos (en secondes)."""
    I = IDLE_MS / 1000
    seq = [('idle', 2 * I), ('attack', ATTACK_MS / 1000), ('idle', I), ('attack', ATTACK_MS / 1000), ('idle', I),
           ('special', SPECIAL_MS / 1000), ('idle', 2 * I)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_svg(T, segs, view=VIEW, ow=0.95):
    P, act, tl = pose_at(T, segs)
    fx = []
    if act == 'attack':
        hist = []
        if 420 <= tl <= 600:
            for j in range(8, -1, -1):
                tj = tl - j * 9
                if tj >= 380:
                    hist.append(tip_of(action_pose('attack', tj)))
        if tl < SPIT:
            TIPS.pop('spit', None)
        fx = [fx_attack(tl, hist)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return D.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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


def compose(pngs, poses, w, h, view):
    bg = background(w, h, view)
    out = []
    for p, P in zip(pngs, poses):
        im = bg.copy()
        sc = 0.0 if P.get('hide') else max(0.0, 1 - P.get('sink', 0) / 40.0)
        im.alpha_composite(shadow_layer(w, h, view, sc))
        im.alpha_composite(Image.open(p))
        out.append(im)
    return out


def find_offset(sprite, frame):
    """Où le pixel art est posé dans une image de GIF (à l'échelle 1)."""
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
    """Les images d'une animation pixel art (GIF de contrôle, fond clair retiré), à l'échelle 1, leurs durées, et où
    tombe l'origine du dessin (pieds en (64, 116))."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-gabryel-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    if name == 'pose':
        return out, (0, 0)
    g0 = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-gabryel-pose.gif'))
    g0.seek(0)
    sprite = g0.convert('RGBA').resize((128, 120), Image.NEAREST).crop((30, 30, 100, 116))
    g.seek(0)
    ref = g.convert('RGBA').resize((g.width // 4, g.height // 4), Image.NEAREST)
    ox, oy = find_offset(sprite, ref)
    return out, (ox - 30, oy - 30)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur un vrai fond de combat de la terre (le repaire d'Arachné), le pixel art à
    gauche et le vectoriel à droite, à la même échelle : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (110, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    I = IDLE_MS / 1000
    seq = [('idle', I), ('attack', ATTACK_MS / 1000), ('idle', I), ('special', SPECIAL_MS / 1000), ('idle', I)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (64 - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    TIPS.clear()
    res = [frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)]
    pngs = render([r[0] for r in res], PW, PH, 'b')
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
        layer = Image.new('RGBA', left.size)
        layer.paste(big, (round(feet[0] - (ox + 64) * SC), round(feet[1] - (oy + 116) * SC)), big)
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
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        moments = [0.45, a_s + 0.3, a_s + 0.44, a_s + 0.47, a_s + 0.52, a_s + 0.6, a_s + 0.7,
                   s_s + 0.15, s_s + 0.3, s_s + 0.38, s_s + 0.5, s_s + 0.62, s_s + 0.8, s_s + 0.93, s_s + 1.0, s_s + 1.2,
                   s_s + 1.25, s_s + 1.42, s_s + 1.5, s_s + 1.6]
        if len(sys.argv) > 2 and sys.argv[2] != '--planche':
            moments = [float(x) for x in sys.argv[2].split(',')]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        ims = compose(pngs, [r[1] for r in res], 640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, im in enumerate(ims):
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        path = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(path)
        print('planche :', path)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    TIPS.clear()
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r[0] for r in res], VW, VH, 'a')
    ims = compose(pngs, [r[1] for r in res], VW, VH, VIEW)
    for p, im in zip(pngs, ims):
        im.convert('RGB').save(p)
    # le GIF : la partie 1 seule (repos ×2, attaque ×2, spéciale), ≈ 400 px de large
    for i, p in enumerate(pngs):
        os.replace(p, os.path.join(TMP, 'g%04d.png' % i))
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'g%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    names2, n2 = game_size_part()
    allf = [os.path.join(TMP, 'g%04d.png' % i) for i in range(n)] + names2
    for i, p in enumerate(allf):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024),
          '— partie 1 : %.1f s, partie 2 : %.1f s' % (total, n2 / FPS))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
