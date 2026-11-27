# Sylvar vectoriel ANIMÉ (refonte des héros du 26/11/2026, même méthode que Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/isis/build.py) — la garde à l'affût (respiration),
# le tir à l'arc, le tir spécial « Flèche de la faille » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/sylvar/anim.py             # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/sylvar/)
#   python3 refonte-graphique/ui-moderne/heros/sylvar/anim.py --planche [t…]   # quelques images clés (contrôle)
#
# Les poses clés reprennent celles du pixel art (mêmes temps : il vise et bande encore l'arc, lâche d'un coup sec, la
# main part en arrière doigts ouverts, la corde claque et vibre, l'arc saute en avant ; puis, sans un geste de trop, la
# main va chercher une flèche au carquois, l'encoche et bande de nouveau). Les réglages passent de clé en clé par des
# courbes douces sans dépassement. Les articulations tournent autour des vraies jointures : le bras proche est d'une
# seule forme (épaule → coude → poignet), le poing lointain reste sur la poignée de l'arc.
# Effets de terre en vectoriel (dégradés, un contour, courbes ; aucun flou) : cailloux qui montent en tournant vers la
# pointe, pointe de pierre veinée d'or, faille d'or dans le sol, éclats de roche dressés, blocs, poussière en volutes.
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
import sylvar as S  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import crpath, taper  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'sylvar')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-sylvar'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-30, -26, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = S.GRD
INK = '#1f1238'
ENEMY_X = 196.0                      # là où la faille éclate (l'ennemi)
# la terre : pierre, or des veines, poussière
STONE = ['#f6e2b8', '#d0ae80', '#a07e5a', '#6e5248', '#40303a']
GOLD = ['#fffbe4', '#ffe68a', '#f6c24a', '#d88a2a', '#8a4a1e']
DUST = ['#f4e8d0', '#d8c4a4', '#a8907e', '#6e5a62']

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


NUM = ['crouch', 'lean', 'tilt', 'cape', 'tal', 'eyes', 'flex', 'push', 'btilt', 'vib', 'stone', 'ha', 'hang',
       'Ex', 'Ey', 'Wx', 'Wy', 'headx', 'heady']
STEP = ['hand', 'arrow', 'free', 'held']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, cape=0, tal=0, eyes=0, flex=0, push=0, btilt=0, vib=0, stone=0, ha=S.HA0, hang=68.0,
             Ex=S.E0[0], Ey=S.E0[1], Wx=S.W0[0], Wy=S.W0[1], headx=0, heady=0)
    for key, v in k.items():
        if key in ('E', 'W', 'head'):
            n = 'head' if key == 'head' else key
            d[n + 'x'], d[n + 'y'] = v
        elif key not in STEP:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés ; la main, la flèche et
    la corde changent d'état à leur clé (sans fondu)."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    out = {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}
    st = dict(hand='draw', arrow=1.0, free=0.0, held=0.0)
    for tk, k in keys:
        if tk <= t:
            for n in STEP:
                if n in k:
                    st[n] = k[n]
    out.update(st)
    return out


# ======================================================================== les actions (poses clés)
E0, W0 = S.E0, S.W0


def arm(dx, dy=0.0, ex=None):
    """Le bras proche qui tire : le poignet décalé de (dx, dy), le coude suit (un peu moins)."""
    k = 0.8 if ex is None else ex
    return dict(W=(W0[0] + dx, W0[1] + dy), E=(E0[0] + dx * k, E0[1] + dy * 0.5))


OPEN = dict(hand='open', arrow=0, free=1)
REACH = dict(hand='grab', held=1, arrow=0, free=1, E=(43.6, 46.4), W=(41.2, 35.0), ha=-104, hang=62)
# 2) Le tir (pixel : ATTAQUE, 1020 ms) : il vise (la tête s'abaisse sur la flèche), bande encore l'arc (les yeux
# s'avivent), lâche : la main part en arrière doigts ouverts, la corde claque et vibre, l'arc saute en avant et se
# détend ; puis la main va chercher une flèche au carquois, l'encoche, et bande de nouveau.
ATTACK = [
    (0, {}),
    (100, dict(**arm(-1.0), head=(0, 0.6), flex=0.25, eyes=0.5, tal=0.3)),
    (320, dict(**arm(-2.2, -0.2), head=(0.2, 1.0), tilt=1.0, flex=0.65, lean=-0.6, eyes=1.3, tal=-0.4, cape=0.3)),
    (340, dict(**arm(-2.3, -0.2), head=(0.2, 1.0), tilt=1.0, flex=0.68, lean=-0.6, eyes=1.4, tal=-0.4, cape=0.3)),
    # le lâcher
    (345, dict(OPEN, **arm(-4.4, -0.6), ha=-10, head=(0.2, 1.0), tilt=1.0, flex=-1.0, vib=2.8, push=1.0, btilt=4.0, lean=-1.2,
               eyes=1.2, tal=0.4, cape=0.0)),
    (390, dict(OPEN, **arm(-5.8, -0.8), ha=-14, head=(0, 0.4), flex=-1.0, vib=-2.0, push=0.9, btilt=3.0, lean=-1.2, eyes=0.9,
               tal=0.8, cape=-0.3)),
    (450, dict(OPEN, **arm(-6.0, -0.7), ha=-12, flex=-1.0, vib=1.2, push=0.7, btilt=2.0, lean=-1.0, eyes=0.7, tal=0.6, cape=-0.5)),
    (530, dict(OPEN, **arm(-5.2, -0.2), ha=-8, head=(0, -0.2), flex=-1.0, vib=-0.5, push=0.4, btilt=1.0, lean=-0.5, eyes=0.4,
               tal=0.0, cape=-0.4)),
    # la main va chercher une flèche au carquois
    (570, dict(OPEN, **arm(-3.0, -4.0), ha=-60, flex=-1.0, vib=0.2, push=0.2, btilt=0.5, head=(0, -0.6), tal=-0.3)),
    (625, dict(REACH, flex=-1.0, head=(0, -0.8), tilt=-1.0, tal=-0.5, cape=0.2)),
    (660, dict(REACH, E=(44.6, 47.2), W=(44.0, 37.6), ha=-80, hang=40, flex=-1.0, head=(0, -0.6), tal=-0.2, cape=0.3)),
    # encochée : la main revient tirer la corde
    (700, dict(hand='draw', held=0, arrow=1, free=0, W=(58.6, 47.6), E=(44.6, 51.6), ha=-2, flex=-0.62, head=(0, -0.2), tal=0.3, cape=0.3)),
    (800, dict(**arm(4.0), flex=-0.25, head=(0, 0.2), tal=0.3, cape=0.1)),
    (890, dict(**arm(0.6), flex=-0.02, head=(0, 0.3), tal=0.0)),
    (1020, {}),
]
ATTACK_REL = 340          # l'instant du lâcher (ms)

# 3) Le tir spécial « Flèche de la faille » (pixel : SPECIALE, 1750 ms) : il s'ancre, bande l'arc plus fort que jamais ;
# le sol se fend sous ses pieds d'une veine d'or, des cailloux montent en tournant vers la pointe et s'y soudent en une
# lourde pointe de pierre (les yeux s'embrasent) ; il lâche (le recul le repousse), le carreau part dans une traînée
# d'or et de poussière, une faille court sous le sol jusqu'à l'ennemi et la terre y explose en éclats dressés.
SPECIAL = [
    (0, {}),
    (100, dict(**arm(-1.0), crouch=1.0, head=(0, 0.6), flex=0.25, eyes=0.8, stone=0.0, tal=0.3)),
    (210, dict(**arm(-2.0), crouch=1.2, head=(0, 1.0), flex=0.5, eyes=1.1, stone=0.8, tal=-0.3, cape=0.3)),
    (320, dict(**arm(-3.0), crouch=2.0, head=(0.2, 1.0), tilt=1.0, flex=0.75, lean=-0.8, eyes=1.4, stone=1.6, tal=-0.5, cape=0.5)),
    (430, dict(**arm(-3.4), crouch=2.1, head=(0.2, 1.0), tilt=1.0, flex=0.9, lean=-1.0, eyes=1.7, stone=2.4, tal=-0.4, cape=0.4)),
    (690, dict(**arm(-4.0), crouch=2.3, head=(0.3, 1.2), tilt=1.4, flex=1.05, lean=-1.2, eyes=2.0, stone=3.0, tal=-0.6, cape=0.5)),
    # le lâcher : le recul le repousse
    (695, dict(OPEN, **arm(-6.4, -0.6), ha=-12, crouch=2.2, head=(-0.2, 0.6), flex=-1.0, vib=3.2, push=2.0, btilt=4.5,
               lean=-2.4, eyes=2.0, stone=0, tal=0.6, cape=-0.4)),
    (750, dict(OPEN, **arm(-7.0, -0.8), ha=-16, crouch=2.0, head=(-0.3, 0.2), flex=-1.0, vib=-2.4, push=1.6, btilt=3.5,
               lean=-2.2, eyes=1.6, tal=1.0, cape=-0.8)),
    (800, dict(OPEN, **arm(-6.8, -0.6), ha=-14, crouch=1.6, flex=-1.0, vib=1.4, push=1.0, btilt=2.5, lean=-1.6, eyes=1.3,
               tal=0.8, cape=-0.7)),
    # arrêt sur l'image : la terre explose chez l'ennemi
    (950, dict(OPEN, **arm(-6.0, -0.4), ha=-10, crouch=1.0, head=(0, -0.4), flex=-1.0, vib=-0.4, push=0.6, btilt=1.5, lean=-1.0,
               eyes=1.0, tal=0.2, cape=-0.4)),
    (1160, dict(OPEN, **arm(-5.2, -0.2), ha=-8, crouch=0.6, head=(0, -0.6), flex=-1.0, push=0.3, btilt=0.6, lean=-0.4, eyes=0.6,
                tal=-0.2, cape=0.0)),
    (1340, dict(OPEN, **arm(-4.6), ha=-6, crouch=0.0, head=(0, 0), flex=-1.0, eyes=0.3, tal=0.0, cape=0.2)),
    # il va chercher une flèche, l'encoche, bande l'arc : retour en garde, silencieux
    (1390, dict(OPEN, **arm(-3.0, -4.0), ha=-60, flex=-1.0, head=(0, -0.6), tal=-0.3)),
    (1450, dict(REACH, flex=-1.0, head=(0, -0.8), tilt=-1.0, tal=-0.5, cape=0.2)),
    (1490, dict(REACH, E=(44.6, 47.2), W=(44.0, 37.6), ha=-80, hang=40, flex=-1.0, head=(0, -0.6), tal=-0.2, cape=0.3)),
    (1530, dict(hand='draw', held=0, arrow=1, free=0, W=(58.6, 47.6), E=(44.6, 51.6), ha=-2, flex=-0.62, head=(0, -0.2), tal=0.3, cape=0.3)),
    (1620, dict(**arm(4.0), flex=-0.25, head=(0, 0.2), tal=0.3, cape=0.1)),
    (1700, dict(**arm(0.6), flex=-0.02, head=(0, 0.3))),
    (1750, {}),
]
SP_REL = 690
SP_HIT = 790              # la faille arrive chez l'ennemi


# ======================================================================== la respiration (en boucle, 3 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2,4 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : les yeux verts au fond du crâne de cerf s'embrasent lentement puis baissent, et le talisman pendu au
    bois (perle d'os, plume rouge) se balance plus large. Une pose partielle pour build() ; jouée au combat (pose_at)
    et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(eyes=2.4 * (0.5 - 0.5 * math.cos(u)), tal=1.5 * math.sin(u - 0.8))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.45 * (0.5 - 0.5 * math.cos(u - 1.6)), heady=0.35 * math.sin(u - 0.7),
                tilt=0.5 * math.sin(u - 0.9), tal=0.55 * math.sin(u - 1.9), cape=0.5 * math.sin(u - 2.2),
                flex=0.04 * math.sin(u - 0.5))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or dict(flat({}), hand='draw', arrow=1.0, free=0.0, held=0.0)
    P = {}
    for n in NUM:
        if n in ('headx', 'heady', 'Ex', 'Ey', 'Wx', 'Wy'):
            continue
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['E'] = (src['Ex'], src['Ey'])
    P['W'] = (src['Wx'], src['Wy'])
    for n in STEP:
        P[n] = src[n]
    sg = signe(T)                                  # le signe du repos : les yeux s'embrasent (anim.signe)
    P['eyes'] += w * sg['eyes']
    P['tal'] += w * sg['tal']
    # clignement : la lueur des yeux baisse un instant
    P['blink'] = 1.0 if (w > 0.95 and 2.62 <= (T % IDLE_T) < 2.72) else 0.0
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=INK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
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


def rock(fig, x, y, s=1.6, rot=0.0, op=1.0, seed=0, vein=False):
    """Un caillou, un éclat de roche : facettes, éclairé en haut à droite, une veine d'or (spéciale)."""
    base = [[(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)],
            [(-1.1, -0.2), (-0.2, -1.0), (1.0, -0.7), (1.0, 0.6), (-0.3, 1.1)],
            [(-0.9, -0.8), (0.6, -1.0), (1.2, 0.2), (0.2, 1.0), (-1.1, 0.5)]][seed % 3]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, STONE[1]), (0.5, STONE[2]), (1, STONE[4])])
    parts = [(sh, gr, 1)]
    hi = sm([pts[1], pts[2], ((pts[2][0] + x) / 2, (pts[2][1] + y) / 2), ((pts[1][0] + x) / 2, (pts[1][1] + y) / 2)], t=0.4)
    parts.append((hi, STONE[0], 0.55))
    if vein:
        parts.append((ribbon([((pts[0][0] + x) / 2, (pts[0][1] + y) / 2), (x, y), ((pts[3][0] + x) / 2, (pts[3][1] + y) / 2)],
                             [0.1, s * 0.35, 0.1]), GOLD[1], 1))
    return outlined(parts, w=1.0, op=op)


def dust(fig, cx, cy, r, op=1.0):
    """Une volute de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DUST[3], DUST[3]) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def mote(fig, x, y, r=0.6, op=1.0):
    """Une paillette d'or (un point chaud et sa petite lueur, en dégradé radial)."""
    glow = g_rad(fig, (x, y), r * 3.2, [(0, GOLD[2], 0.55 * op), (1, GOLD[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, GOLD[0], op), (0.6, GOLD[1], op), (1, GOLD[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def streak(fig, a, b, w, cols, op=1.0):
    """Une traînée d'air derrière ce qui file : un fuseau effilé (pointe en arrière), du transparent à la couleur."""
    if math.dist(a, b) < 1:
        return ''
    c = [(a[0] + (b[0] - a[0]) * i / 8, a[1] + (b[1] - a[1]) * i / 8) for i in range(9)]
    ws = [w * (i / 8) ** 0.7 for i in range(9)]
    ws[0] = 0.05
    sh = ribbon(c, ws)
    gr = g_lin(fig, a, b, [(0, cols[0], 0), (0.7, cols[0], 0.55 * op), (1, cols[1], 0.9 * op)])
    return '<path d="%s" fill="%s"/>' % (sh.d(), gr)


def flying_arrow(fig, nock, ang, length=63.5, stone=0.0, op=1.0):
    """La flèche en vol : un objet à part, avec son contour (dessinée par sylvar.arrow_parts dans une petite figure)."""
    from atelier import Figure, xf
    sub = Figure(*VIEW, ow=fig.ow)
    A = lambda sh: xf(sh, nock[0], nock[1], ang)
    S.arrow_parts(sub, A, length, stone, 'x')
    svg = sub.svg()
    inner = svg[svg.index('<defs>'):svg.rindex('</svg>')]
    # identifiants uniques (la petite figure a les siens)
    tag = fig.uid('fa')
    inner = inner.replace('id="', 'id="%s' % tag).replace('url(#', 'url(#%s' % tag).replace('href="#', 'href="#%s' % tag)
    return '<g opacity="%g">%s</g>' % (op, inner)


def ring_wave(fig, c, r, w, op, cols=(GOLD[1], '#ffffff')):
    """Une onde (un anneau, plus épais devant que derrière : une courbe pleine, pas des rayons)."""
    if r < 0.5 or op <= 0.02:
        return ''
    outer = [(c[0] + r * 0.55 * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in range(-90, 91, 15)]
    inner = [(c[0] + (r * 0.55 - w * math.cos(math.radians(a)) ** 2) * math.cos(math.radians(a)),
              c[1] + (r - w * 0.3) * math.sin(math.radians(a))) for a in range(90, -91, -15)]
    sh = sm(outer + inner, sharp=(0, len(outer) - 1, len(outer), len(outer) + len(inner) - 1), t=0.7)
    gr = g_lin(fig, (c[0], c[1] - r), (c[0] + r * 0.55, c[1]), [(0, cols[0], 0.4 * op), (1, cols[1], 0.9 * op)])
    return '<path d="%s" fill="%s"/>' % (sh.d(), gr)


def crack(fig, x0, x1, heat, seed=0, w=1.0):
    """La faille dans le sol : une fêlure qui zigzague, son cœur d'or, une lueur douce (refroidit : heat 1 → 0)."""
    if x1 - x0 < 1 or heat <= 0.02:
        return ''
    n = max(3, int((x1 - x0) / 5))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.6 + 0.7 * math.sin(i * 2.1 + seed) + (0.5 if i % 2 else -0.3)) for i in range(n + 1)]
    halo = ribbon(pts, [0.3] + [4.2 * w] * (n - 1) + [0.3])
    core = ribbon(pts, [0.2] + [1.6 * w] * (n - 1) + [0.2])
    hot = ribbon(pts, [0.1] + [0.7 * w] * (n - 1) + [0.1])
    gh = g_lin(fig, (x0, GR), (x1, GR), [(0, GOLD[3], 0.12 * heat), (1, GOLD[2], 0.4 * heat)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        halo.d(), gh, core.d(), STONE[4], min(1, heat * 1.3), hot.d(), GOLD[1], heat)


def spike(fig, bx, h, w, lean=0.0, op=1.0):
    """Un éclat de roche dressé (qui jaillit du sol) : facettes, éclairé à droite, une veine d'or."""
    if h < 0.6:
        return ''
    tip = (bx + lean * h, GR - h)
    pts = [(bx - w / 2, GR + 0.6), (bx - w * 0.3 + lean * h * 0.4, GR - h * 0.55), tip, (bx + w * 0.34 + lean * h * 0.5, GR - h * 0.45),
           (bx + w / 2, GR + 0.6)]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (bx + w, GR - h), (bx - w, GR), [(0, STONE[1]), (0.5, STONE[2]), (1, STONE[4])])
    face = sm([tip, (bx + w * 0.34 + lean * h * 0.5, GR - h * 0.45), (bx + w / 2, GR + 0.6), (bx + w * 0.05, GR + 0.6)], t=0.4)
    vein = ribbon([(bx - w * 0.05, GR), (bx + lean * h * 0.5 + w * 0.05, GR - h * 0.5), (tip[0] - lean * 0.8, tip[1] + h * 0.2)],
                  [w * 0.12, w * 0.08, 0.05])
    return outlined([(sh, gr, 1), (face, STONE[0], 0.45), (vein, GOLD[1], 0.95)], w=1.4, op=op)


# ---- l'attaque de base

def fx_attack(tl):
    def f(fig, ctx):
        tau = tl - ATTACK_REL
        if 0 <= tau < 420:
            # la flèche file vers la droite et sort du cadre ; derrière elle, une traînée d'air
            v = 0.75                                        # pixels du dessin par ms
            nk = (ctx['N0'][0] + v * tau + 4, ctx['N0'][1] - 0.02 * tau)
            if nk[0] < VIEW[0] + VIEW[2] + 10:
                fig.fx_front.append(streak(fig, (max(ctx['N0'][0], nk[0] - 38), nk[1]), (nk[0] + 4, nk[1]), 2.6,
                                           ('#f4ecd6', '#ffffff')))
                fig.fx_front.append(flying_arrow(fig, nk, 0))
            # une traînée lointaine qui s'efface
            k = env(tau, 0, 30, 140, 400)
            if k > 0:
                x0 = 112 + 0.5 * tau
                fig.fx_back.append(streak(fig, (x0, ctx['N0'][1] - 0.5), (VIEW[0] + VIEW[2], ctx['N0'][1] - 0.5), 1.4,
                                          ('#d8c4a4', '#fff4dc'), op=k))
        if 0 <= tau < 160:
            # la corde claque : une onde courbe devant l'arc (un anneau plein, pas des rayons)
            o = env(tau, 0, 20, 60, 160)
            g = ctx['G']
            fig.fx_front.append(ring_wave(fig, (g[0] + 3 + 0.04 * tau, g[1] - 5), 3 + 0.05 * tau, 1.8, o, ('#f4ecd6', '#ffffff')))
    return f


# ---- l'attaque spéciale

def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        feet = (64, GR)
        # 1) la faille s'ouvre sous ses pieds (veine d'or), elle refroidit après le tir
        heat = env(tl, 40, 300, 900, 1500)
        if heat > 0:
            sp = min(1.0, max(0.0, (tl - 40) / 380))
            fig.fx_back.append(crack(fig, feet[0] - 26 * sp, feet[0] + 30 * sp, heat, seed=1, w=1.4))
        # la lueur d'or au sol, sous lui
        gl = env(tl, 60, 400, 700, 1000)
        if gl > 0:
            fig.glow(feet[0], GR, 36 * gl, 7 * gl, GOLD[2], 0.5 * gl)
        tip = ctx['tip']
        # 2) les cailloux s'arrachent du sol et montent en tournant vers la pointe
        if tl < SP_REL:
            for j in range(9):
                start = 40 + 55 * j
                u = (tl - start) / 330.0
                if 0 <= u < 1:
                    x0 = feet[0] - 30 + (j * 37) % 62
                    p0 = (x0, GR - 0.5)
                    e = u * u * (3 - 2 * u)
                    # une spirale qui se resserre sur la pointe
                    rr = (1 - e) * (10 + 3 * (j % 3))
                    ang = j * 1.7 + e * 5.5
                    mid = (p0[0] + (tip[0] - p0[0]) * e, p0[1] + (tip[1] - p0[1]) * e - 14 * math.sin(math.pi * e))
                    x = mid[0] + rr * math.cos(ang) * 0.6
                    y = mid[1] + rr * math.sin(ang) * 0.4
                    s = 1.4 - 0.6 * e
                    fig.fx_front.append(rock(fig, x, y, s, rot=tl * 0.9 + j * 60, seed=j, op=1 if u < 0.85 else (1 - u) / 0.15))
            # la poussière soulevée à ses pieds
            dk = env(tl, 30, 160, 420, 640)
            for j, dx in enumerate((-22, -9, 8, 22)):
                if dk > 0:
                    fig.fx_back.append(dust(fig, feet[0] + dx + 2 * math.sin(tl / 90 + j), GR - 2 - 5 * dk * (1 + j % 2),
                                            2.2 + 1.4 * dk, op=0.75 * dk))
        # 3) la pointe : lueur d'or, paillettes en orbite pendant la tenue
        if 200 <= tl < SP_REL:
            h = env(tl, 200, 600, 680, 720)
            fig.glow(tip[0], tip[1], 6 + 6 * h, 6 + 6 * h, GOLD[2], 0.45 * h)
            if tl >= 430:
                for j in range(6):
                    a = tl / 120.0 + j * math.pi / 3
                    fig.fx_front.append(mote(fig, tip[0] - 2 + 7 * math.cos(a), tip[1] + 4.2 * math.sin(a), 0.5, op=0.9))
        # 4) le lâcher : le carreau de pierre file dans une traînée d'or et de poussière
        tau = tl - SP_REL
        if 0 <= tau < 130:
            v = 1.2
            nk = (ctx['N0'][0] + v * tau + 4, ctx['N0'][1])
            hx = nk[0] + 63.5
            if hx < ENEMY_X + 6:
                fig.fx_front.append(streak(fig, (max(60, nk[0] - 50), nk[1]), (nk[0] + 6, nk[1]), 5.0, (GOLD[2], GOLD[0])))
                fig.fx_front.append(streak(fig, (max(60, nk[0] - 30), nk[1] + 0.6), (nk[0] + 4, nk[1]), 2.4, (DUST[1], '#ffffff')))
                fig.fx_front.append(flying_arrow(fig, nk, 0, stone=3))
                fig.glow(hx, nk[1], 10, 8, GOLD[2], 0.5)
        if 0 <= tau < 200:
            o = env(tau, 0, 20, 80, 200)
            g = ctx['G']
            fig.fx_front.append(ring_wave(fig, (g[0] + 4 + 0.05 * tau, g[1] - 5), 4 + 0.06 * tau, 2.4, o))
        # la faille court sous le sol jusqu'à l'ennemi
        if tau >= 0:
            run = min(1.0, tau / (SP_HIT - SP_REL))
            hk = env(tl, SP_REL, SP_REL + 40, 1250, 1700)
            if hk > 0:
                fig.fx_back.append(crack(fig, 70, 70 + (ENEMY_X - 70) * run, hk, seed=3, w=1.1))
        # 5) l'impact : la terre explose en éclats dressés, des blocs volent, la poussière se défait en volutes
        ti = tl - SP_HIT
        if ti >= 0:
            X = ENEMY_X
            fl = env(ti, 0, 30, 90, 260)
            if fl > 0:
                fig.glow(X, GR - 8, 26 * fl, 18 * fl, GOLD[1], 0.55 * fl)
            sc = env(ti, 0, 70, 380, 620)
            if sc > 0:
                for j, (dx, hh, ww, ln) in enumerate(((0, 30, 9.0, 0.05), (-9, 21, 7.0, -0.25), (9, 24, 7.5, 0.22),
                                                      (-17, 12, 5.5, -0.45), (17, 14, 5.5, 0.4), (-4, 15, 5.0, -0.1))):
                    grow = min(1.0, sc * (1.2 - 0.06 * j))
                    (fig.fx_front if j in (0, 2) else fig.fx_back).append(spike(fig, X + dx, hh * grow, ww, lean=ln))
            for j, (vx, vy) in enumerate(((-70, -150), (60, -170), (-110, -90), (115, -100), (-25, -210), (30, -195), (-150, -40), (150, -50))):
                t_ = (ti - 15 * (j % 3)) / 1000.0
                if 0 <= t_ < 0.8:
                    x, y = ballistic((X, GR - 8), (vx, vy), 320, t_)
                    if y < GR - 0.5:
                        fig.fx_front.append(rock(fig, x, y, 1.9 if j % 2 else 1.4, rot=t_ * 700 + j * 50, seed=j, vein=(j % 3 == 0)))
            dk = (ti - 80) / 1000.0
            if 0 < dk < 1.3:
                o = env(dk, 0, 0.15, 0.6, 1.3)
                for j, (dx, rr, sp) in enumerate(((-16, 5.0, 16), (0, 6.5, 24), (16, 5.0, 18), (-28, 3.8, 8), (28, 4.0, 10))):
                    fig.fx_back.append(dust(fig, X + dx + 5 * dk * (1 if dx > 0 else -1), GR - 4 - sp * dk, rr * (0.7 + 0.7 * dk), op=0.85 * o))
                for j in range(5):
                    fig.fx_front.append(mote(fig, X - 18 + 9 * j + 3 * math.sin(dk * 5 + j), GR - 14 - 30 * dk - 5 * j, 0.5, op=o))
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
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    sh = Image.new('RGBA', (w, h))
    cx = (62 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 30 * k, fy - 3.0 * k, cx + 30 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes — repos ×2, attaque ×2, spéciale."""
    seq = [('idle', 4.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
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
    P = pose_at(T, act, t0)
    fx = []
    if act:
        tl = (T - t0) * 1000
        # l'encoche au moment du lâcher (d'où part la flèche)
        Pr = pose_at(t0 + (ATTACK_REL if act == 'attack' else SP_REL) / 1000.0 - 0.001, act, t0)
        N0 = S.build(pose=Pr).ctx['N']
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
        fx = [lambda fig, ctx, f_=fx[0], N0=N0: (ctx.__setitem__('N0', N0), f_(fig, ctx))]
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


def find_offset(sprite, frame):
    """Où le pixel art est posé dans une image du GIF (à l'échelle 1)."""
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
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées,
    et la place du dessin dans l'image (repère du dessin : pieds en (64, 116))."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-isis-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'myths-9.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    # le sprite de pose : pieds (55, 115) = (64, 116) du dessin
    return out, (ox - 9, oy + 1)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de la terre (Méduse), le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'meduse.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (100, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (64 - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)], PW, PH, 'b')
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
        moments = [1.0, a_s + 0.32, a_s + 0.36, a_s + 0.42, a_s + 0.6, a_s + 0.64, a_s + 0.7, a_s + 0.85,
                   s_s + 0.3, s_s + 0.6, s_s + 0.72, s_s + 0.82, s_s + 0.9, s_s + 1.05, s_s + 1.3, s_s + 1.6]
        rest = [a for a in sys.argv[2:] if not a.startswith('--')]
        if rest:
            moments = [float(x) for x in rest]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
    names2, n2 = game_size_part()
    allf = pngs + names2
    for i, p in enumerate(allf):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    # le GIF : la partie 1 seulement (repos ×2, attaque ×2, spéciale), ≈ 400 px de large
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-frames:v', str(n),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024),
          '— partie 1 : %.1f s, partie 2 : %.1f s' % (total, n2 / FPS))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
