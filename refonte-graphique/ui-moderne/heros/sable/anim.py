# Sable vectorielle ANIMÉE (refonte du 26/11/2026, d'après l'essai validé de Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/sable/build.py) — respiration, attaque de base
# « khopesh lancé », attaque spéciale « Rugissement de la lionne » — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/sable/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/sable/)
#   python3 refonte-graphique/ui-moderne/heros/sable/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode (comme Kael) : le dessin (sable.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui
# respire, se ramasse ou se dresse et se penche depuis les hanches, tête, oreille qui frémit, queue qui ondule et
# fouette, tablier ; le bras lointain d'un seul tenant est placé par cinématique inverse depuis le poignet, le poing
# tourne avec le khopesh). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps : appuis courts,
# détentes sèches — c'est une lionne) et sont reliées par des courbes douces sans dépassement (24 images par seconde).
# Les effets (traînées d'or en croissant, feu solaire, crinière de flammes, lionne de feu, braises, fumée) sont
# dessinés dans le même style : dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits répétés.
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
import sable as S  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, mapp, f as fm  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sable')
TMP = os.path.join(HERE, '_images')
FIRE = S.FIRE
FPS = 24
VIEW = (-22, -25, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes
GR = S.GRD
ENEMY_X = 212.0                      # où se tient l'ennemi (un peu plus près que le pixel art, pour que la gerbe tienne dans l'image)

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


NUM = ['crouch', 'lean', 'tilt', 'ear', 'q', 'qu', 'roar', 'hot', 'pg', 'bend', 'ang', 'wx', 'wy', 'headx', 'heady']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, ear=0, q=0, qu=0, roar=0, hot=0, pg=0, bend=1, ang=S.KH_ANG0,
             wx=S.WR0[0], wy=S.WR0[1], headx=0, heady=0)
    for key, v in k.items():
        if key == 'wrist':
            d['wx'], d['wy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « khopesh lancé » (pixel : ATTAQUE, 1130 ms). Elle arme : le bras monte derrière la tête, la
# lame se dresse au-dessus de la coiffe, elle se ramasse sur son genou, oreille couchée, la queue se dresse (tenue).
# Détente sèche : elle lance le khopesh qui file en tournoyant vers l'ennemi (traînée d'or) et sort du cadre ; main
# tendue, elle attend ; il revient comme un boomerang, elle le rattrape au vol (éclat d'or), amortit et revient en garde.
ARMED = dict(wrist=(89.5, 41.5), ang=121)
ATTACK = [
    (0, {}),
    (90, dict(crouch=1, lean=-1, wrist=(93.0, 54.0), ang=100, head=(0, 1), q=1, qu=1, ear=1)),
    (210, dict(ARMED, crouch=2, lean=-2, head=(-1, 1), tilt=-2, q=2, qu=2, ear=1)),
    (290, dict(ARMED, crouch=2.2, lean=-2.3, head=(-1.2, 1.2), tilt=-2.5, q=2, qu=2.2, ear=1, pg=1)),
    (335, dict(crouch=0, lean=2, wrist=(106.0, 57.0), ang=30, head=(1, 0), tilt=2, q=-1, qu=1, pg=-1)),
    (420, dict(crouch=0, lean=2, wrist=(107.0, 60.0), ang=30, head=(1, 0), tilt=1.5, q=-2, qu=0.6, pg=-1)),
    (560, dict(crouch=0, lean=1, wrist=(105.5, 60.5), ang=30, head=(0, 0), q=-1, qu=0.3)),
    (650, dict(crouch=0, lean=1, wrist=(106.5, 59.6), ang=40, head=(0, 0), q=1)),
    (700, dict(crouch=0, lean=1, wrist=(105.0, 59.5), ang=56, q=1)),
    (790, dict(crouch=1, lean=-1, wrist=(100.5, 61.5), ang=70, head=(0, 1), q=1)),
    (910, dict(crouch=1, lean=0, wrist=(97.5, 62.5), ang=76)),
    (1130, {}),
]
THROW_T, CATCH_T = 320, 700
# la course du khopesh en vol (le centre de sa rotation, repère du dessin) et son angle
FLY = [(320, None), (360, (138, 37)), (410, (180, 35)), (470, (224, 35)), (525, (250, 38)), (585, (232, 42)),
       (640, (184, 44)), (700, None)]

# 3) L'attaque spéciale « Rugissement de la lionne » (pixel : SPECIALE, 1550 ms). Elle se ramasse et arme le khopesh
# derrière sa tête : la lame s'embrase, la chaleur monte. Elle se dresse et RUGIT : une crinière de flammes jaillit
# autour de sa tête, l'air brûlant sort de sa gueule en croissants (arrêt sur l'image). Elle abat le khopesh (arc de
# feu) : la crinière se détache et devient une tête de lionne de feu qui bondit vers l'ennemi. Gerbe de feu, langues
# qui montent, braises qui retombent, fumée qui s'enroule ; Sable revient en garde.
STRIKE = dict(wrist=(107.5, 58.5), ang=26)
SPECIAL = [
    (0, {}),
    (100, dict(crouch=1, lean=-1, wrist=(93.0, 54.0), ang=100, hot=1, head=(0, 1), q=1, qu=1, ear=1)),
    (250, dict(ARMED, crouch=2, lean=-2, hot=2, head=(-1, 1), tilt=-2, q=2, qu=2, ear=1)),
    (330, dict(ARMED, crouch=2.2, lean=-2.2, hot=2, head=(-1.2, 1.2), tilt=-2.5, q=2, qu=2.2, ear=1, pg=1)),
    (395, dict(ARMED, crouch=-2, lean=1, hot=2, head=(1, -2), tilt=-6, q=-1, qu=3, roar=1, pg=-1)),
    (600, dict(ARMED, crouch=-2.2, lean=1.2, hot=2, head=(1, -2.2), tilt=-6.5, q=-2, qu=3, roar=1, pg=-1)),
    (655, dict(STRIKE, crouch=0, lean=3, hot=2, head=(1, 0), tilt=3, q=-2, qu=1, roar=0.4, pg=-2)),
    (720, dict(crouch=0, lean=3, wrist=(108.0, 60.0), ang=22, hot=1.2, head=(1, 0), tilt=2, q=-1, roar=0.2, pg=-1)),
    (830, dict(crouch=0, lean=2, wrist=(107.5, 60.5), ang=24, hot=1, head=(0, 0), q=1)),
    (1000, dict(crouch=0, lean=2, wrist=(106.5, 61.0), ang=30, hot=0.4, q=1)),
    (1100, dict(crouch=1, lean=1, wrist=(103.0, 61.5), ang=52, head=(0, 1))),
    (1200, dict(crouch=1, lean=0, wrist=(99.0, 62.5), ang=70)),
    (1300, dict(crouch=1, q=-1)),
    (1550, {}),
]
SP_ROAR, SP_STRIKE, SP_HIT = 380, 640, 830
LION = [(640, (128, 36)), (720, (164, 40)), (780, (192, 44)), (830, (210, 50))]

# ======================================================================== la respiration (en boucle, 2 s)


def idle_offsets(T):
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    ear = 1.0 if 0.55 <= (T % 4.0) < 0.75 else 0.0
    return dict(breath=br, crouch=0.35 * (0.5 - 0.5 * math.cos(u - 1.4)), heady=0.35 * math.sin(u - 0.6),
                tilt=0.8 * math.sin(u - 0.9), pg=0.7 * math.sin(u + 0.5), q=0.6 * math.sin(u - 0.4), ear=ear)


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
    # l'oreille qui frémit : on garde la plus couchée
    P['ear'] = max(src['ear'], w * idl['ear'])
    P['breath'] = w * idl['breath']
    P['wrist'] = (P.pop('wx'), P.pop('wy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ph'] = 2 * math.pi * T * 0.5 + (2.5 * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % 4.0) < 1.38) else 0.0
    P['kh'] = 1
    if action == 'attack' and THROW_T <= tl < CATCH_T:
        P['kh'] = 0
        P['fly'] = fly_at(tl)
    return P, tl


def kh_spin_center(wrist, ang):
    u, n = S.kh_axes(ang)
    wl = S.WRL
    G = (wrist[0] - wl[0] * u[0] - wl[1] * n[0], wrist[1] - wl[0] * u[1] - wl[1] * n[1])
    return (G[0] + S.KH_SPIN[0] * u[0] + S.KH_SPIN[1] * n[0], G[1] + S.KH_SPIN[0] * u[1] + S.KH_SPIN[1] * n[1])


def fly_at(tl):
    """Le khopesh en vol à l'instant tl (ms) : (centre, angle), repère du dessin (avant la pose du corps). Il part de la
    main et y revient (positions de la main aux instants du lancer et de la prise) ; il tourne dans le sens des
    aiguilles d'une montre (le haut file vers l'ennemi)."""
    a0 = keyed(ATTACK, THROW_T)
    a1 = keyed(ATTACK, CATCH_T)
    c0 = kh_spin_center((a0['wx'], a0['wy']), a0['ang'])
    c1 = kh_spin_center((a1['wx'], a1['wy']), a1['ang'])
    pts = [(t, p if p else (c0 if t == THROW_T else c1)) for t, p in FLY]
    ts = [t for t, _ in pts]
    x = monotone(ts, [p[0] for _, p in pts], tl)
    y = monotone(ts, [p[1] for _, p in pts], tl)
    ang = a0['ang'] + (a1['ang'] - 720 - a0['ang']) * (tl - THROW_T) / (CATCH_T - THROW_T)
    return (x, y), ang


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w)) for sh, _, _ in shapes_fills if w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def flame(fig, p0, p1, p2, p3, w, op=1.0, ink=True, hot=False):
    """Une langue de feu le long d'une courbe : large et pâle à la racine, fine et rouge au bout."""
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.25)
    q = lambda p, k: (p0[0] + (p[0] - p0[0]) * k, p0[1] + (p[1] - p0[1]) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.6), w * 0.5, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, FIRE[1]), (0.35, FIRE[2]), (0.72, FIRE[3]), (1, FIRE[4])])
    gin = g_lin(fig, p0, q(p3, 0.6), [(0, FIRE[0]), (0.6, FIRE[1]), (1, FIRE[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3 if ink else 0, op=op)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, direction=-90.0):
    """Une langue de feu qui monte d'un point (direction en degrés, écran : −90 = vers le haut), en S."""
    if h < 0.6:
        return ''
    a = math.radians(direction)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    bx, by = base
    P_ = lambda along, side: (bx + ux * along + px * side, by + uy * along + py * side)
    return flame(fig, P_(0, 0), P_(h * 0.33, bend * w * 0.5 + lean * h * 0.12), P_(h * 0.68, -bend * w * 0.45 + lean * h * 0.55),
                 P_(h, lean * h), w, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, FIRE[2], 0.6 * op), (1, FIRE[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, FIRE[0], op), (0.6, FIRE[1], op), (1, FIRE[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def spark(fig, x, y, r=0.8, op=1.0):
    """Une étincelle d'or (prise du khopesh) : un petit losange courbe, blanc chaud."""
    if op <= 0.02:
        return ''
    sh = sm([(x, y - r * 2.2), (x + r * 0.6, y - r * 0.6), (x + r * 2.2, y), (x + r * 0.6, y + r * 0.6), (x, y + r * 2.2),
             (x - r * 0.6, y + r * 0.6), (x - r * 2.2, y), (x - r * 0.6, y - r * 0.6)], sharp=(0, 2, 4, 6), t=0.6)
    gl = g_rad(fig, (x, y), r * 4, [(0, '#fffbe0', 0.7 * op), (1, '#ffd86a', 0)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><path d="%s" fill="#fffbe8" opacity="%g"/>' % (fm(x), fm(y), fm(r * 4), gl, sh.d(), op)


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
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (écran, y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def trail(fig, C, R, a0, a1, w, hot=False, op=1.0):
    """Une traînée en croissant qui s'efface vers l'arrière (d'or, ou de feu)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.6, a0, a1, w * 0.36)
    if hot:
        g1 = g_lin(fig, pa, pb, [(0, FIRE[3], 0), (0.5, FIRE[2], 0.7 * op), (1, FIRE[1], 0.95 * op)])
        g2 = g_lin(fig, pa, pb, [(0, FIRE[4], 0), (0.6, FIRE[3], 0.9 * op), (1, FIRE[0], op)])
    else:
        g1 = g_lin(fig, pa, pb, [(0, '#ffd86a', 0), (1, '#ffe9a0', 0.65 * op)])
        g2 = g_lin(fig, pa, pb, [(0, '#e6a22c', 0), (0.6, '#ffd86a', 0.85 * op), (1, '#fffbe0', op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


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


def dust(fig, x, k, op=1.0):
    """Une petite bouffée de sable soulevée au sol (le genou qui pousse) : deux boules qui s'étalent et pâlissent."""
    if k <= 0 or k >= 1:
        return ''
    o = op * (1 - k)
    out = ''
    for dx, r in ((-4, 1.6), (2, 2.0), (6, 1.3)):
        cx, cy, rr = x + dx * (1 + k), GR - 1.2 - 2.5 * k, r * (0.8 + 1.2 * k)
        gr = g_lin(fig, (cx + rr, cy - rr), (cx - rr, cy + rr), [(0, '#f6e8c4'), (0.5, '#d8bc8c'), (1, '#a6846a')])
        out += '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%g"/>' % (fm(cx), fm(cy), fm(rr), gr, o * 0.9)
    return out


# ---- l'attaque de base : la détente, le khopesh qui tournoie, la prise


def fx_attack(tl, P, Pp):
    def f(fig, ctx):
        # la détente : une grande traînée d'or en croissant, de la lame armée (au-dessus de la tête) jusqu'à la main
        e = env(tl, 290, 320, 345, 420)
        if e > 0:
            W = ctx['wrist']
            fig.fx_back.append(trail(fig, (W[0] - 6, W[1] + 8), 44, -112, -22, 12 * e, op=e))
        # le khopesh en vol : la traînée d'or derrière la lame, et derrière la poignée
        if 'fly' in P:
            (cx, cy), ang = P['fly']
            _, pang = Pp['fly'] if 'fly' in Pp else (None, ang + 60)
            sweep = min(150.0, abs(pang - ang))
            # angle écran de la lame (la lame est vers le haut de l'axe, en +u ; le crochet vers +n)
            a_scr = -ang
            fig.fx_back.append(trail(fig, (cx, cy), 21.5, a_scr - sweep - 30, a_scr - 30 + 4, 8.5, op=0.95))
            fig.fx_back.append(trail(fig, (cx, cy), 18.0, a_scr + 180 - sweep * 0.6, a_scr + 184, 3.0, op=0.7))
        # le sable soulevé par la détente
        k = (tl - 320) / 380.0
        fig.fx_back.append(dust(fig, 96, k))
        # la prise : un éclat d'or contre la main, puis deux étincelles qui retombent
        tau = tl - CATCH_T
        if -10 <= tau < 260:
            G = ctx['G']
            u, n = S.kh_axes(ctx['ang'])
            g = (G[0] + 6 * u[0], G[1] + 6 * u[1])
            e = env(tau, -10, 10, 50, 140)
            if e > 0:
                fig.fx_front.append(spark(fig, g[0] + 4, g[1] - 2, 1.3 * e + 0.3, op=e))
            for i, (vx, vy) in enumerate(((50, -40), (20, -60))):
                if 30 < tau < 260:
                    x, y = ballistic((g[0] + 4, g[1]), (vx, vy), 260, (tau - 30) / 1000)
                    fig.fx_front.append(spark(fig, x, y, 0.55, op=max(0, 1 - (tau - 30) / 230)))
    return f


# ---- l'attaque spéciale

# la crinière de feu (comme la crinière de Kael) : de grosses mèches de flamme couchées vers l'arrière, qui ondulent,
# de longueurs inégales, la pointe relevée ; (racine, 2 points de la courbe, pointe) dans le repère de la tête, largeur
MANE = [
    ((58, 50), (50, 55), (42, 56), (35.5, 52), 9.0),
    ((55, 42), (46, 45), (36, 45), (28, 38), 11.5),
    ((55, 33), (45, 33), (34, 30), (27, 20), 12.5),
    ((58, 25), (50, 22), (42, 17), (39, 6), 11.5),
    ((65, 20), (60, 14), (55, 9), (54, -1), 9.5),
    ((74, 19), (72, 13), (68, 9), (68, 2), 7.0),
]


def mane_svg(fig, tf, k, t, ink=True):
    """La crinière de flammes : un seul contour autour de toute la masse ; tf : repère de la tête → dessin ; k : sa
    taille (0..1). Les mèches ondulent (la vague court de la racine vers la pointe)."""
    if k <= 0.02:
        return ''
    shapes = []
    for j, (p0, p1, p2, p3, w) in enumerate(MANE):
        ph = t / 90.0 - j * 0.9
        sc = lambda p, kk: (p0[0] + (p[0] - p0[0]) * kk, p0[1] + (p[1] - p0[1]) * kk)
        q1 = sc(p1, k)
        q2 = sc((p2[0] + 0.8 * math.sin(2 * ph + 1), p2[1] + 1.2 * math.sin(ph)), k)
        q3 = sc((p3[0] + 1.6 * math.sin(ph + 0.8), p3[1] + 1.8 * math.cos(ph)), k)
        P0, P1, P2, P3 = tf(p0), tf(q1), tf(q2), tf(q3)
        sh = lock(P0, P1, P2, P3, w * (0.55 + 0.45 * k) * abs(tf((1, 0))[0] - tf((0, 0))[0]), n=12, bulge=0.32)
        under = __import__('lib').Shape(sh.subs + sh.move(0.8, -2.4).subs, evenodd=True)
        shapes.append((sh, g_lin(fig, P0, P3, [(0, '#ffe680'), (0.22, '#ffbc34'), (0.58, '#ff7a22'), (1, '#e03a1a')]), 1))
        shapes.append((under, g_lin(fig, P0, P3, [(0, '#ff8a24'), (0.5, '#d8381a'), (1, '#a82418')]), 0.85))
    # chaque mèche pose une ligne sombre sur la suivante : on peint mèche par mèche, silhouettes d'abord
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="1.5" stroke-linejoin="round"/>' % (sh.d(), FINK, FINK)
                  for sh, _, _ in shapes[::2]) if ink else ''
    col = ''
    for i in range(0, len(shapes), 2):
        a, b = shapes[i], shapes[i + 1]
        col += '<path d="%s" fill="%s"/>' % (a[0].d(), a[1])
        col += '<path d="%s" fill-rule="evenodd" fill="%s" opacity="0.85" clip-path="none"/>' % (b[0].d(), b[1]) if False else ''
        col += '<g><clipPath id="mc%d_%d"><path d="%s"/></clipPath><path d="%s" fill-rule="evenodd" fill="%s" opacity="0.85" clip-path="url(#mc%d_%d)"/></g>' % (
            fig.n, i, a[0].d(), b[0].d(), b[1], fig.n, i)
    fig.n += 1
    return '<g>%s%s</g>' % (sil, col)


def mane(fig, ctx, k, t, under=True):
    """La crinière de flammes qui jaillit autour de sa tête au rugissement, derrière la tête (le visage reste net)."""
    H = ctx['HEAD']
    c = mapp(H, (60, 32))
    fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(26 * k + 4), fm(24 * k + 4),
                       g_rad(fig, c, 26 * k + 4, [(0, FIRE[1], 0.5 * k), (0.6, FIRE[2], 0.25 * k), (1, FIRE[3], 0)])))
    fig.fx_back.append(mane_svg(fig, lambda p: mapp(H, p), k, t))


def spirit(fig, c, k=1.0, t=0.0, mane_k=1.0, trail_k=1.0, head=True):
    """La tête de lionne de feu (l'esprit de Sable : sa propre tête, recolorée en feu), tournée vers l'ennemi ; c = son
    milieu ; la crinière de flammes fuit vers l'arrière, des braises traînent derrière elle."""
    hx, hy = 80.0, 39.0
    tf = lambda p: (c[0] + (p[0] - hx) * k, c[1] + (p[1] - hy) * k)
    out_back, out_front = [], []
    # la traînée : deux longues langues couchées vers l'arrière, des braises
    if trail_k > 0:
        for j, (dy, L, w) in enumerate(((-6, 30, 9.0), (6, 22, 7.0))):
            fl = 1 + 0.1 * math.sin(t / 40.0 + j * 2)
            out_back.append(tongue(fig, (c[0] - 12 * k, c[1] + dy * k), L * trail_k * fl, w * k, bend=0.7 if j else -0.7,
                                   lean=0.15 * (1 if j else -1), direction=180 + dy * 1.2))
        for j in range(6):
            fr = (j * 0.37 + t / 400.0) % 1
            out_back.append(ember(fig, c[0] - 20 * k - 30 * fr * trail_k, c[1] + (8 * math.sin(j * 2.1) + 4 * math.sin(t / 60 + j)) * k,
                                  0.55 + 0.25 * (j % 2), op=1 - fr))
    # la crinière : les mèches de feu qui fuient vers l'arrière
    if mane_k > 0:
        out_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(c[0] - 6 * k), fm(c[1] - 2 * k), fm(20 * k), fm(18 * k), g_rad(fig, (c[0] - 6 * k, c[1] - 2 * k), 20 * k, [(0, FIRE[1], 0.5), (1, FIRE[3], 0)])))
        out_back.append(mane_svg(fig, tf, mane_k, t))
    if head:
        sh = S.head_outline(1.0).map(tf)
        gr = g_lin(fig, tf((98, 30)), tf((62, 52)), [(0, FIRE[0]), (0.25, FIRE[1]), (0.6, FIRE[2]), (1, FIRE[3])])
        mouth = sm([(81.6, 41.8), (96.0, 41.2), (93.6, 43.4), (94.4, 46.6), (88, 47.8), (82.2, 46.2)], sharp=(1, 2, 3)).map(tf)
        eye = sm([(S.FACE['oeil_proche'][0] + (x - 76.5) * S.EYE_SX, y) for x, y in ((72.6, 31.0), (76.0, 30.4), (80.4, 32.0), (78.8, 33.4), (75.0, 33.0))],
                 sharp=(0, 2)).map(tf)   # le seul œil, à la place donnée par visage.py
        ears = [sm([(58.4, 26), (58.2, 16.8), (60.2, 14.2), (63.4, 14.0), (65.6, 16.4), (65.8, 26)]).map(tf),
                sm([(74.0, 26), (74.4, 17.4), (76.6, 15.4), (79.2, 15.8), (80.6, 18.2), (80.4, 26)]).map(tf)]
        parts = [(e, g_lin(fig, tf((66, 14)), tf((58, 24)), [(0, FIRE[1]), (1, FIRE[3])]), 1) for e in ears]
        parts += [(sh, gr, 1),
                  (sm([(79, 27), (90.8, 31.6), (98.4, 35.0), (96, 36.6), (84, 34.4)]).map(tf), FIRE[0], 0.55),
                  (mouth, g_lin(fig, tf((90, 41)), tf((86, 48)), [(0, FIRE[4]), (1, FIRE[5])]), 1),
                  (eye, '#fffbe4', 1)]
        out_front.append(outlined(parts, w=1.4))
    fig.fx_back.extend(out_back)
    fig.fx_front.extend(out_front)


def fx_special(tl, P, Pp):
    def f(fig, ctx):
        t = tl
        hot = ctx['P']['hot']
        # la chaleur autour d'elle : une lueur derrière le buste, des braises qui montent
        if hot > 0.3:
            c = ctx['chest']
            fig.under.append((c[0], c[1], 30 + 8 * hot, 34 + 8 * hot, '#ff7a1e', 0.08 * hot, None))
        ch = env(t, 60, 260, 640, 900)
        if ch > 0:
            for i in range(14):
                fr = (i * 0.618) % 1
                x0 = 14 + 96 * fr
                sp = 0.6 + 0.4 * ((i * 0.37) % 1)
                k = ((t / 1000.0) * sp + (i * 0.29) % 1) % 1
                fig.fx_front.append(ember(fig, x0 + 3 * math.sin(k * 6 + i), GR - 4 - 70 * k, 0.45 + 0.25 * (i % 3) / 2,
                                          op=ch * (1 - k) * min(1, k * 5)))
            for j, (x, hh, ww, bd) in enumerate(((28, 8, 4.0, 0.6), (108, 7, 3.6, -0.6))):
                fl = 1 + 0.2 * math.sin(t / 40.0 + j * 2.4)
                (fig.fx_back if j == 0 else fig.fx_front).append(tongue(fig, (x, GR), hh * fl * ch, ww, bend=bd))
        # la lame s'embrase : des langues de feu montent de son dos
        if hot > 0.2 and t < 1000:
            for j, p in enumerate(ctx['blade'][1:6:2]):
                fl = 1 + 0.2 * math.sin(t / 35.0 + j * 2.1)
                L = (4 + 4.5 * min(hot, 2)) * fl * (1.2 if j == 1 else 1.0)
                (fig.fx_front if j == 1 else fig.fx_back).append(
                    tongue(fig, p, L, 3.2 + 1.4 * min(hot, 2), bend=0.8 if j % 2 else -0.7, lean=-0.1 * (j - 1)))
        # la touffe de la queue prend feu
        tf_ = env(t, 300, 400, 650, 900)
        if tf_ > 0:
            tip = ctx['tuft']
            fig.fx_front.append(tongue(fig, tip, 7 * tf_ * (1 + 0.15 * math.sin(t / 30.0)), 3.6, bend=0.6))
        # le rugissement : la crinière de flammes jaillit (derrière la tête), l'air brûlant sort de la gueule
        mk = env(t, SP_ROAR - 30, SP_ROAR + 40, SP_STRIKE - 20, SP_STRIKE + 60)
        if mk > 0:
            mane(fig, ctx, mk, t)
        rk = env(t, SP_ROAR, SP_ROAR + 30, 560, 660)
        if rk > 0:
            m = ctx['mouth']
            for j in range(2):
                tau = ((t - SP_ROAR) / 260.0 + j * 0.5) % 1
                R = 4 + 18 * tau
                fig.fx_front.append(trail(fig, (m[0] - 6 + 4 * tau, m[1]), R + 6, -50, 50, (5.5 - 3 * tau) * rk, hot=True, op=rk * (1 - tau)))
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(m[0] + 2), fm(m[1]), fm(6 * rk), g_rad(
                fig, (m[0] + 2, m[1]), 6 * rk, [(0, FIRE[0], 0.9 * rk), (0.5, FIRE[1], 0.5 * rk), (1, FIRE[2], 0)])))
        # l'éclair du rugissement (arrêt sur l'image) : un éclat chaud qui part de la tête
        fl = env(t, SP_ROAR - 10, SP_ROAR + 10, SP_ROAR + 40, SP_ROAR + 160)
        if fl > 0:
            c = ctx['head']
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(140), g_rad(
                fig, c, 140, [(0, '#fffbe4', 0.6 * fl), (0.15, '#ffe68a', 0.35 * fl), (0.5, '#ffb43a', 0.1 * fl), (1, '#ff7a1e', 0)])))
        # l'abattage : un grand arc de feu en croissant, de la lame armée jusqu'à la lame abattue
        e = env(t, SP_STRIKE - 30, SP_STRIKE, SP_STRIKE + 40, SP_STRIKE + 160)
        if e > 0:
            W = ctx['wrist']
            fig.fx_back.append(trail(fig, (W[0] - 6, W[1] + 8), 46, -115, -20, 14 * e, hot=True, op=e))
        # la lionne de feu bondit vers l'ennemi
        if SP_STRIKE - 20 <= t < SP_HIT + 30:
            ts = [a for a, _ in LION]
            x = monotone(ts, [p[0] for _, p in LION], t)
            y = monotone(ts, [p[1] for _, p in LION], t)
            k = min(1.0, (t - SP_STRIKE + 20) / 80.0)
            op = 1.0 if t < SP_HIT else max(0.0, 1 - (t - SP_HIT) / 30.0)
            lf, lb = len(fig.fx_front), len(fig.fx_back)
            spirit(fig, (x, y), 0.75 + 0.25 * k, t, mane_k=k, trail_k=0.6 + 0.6 * k, head=k > 0.35)
            if op < 1:
                fig.fx_front[lf:] = ['<g opacity="%g">%s</g>' % (op, s_) for s_ in fig.fx_front[lf:]]
                fig.fx_back[lb:] = ['<g opacity="%g">%s</g>' % (op, s_) for s_ in fig.fx_back[lb:]]
        # l'impact : la gerbe de feu sur l'ennemi, les langues qui montent puis baissent, fumée, braises
        if t >= SP_HIT:
            X = ENEMY_X
            tg = t - SP_HIT
            sc = env(tg, 0, 60, 230, 600)
            if sc > 0:
                for j, (dx, hh, ww, bd, ln) in enumerate(((0, 50, 14.0, 0.5, 0.05), (-11, 34, 10.0, -1.0, -0.45), (11, 38, 10.5, 1.0, 0.5),
                                                          (-21, 18, 6.0, -0.9, -0.9), (22, 20, 6.0, 0.9, 0.9))):
                    flick = 1 + 0.08 * math.sin(t / 26.0 + j * 2.3)
                    (fig.fx_front if j == 0 else fig.fx_back).append(
                        tongue(fig, (X + dx * (0.7 + 0.3 * sc), GR), hh * sc * flick, ww * (0.6 + 0.4 * sc), bend=bd, lean=ln))
            fb = env(tg, 0, 20, 60, 220)
            if fb > 0:
                c = (X - 2, GR - 22)
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(30), g_rad(
                    fig, c, 30, [(0, FIRE[0], fb), (0.3, FIRE[1], 0.8 * fb), (0.7, FIRE[2], 0.35 * fb), (1, FIRE[3], 0)])))
            for j, (vx, vy) in enumerate(((-26, -50), (22, -60), (-10, -70), (34, -38), (-36, -30), (10, -66))):
                tau = tg / 1000.0
                if tau < 0.7:
                    x, y = ballistic((X, GR - 20), (vx * 1.6, vy * 1.6), 260, tau)
                    if y < GR - 1:
                        fig.fx_front.append(ember(fig, x, y, 0.8 if vx > 0 else 0.6, op=1 - tau / 0.7))
            sm_k = (tg - 120) / 1000.0
            if 0 < sm_k < 0.9:
                o = env(sm_k, 0, 0.12, 0.4, 0.9)
                for j, (dx, rr, sp) in enumerate(((-10, 5.0, 26), (4, 6.5, 34), (16, 4.4, 24))):
                    fig.fx_back.append(smoke(fig, X + dx + 3 * sm_k * (1 if dx > 0 else -1), GR - 14 - sp * sm_k, rr * (0.7 + 0.7 * sm_k), op=0.85 * o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous elle."""
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
    cx = (58 - x0) * k
    sd.ellipse([cx - 52 * k, fy - 3.2 * k, cx + 50 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


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
    if act:
        Pp, _ = pose_at(T - 0.045, act, t0)
        fx = [fx_attack(tl, P, Pp) if act == 'attack' else fx_special(tl, P, Pp)]
    return S.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        moments = extra or [1.0, a_s + 0.09, a_s + 0.25, a_s + 0.33, a_s + 0.38, a_s + 0.47, a_s + 0.6, a_s + 0.7, a_s + 0.8,
                            s_s + 0.25, s_s + 0.42, s_s + 0.55, s_s + 0.66, s_s + 0.75, s_s + 0.86, s_s + 1.0]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(HERE, '_planche.png')
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
