# Célia vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/celia/build.py) —
# respiration, attaque de base « aiguilles de glace », attaque spéciale d'équipe « Voile de neige » — dans le style lisse
# de l'interface, à 24 images par seconde (même méthode que Kael : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/celia/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/celia/
#   python3 refonte-graphique/ui-moderne/heros/celia/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (celia.py) est fait de morceaux ; chaque image le redessine dans une POSE (la robe se cisaille
# depuis le sol, le buste respire, la tête suit avec retard, l'onde du vent froid court dans les longues mèches, les
# manches se balancent, le bras lointain se replie ou se tend : la manche suit l'épaule, le coude et le poignet). Les
# poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps : préparation tenue, geste ample, retour lent),
# reliées par des courbes douces sans dépassement. Les effets (cristaux taillés, aiguilles et leur traîne de givre,
# fleur de glace, brume, tourbillon de flocons, anneau au sol, aura givrée, éclats de lumière) sont dessinés dans le
# même style : dégradés, un seul contour pour les objets solides (la brume et la neige n'en ont pas), aucun flou SVG ;
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
import celia as C  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import crpath, taper, crystal_shapes  # noqa: E402
from lib import sparkle_shape  # noqa: E402

ROOT = C.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'celia')
TMP = os.path.join(HERE, '_images')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-celia'
FPS = 24
VIEW = (-22, -26, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = C.GRD
FOE = (228.0, 82.0)                  # l'ennemi (milieu du corps), comme dans le pixel art
ICE_INK = '#14244e'                  # le contour de la glace (comme les cristaux du dessin)
HC = (68.0, 44.0)                    # le centre de la ronde des cristaux (spéciale)
FEET_X = 67.0                        # le centre de l'anneau au sol

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


NUM = ['crouch', 'lean', 'tilt', 'headx', 'heady', 'hx', 'hy', 'hrot', 'mp', 'ml', 'ha', 'hl', 'eyes', 'blow', 'breath']
DEF = dict(crouch=0, lean=0, tilt=0, headx=0, heady=0, hx=0, hy=0, hrot=0, mp=0, ml=0, ha=1.0, hl=0, eyes=0, blow=0, breath=0)


def flat(k):
    d = dict(DEF)
    for key, v in k.items():
        if key == 'hand':
            d['hx'], d['hy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


def curve(keys, t):
    """Une seule valeur suivant ses clés [(t, v)…]."""
    return monotone([k[0] for k in keys], [k[1] for k in keys], t)


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


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) L'attaque de base (pixel : ATTAQUE, 1130 ms) : elle ramène la main vers elle, paume en l'air, le buste recule, la
# tête se baisse ; les trois cristaux descendent sur la paume en tournant et se couchent en éventail, pointes vers
# l'ennemi ; elle TIENT ; puis d'un geste ample elle pousse la main : les aiguilles partent l'une après l'autre, se
# plantent dans l'ennemi et y font éclore une fleur de glace qui éclate ; trois cristaux renaissent sur sa paume.
ATTACK = [
    (0, {}),
    (110, dict(hand=(-2, 1), lean=-1, head=(-1, 1), mp=1, ml=1, hrot=-4)),
    (300, dict(hand=(-3, 1.2), lean=-1.2, crouch=1, head=(-1, 1.2), tilt=-1.5, ha=1.2, mp=1, ml=1.2, hrot=-6)),
    (350, dict(hand=(-3.2, 1.2), lean=-1.3, crouch=1, head=(-1, 1.2), tilt=-1.5, ha=1.2, mp=1, ml=1.2, hrot=-6)),
    (400, dict(hand=(4, -2), lean=2, head=(1, 0), tilt=1, ha=1.5, hl=1, mp=-1, ml=-1.4, hrot=6)),
    (460, dict(hand=(5, -2.2), lean=2.2, head=(1, 0), tilt=1.2, ha=1.5, hl=1, mp=-1, ml=-1.6, hrot=7)),
    (630, dict(hand=(5, -2), lean=2, head=(1, 0), tilt=1, ha=1.3, hl=0.5, mp=0, ml=-1, hrot=5)),
    (740, dict(hand=(4, -1), lean=1, head=(1, 0), ha=1.1, mp=1, ml=0, hrot=3)),
    (850, dict(hand=(2, 0), lean=1, mp=1, ml=1, hrot=1)),
    (970, dict(hand=(1, 0), mp=0, ml=1)),
    (1130, {}),
]
NEEDLE_GO = 360            # les aiguilles partent (ms)

# 3) La spéciale d'équipe « Voile de neige » (pixel : SPECIALE, 2020 ms) : les cristaux s'élèvent et tournent autour
# d'elle, ses yeux s'allument, elle inspire (elle se grandit, les mèches se soulèvent, la neige converge), TIENT ; puis
# elle souffle (image tenue) : les cristaux s'embrasent, le tourbillon de flocons descend autour d'elle et s'ouvre en
# anneau au sol, l'aura givrée monte, des éclats partent en gerbe ; tout se défait, les cristaux reviennent.
SPECIAL = [
    (0, {}),
    (120, dict(hand=(-2, -2), lean=-1, head=(0, 1), mp=1, ml=1)),
    (250, dict(hand=(-3, -3), lean=-1, head=(0, 1), hl=0.5, mp=1, ml=1, eyes=1)),
    (360, dict(hand=(-4, -4), lean=-1, hl=1, mp=1, eyes=1, ha=1.2)),
    (570, dict(hand=(-4, -4), crouch=-1.2, breath=1, lean=-1, head=(0, -1), tilt=-1, hl=1.6, ha=1.3, mp=1, eyes=1)),
    (650, dict(hand=(-4, -4.2), crouch=-1.3, breath=1, lean=-1, head=(0, -1.2), tilt=-1.2, hl=1.8, ha=1.3, mp=1, eyes=1)),
    (720, dict(hand=(-3, -4), lean=1, head=(1, 0), tilt=1.5, hl=2, ha=1.7, mp=-1, ml=-1, eyes=1, blow=1)),
    (870, dict(hand=(-3, -4), lean=1, head=(1, 0), tilt=1.5, hl=2, ha=1.7, mp=-1, ml=-1, eyes=1, blow=1)),
    (970, dict(hand=(-3, -4), lean=1, head=(1, 0), tilt=1.2, hl=2, ha=1.6, mp=-1, ml=-1, eyes=1, blow=1)),
    (1080, dict(hand=(-3, -3), lean=1, head=(1, 0), hl=1.5, ha=1.4, mp=0, ml=-1, eyes=1)),
    (1200, dict(hand=(-2, -3), lean=1, head=(1, 0), hl=1, ha=1.2, ml=0, eyes=1)),
    (1330, dict(hand=(-2, -2), hl=0.5, mp=1, eyes=1)),
    (1470, dict(hand=(-1, -2), mp=1, ml=1, eyes=1)),
    (1590, dict(hand=(-1, -1), ml=1, eyes=0.2)),
    (1710, dict(hand=(0, -1), mp=-1)),
    (1850, dict(mp=-1)),
    (2020, {}),
]
LAUNCH = 720               # elle souffle : tout part (ms) ; l'image est tenue jusqu'à 870

# ======================================================================== la respiration (en boucle, 2,16 s comme le pixel)
IDLE_T = 2.16


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, heady=0.35 * math.sin(u - 0.9), tilt=0.6 * math.sin(u - 1.2),
                mp=0.9 * math.sin(u - 2 * math.pi * 0.3), ml=0.9 * math.sin(u - 2 * math.pi * 0.5), hy=-0.35 * br,
                hrot=0.8 * math.sin(u - 1.0))


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
    P['breath'] = clamp(P['breath'])
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    u = 2 * math.pi * T / IDLE_T
    P['ph'] = u + (0.0 if not act else 0.0018 * tl * (P['ha'] - 1.0))
    P['bob'] = tuple(1.2 * math.sin(u - 2 * math.pi * k / 3) for k in range(3))
    P['blink'] = 1.0 if (w > 0.95 and 1.62 <= (T % (2 * IDLE_T)) < 1.72) else 0.0
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, ry or r, stops)


def outlined(shapes_fills, ink=ICE_INK, w=1.6, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def path(sh, fill, op=1.0):
    return '<path d="%s" fill="%s"%s/>' % (sh.d(), fill, '' if op >= 1 else ' opacity="%g"' % max(0, op))


def crystal(fig, c, L, W, ang, lit=0.0, op=1.0):
    """Un cristal taillé (objet solide : un contour), redessiné à n'importe quel angle ; lit : il s'embrase."""
    sil, left, right, ridge, low, top, bot = crystal_shapes(c, L, W, ang)
    lc = C.ICE.light if lit < 0.5 else ('#e4fbff' if lit < 1.5 else '#ffffff')
    bc = C.ICE.base if lit < 0.5 else ('#9ae6fa' if lit < 1.5 else '#d4f8ff')
    sc = C.ICE.shadow if lit < 0.5 else ('#4aaee0' if lit < 1.5 else '#8ad8f4')
    g0 = g_lin(fig, top, bot, [(0, lc), (0.5, bc), (1, sc)])
    gl = g_lin(fig, top, bot, [(0, C.ICE.base if lit < 1 else '#9ae6fa'), (1, sc)])
    gr = g_lin(fig, top, bot, [(0, '#ffffff'), (0.5, lc), (1, bc)])
    return outlined([(sil, g0, 1), (left, gl, 1), (right, gr, 1), (low, C.ICE.shadow if lit < 1 else '#6cc6ee', 0.7),
                     (ridge, '#ffffff', 0.95)], w=2 * fig.ow * 0.9, op=op)


def halo(fig, c, r, op=0.6):
    """La lumière glacée autour d'un cristal (un dégradé, pas de flou)."""
    if r <= 0.2 or op <= 0.01:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(fig, c, r, [
        (0, '#e8fdff', op), (0.45, '#8ae4fa', op * 0.45), (1, '#5ccaee', 0)]))


def shard(fig, c, L, ang, op=1.0):
    """Un éclat tout de lumière (blanc, givre, cyan ; sans contour)."""
    sil, left, right, ridge, low, top, bot = crystal_shapes(c, L, L * 0.42, ang, tip=0.36, tail=0.4)
    return '<g opacity="%g">%s%s%s</g>' % (op, path(sil, g_lin(fig, top, bot, [(0, '#ffffff'), (0.5, '#b8f2ff'), (1, '#5ccaee')])),
                                            path(left, '#8ae4fa', 0.7), path(ridge, '#ffffff', 0.95))


def snow(fig, x, y, r=0.9, op=1.0):
    """Un flocon de l'air (sans contour) : un cœur blanc, un bord lavande, lisible sur tous les fonds."""
    if op <= 0.02:
        return ''
    return ('<g opacity="%g"><circle cx="%s" cy="%s" r="%s" fill="#a6aee4"/><circle cx="%s" cy="%s" r="%s" fill="#ffffff"/></g>'
            % (op, fm(x), fm(y), fm(r), fm(x + 0.12 * r), fm(y - 0.12 * r), fm(r * 0.68)))


def flake(fig, x, y, r=1.6, op=1.0, rot=0.0):
    """Une étincelle de neige (petit objet solide, comme celles du dessin) : quatre branches courbes, un contour."""
    sh = sparkle_shape(x, y, r, 0.3)
    if rot:
        sh = sh.rot(rot, x, y)
    return outlined([(sh, g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, '#ffffff'), (1, '#b8f2ff')]), 1),
                     (ellipse(x, y, r * 0.3, r * 0.3), '#ffffff', 1)], w=1.3 * fig.ow, op=op)


def frost(fig, pts, wmax, op=1.0, tones=('#ffffff', '#d4ecff', '#9aa6e2'), head=0.6):
    """Un ruban de givre (brume, traîne, souffle) : effilé aux deux bouts, cœur blanc, bord lavande, sans contour."""
    if len(pts) < 3 or op <= 0.02 or wmax <= 0.1:
        return ''
    n = len(pts)
    ws = []
    for i in range(n):
        s = i / (n - 1)
        ws.append(max(0.05, wmax * (s / head if s < head else (1 - s) / (1 - head)) ** 0.8))
    outer = ribbon(pts, ws, True)
    inner = ribbon(pts, [w * 0.55 for w in ws], True)
    g = g_lin(fig, pts[0], pts[-1], [(0, tones[2], 0.0), (0.5, tones[1], 0.85), (1, tones[1], 0.9)])
    return '<g opacity="%g">%s%s</g>' % (op, path(outer, g), path(inner, tones[0], 0.85))


def mist(fig, cx, cy, r, op=1.0, seed=0):
    """Une bouffée de brume givrée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    k = [(0, 0, 1), (0.8, 0.25, 0.74), (-0.85, 0.3, 0.7), (0.15, -0.6, 0.64), (-0.4, 0.75, 0.55)]
    balls = [(cx + dx * r, cy + dy * r, rr * r * (0.92 + 0.12 * math.sin(seed + i))) for i, (dx, dy, rr) in enumerate(k)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#ffffff'), (0.5, '#dfe6fb'), (1, '#a6aee4')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#6c70b8" stroke="#6c70b8" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def tongue(fig, base, h, w, lean=0.0, wob=0.0, op=1.0):
    """Une langue de l'aura givrée : large et blanche à la base, fine et cyan au bout, en S ; sans contour dur."""
    if h < 0.8 or op <= 0.02:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + wob * w * 0.4, by - h * 0.33)
    p2 = (bx - wob * w * 0.35 + lean * h * 0.5, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    g = g_lin(fig, p0, p3, [(0, '#ffffff', 0.95), (0.35, '#c8f6ff', 0.85), (0.75, '#5ccaee', 0.6), (1, '#2c88c6', 0.2)])
    return '<g opacity="%g">%s%s</g>' % (op, path(sh.move(0.5, 0.4), '#4a62b8', 0.35), path(sh, g))


def bezq(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def bezc(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


# ---- les cristaux : places et angles (angle depuis la verticale, + = penché vers la droite)

def rest_cryst(ctx, lift=(0.0, 0.0, 0.0), dx=(0.0, 0.0, 0.0), bob=(0, 0, 0), scale=(1, 1, 1), lit=0.0):
    W = ctx['W']
    ox, oy = W[0] - C.W0[0], W[1] - C.W0[1]
    return [(c[0] + ox + dx[i], c[1] + oy - lift[i] + bob[i], a, scale[i], lit) for i, (c, L, w, a) in enumerate(C.CRY0)]


def needle_spec(ctx, k):
    """Les aiguilles couchées sur la paume (k = 1), pointes vers l'ennemi, en éventail ; k entre 0 et 1 : elles
    descendent en tournant depuis leur place au-dessus de la paume."""
    px, py = ctx['palm']
    rest = rest_cryst(ctx)
    lay = [((px + 0.5, py - 19.5), 72.0, 0.95), ((px + 4.0, py - 11.5), 86.0, 0.72), ((px + 1.5, py - 4.5), 100.0, 0.95)]
    out = []
    for i in range(3):
        x0, y0, a0, s0, _ = rest[i]
        (x1, y1), a1, s1 = lay[i]
        t = ease(k)
        # la descente en tournant : une petite boucle (jamais en ligne droite)
        sw = math.sin(math.pi * t) * (3.0 if i != 1 else 2.0)
        out.append((x0 + (x1 - x0) * t - sw, y0 + (y1 - y0) * t, a0 + (a1 - a0) * t, s0 + (s1 - s0) * t))
    return out


def needle_path(j, ctx0):
    """La course de l'aiguille j : de la paume à l'ennemi, en arc léger (comme le pixel art)."""
    px, py = ctx0['palm']
    p0 = (px + 8, py - [19.5, 11.5, 4.5][j])
    p1 = (FOE[0] - 4, FOE[1] + [-9, 0, 8][j])
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + [-12, -7, -3][j])
    return lambda t: bezq(p0, mid, p1, t)


_CTX0 = {}


def fx_attack(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        if 'palm' not in _CTX0:
            # la paume à l'instant du lancer (la respiration est alors effacée : toujours la même place)
            k = keyed(ATTACK, NEEDLE_GO)
            P0 = dict(k)
            P0['hand'] = (P0.pop('hx'), P0.pop('hy'))
            P0['head'] = (P0.pop('headx'), P0.pop('heady'))
            _CTX0['palm'] = C.build(pose=P0).ctx['palm']
        # 1) les cristaux descendent sur la paume en tournant, se couchent ; la brume s'enroule autour
        if tl < NEEDLE_GO + 10:
            k = clamp(tl / 300)
            for i, (x, y, a, s) in enumerate(needle_spec(ctx, k)):
                L = C.CRY0[i][1] * s
                W = C.CRY0[i][2] * (s if i != 1 else 0.78)
                front.append(crystal(fig, (x, y), L, W, a))
            px, py = ctx['palm']
            ph = tl / 1000 * 7
            pts = [(px + 3 + 10 * math.cos(ph + 2.4 * t) * (1 - 0.3 * t), py - 11 - 7 * math.sin(ph + 2.4 * t) * (1 - 0.3 * t)) for t in [i / 16 for i in range(17)]]
            back.append(frost(fig, pts, 2.4, op=0.85 * ease(tl / 200)))
            if tl > 200:
                front.append(snow(fig, px - 8, py - 17 - 0.01 * tl, 0.9))
                front.append(snow(fig, px + 14, py - 2, 0.7))
        # 2) les aiguilles volent, l'une après l'autre, chacune avec sa traîne de givre qui ondule
        for j in range(3):
            t0 = NEEDLE_GO + 26 * j
            t = (tl - t0) / 165.0
            if 0 <= t <= 1:
                at = needle_path(j, _CTX0)
                c = at(ease(t) * 0.25 + t * 0.75)
                q = at(min(1, t + 0.02))
                p_ = at(max(0, t - 0.02))
                ang = math.degrees(math.atan2(q[0] - p_[0], -(q[1] - p_[1])))
                tr = [at(max(0.0, t - 0.014 * i)) for i in range(18)]
                tr = [(x, y + 1.2 * math.sin(i * 0.7 + j * 2.0) * (i / 18)) for i, (x, y) in enumerate(tr)][::-1]
                back.append(frost(fig, tr, 2.6, op=0.9, head=0.75))
                L = [14.5, 18.6, 14.5][j] * (1.25 if t < 0.25 else 1.0)
                front.append(crystal(fig, c, L, [5.2, 6.2, 5.2][j], ang))
        # 3) la fleur de glace : plantée, elle éclate, les éclats retombent, la brume se défait
        hit = NEEDLE_GO + 26 * 2 + 165
        tb = tl - (NEEDLE_GO + 165)
        if tb > 0:
            c = FOE
            k0 = env(tb, 0, 40, 170, 260)
            if k0 > 0:
                back.append(mist(fig, c[0] - 2, c[1], 9 * (0.6 + 0.4 * k0), op=0.9 * k0, seed=1))
                for (a, L) in ((155, 22), (115, 16), (195, 17), (225, 12), (70, 12), (265, 10), (20, 9)):
                    r_ = math.radians(a)
                    s = 0.5 + 0.5 * ease(tb / 60)
                    cc = (c[0] + 0.45 * L * s * math.cos(r_), c[1] - 0.45 * L * s * math.sin(r_))
                    front.append(crystal(fig, cc, L * s, max(4, L * 0.42) * s, 90 - a, op=k0))
            tk = tb - 150
            if tk > 0:
                fade = 1 - ease((tk - 260) / 200)
                back.append(mist(fig, c[0] - 1, c[1] - 0.01 * tk, 9 + 0.03 * tk, op=0.85 * fade * ease(tk / 60), seed=3))
                for i in range(9):
                    a = math.radians(40 * i + 15 + 9 * math.sin(i * 3.1))
                    d = (8 + 0.075 * tk) * (0.75 + 0.3 * ((i * 7) % 4) / 3)
                    fall = 0.00012 * tk * tk
                    q = (c[0] + d * math.cos(a), c[1] - d * math.sin(a) + fall)
                    front.append(crystal(fig, q, 7 + (i % 3) * 1.6, 3.6 + (i % 2) * 0.6, math.degrees(-a) + 90 + tk * 0.4 * (1 if i % 2 else -1), op=fade))
                for i, (dx, dy) in enumerate(((-26, -10), (-14, -24), (10, -20), (-30, 10))):
                    front.append(snow(fig, c[0] + dx * (1 + tk / 600), c[1] + dy + tk * 0.02, 1.0, op=fade))
        # 4) trois cristaux renaissent au-dessus de la paume : des étincelles, puis de petits cristaux qui grandissent
        if tl >= 760:
            g = ease((tl - 820) / 260)
            rc = rest_cryst(ctx)
            for i, (x, y, a, s, _) in enumerate(rc):
                if g <= 0.02:
                    front.append(flake(fig, x, y + 3, 1.6 if i == 1 else 1.1, op=ease((tl - 760) / 60)))
                else:
                    front.append(crystal(fig, (x, y + 3 * (1 - g)), C.CRY0[i][1] * (0.35 + 0.65 * g), C.CRY0[i][2] * (0.4 + 0.6 * g), a))
        _ = hit
    return f


# ---- la spéciale d'équipe

SP_ORB = dict(
    mix=[(0, 0), (250, 0), (340, 1), (1470, 1), (1590, 0)],
    ang=[(250, -250), (360, -230), (570, -120), (650, -75), (870, 10), (970, 60), (1080, 100), (1200, 135), (1330, 210), (1470, 230)],
    rx=[(250, 40), (360, 44), (570, 48), (870, 50), (1200, 49), (1330, 46), (1470, 40)],
    ry=[(250, 15), (360, 17), (570, 20), (1200, 20), (1330, 17), (1470, 16)],
    lit=[(0, 0), (500, 0), (570, 1), (700, 1), (760, 2), (1080, 2), (1200, 1), (1400, 1), (1470, 0)],
    halo=[(0, 0), (500, 0), (570, 3), (650, 3.5), (720, 5.5), (970, 4.5), (1080, 3.5), (1200, 2.5), (1330, 0)],
    lift=[(0, 0), (120, 3.5), (250, 11), (1470, 11), (1590, 10), (1710, 4.5), (1850, 1.5), (2020, 0)],
)


def orbit_pos(a, rx, ry, c=HC):
    r = math.radians(a)
    return (c[0] + rx * math.cos(r), c[1] - ry * math.sin(r)), math.sin(r) > 0.0


def helix_pts(t0, t1, n=90):
    """La route du tourbillon de flocons : il sort des lèvres, descend en spirale autour d'elle et finit au sol."""
    out = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = math.radians(-22 - 470 * t)
        r = 14 + 26 * min(1.0, t / 0.3) ** 0.8
        yc = 42 + (GR - 9 - 42) * t
        out.append((FEET_X + r * math.cos(a), yc - 0.3 * r * math.sin(a), math.sin(a) > 0.05))
    return out


def split_runs(pts):
    runs, cur, side = [], [], None
    for x, y, bk in pts:
        if side is None or bk == side:
            cur.append((x, y))
        else:
            if len(cur) >= 2:
                runs.append((side, cur))
            cur = [cur[-1], (x, y)] if cur else [(x, y)]
        side = bk
    if len(cur) >= 2:
        runs.append((side, cur))
    return runs


SHARDS = [((3, -210), 0.00), ((-98, -190), 0.02), ((100, -186), 0.03), ((-128, -100), 0.05), ((126, -96), 0.06),
          ((-70, -58), 0.08), ((72, -62), 0.09), ((-60, -3), 0.10), ((64, -3), 0.12)]


def fx_special(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        mix = curve(SP_ORB['mix'], tl)
        a0 = curve(SP_ORB['ang'], tl)
        rx, ry = curve(SP_ORB['rx'], tl), curve(SP_ORB['ry'], tl)
        lit = curve(SP_ORB['lit'], tl)
        hal = curve(SP_ORB['halo'], tl)
        lift = curve(SP_ORB['lift'], tl)
        rest = rest_cryst(ctx, lift=(lift * 0.85, lift, lift * 0.85), dx=(-0.3 * lift, 0, 0.3 * lift))
        # l'aura givrée qui monte de toute sa silhouette (derrière elle)
        au = curve([(0, 0), (690, 0), (760, 3), (970, 3), (1080, 2.2), (1200, 1.8), (1330, 0.8), (1420, 0)], tl)
        if au > 0.05:
            ph = tl / 1000 * 9
            bases = [(52, 22, 9, -0.25), (60, 13, 10, -0.1), (70, 11, 11, 0.0), (80, 14, 9, 0.12), (86, 26, 8, 0.2),
                     (46, 56, 8, -0.35), (90, 54, 7, 0.3), (44, 84, 7, -0.3), (88, 84, 6, 0.25), (104, 46, 6, 0.3),
                     (40, 104, 6, -0.25), (90, 106, 5, 0.2)]
            for i, (x, y, w, ln) in enumerate(bases):
                h = au * (5.5 + 2.4 * math.sin(ph + i * 1.7) + 1.6 * math.sin(0.45 * ph + i * 2.9)) * (1.25 if y < 30 else 1.0)
                back.append(tongue(fig, (x, y + 4), h, w * (0.7 + 0.1 * au), lean=ln * 0.4, wob=math.sin(ph * 1.3 + i), op=min(1, au)))
        # la neige de l'air converge vers elle (l'inspiration)
        g = env(tl, 420, 520, 640, 720)
        if g > 0:
            k = clamp((tl - 420) / 300)
            for j in range(10):
                a = math.radians(j * 36 + 25 + 60 * k)
                r = (60 - 26 * k) * (0.8 + 0.25 * (j % 3) / 2)
                x, y = HC[0] + 4 + r * math.cos(a), HC[1] + 14 - 0.6 * r * math.sin(a)
                lay = back if math.sin(a) > 0 else front
                lay.append(flake(fig, x, y, 1.4, op=g, rot=20 * j + 90 * k) if j % 2 == 0 else snow(fig, x, y, 0.9, op=g))
        # les cristaux : au-dessus de la paume (ils s'élèvent), puis la ronde autour d'elle
        for i in range(3):
            (ox, oy), behind = orbit_pos(a0 + 120 * i, rx, ry)
            x0, y0, ang0, s0, _ = rest[i]
            x, y = x0 + (ox - x0) * mix, y0 + (oy - y0) * mix
            behind = behind and mix > 0.5
            spin = (a0 + 120 * i) * 0.35 * mix
            ang = ang0 * (1 - mix) + 12 * math.sin(math.radians(spin)) * mix
            lay = back if behind else front
            if hal > 0.1:
                lay.append(halo(fig, (x, y), hal * (1.6 if i == 1 else 1.15) * 1.6, op=0.65))
            depth = 1.0 - (0.12 * mix if behind else 0.0)
            lay.append(crystal(fig, (x, y), C.CRY0[i][1] * depth, C.CRY0[i][2] * depth, ang, lit=lit))
        # le souffle : une bouffée aux lèvres, puis le tourbillon de flocons qui descend en spirale jusqu'au sol
        mx, my = ctx['mouth']
        pu = env(tl, LAUNCH - 20, LAUNCH + 20, 900, 1000)
        if pu > 0:
            pts = [(mx + 2 + 4 * math.cos(math.radians(150 - 280 * t)) * (0.6 + 0.4 * t) + 4 * t, my + 1 - 3 * math.sin(math.radians(150 - 280 * t)) * (0.6 + 0.4 * t))
                   for t in [i / 14 for i in range(15)]]
            front.append(frost(fig, pts, 2.2, op=pu))
        hh = clamp((tl - LAUNCH) / 220)
        ht = clamp((tl - LAUNCH - 160) / 300)
        if hh > ht + 0.02 and tl < 1250:
            pts = helix_pts(ht, hh)
            fade = 1 - ease((tl - 1050) / 200)
            for side, run in split_runs(pts):
                (back if side else front).append(frost(fig, run, 4.0 * (0.4 + 0.6 * (len(run) / len(pts))), op=fade,
                                                       tones=('#ffffff', '#c8f6ff', '#5ccaee')))
            for j in range(9):
                x, y, bk = pts[int((j * 0.37 + 0.11) % 1 * (len(pts) - 1))]
                (back if bk else front).append(flake(fig, x + 2 * math.sin(j), y + 1.5 * math.cos(j * 2), 1.3, op=fade, rot=tl * 0.3 + 40 * j)
                                               if j % 3 == 0 else snow(fig, x + 2 * math.sin(j), y - 1.5, 0.8, op=fade))
        # l'anneau de flocons posé au sol tout autour d'elle, qui s'élargit puis se défait en neige
        rr = curve([(0, 0), (800, 0), (880, 34), (970, 42), (1080, 56), (1200, 68), (1330, 74), (1470, 78)], tl)
        thin = curve([(0, 0), (1080, 0), (1200, 0.3), (1330, 0.75), (1470, 1)], tl)
        if rr > 1 and thin < 0.98:
            spin = curve([(800, 40), (970, 110), (1080, 180), (1200, 245), (1470, 330)], tl)
            ryy = 0.22 * rr
            c = (FEET_X, GR - 0.6 - ryy * 0.4)
            op = (1 - thin) * ease((tl - 800) / 80)
            for (off, Lr, wv, tones) in ((0, 230, 5.0, ('#ffffff', '#dfe6fb', '#a6aee4')), (180, 190, 3.4, ('#ffffff', '#c8f6ff', '#5ccaee'))):
                L_ = Lr * (1 - 0.6 * thin)
                pts = []
                for i in range(41):
                    a = math.radians(spin + off - L_ + L_ * i / 40)
                    pts.append((c[0] + rr * math.cos(a), c[1] - ryy * math.sin(a), math.sin(a) > -0.05))
                for side, run in split_runs(pts):
                    (back if side else front).append(frost(fig, run, wv * (1 - 0.6 * thin) * (0.5 + 0.5 * len(run) / 41), op=op, tones=tones))
            for j in range(12):
                a = j * 30 + spin * 0.6 + 11 * (j % 2)
                (x, y), bk = orbit_pos(a, rr * (0.92 + 0.12 * (j % 3) / 2), ryy, c)
                y -= 2 + 3 * ((j * 7) % 4) + 6 * thin * (1 + j % 2)
                lay = back if bk else front
                lay.append(flake(fig, x, y, 1.3, op=1 - thin, rot=spin + 30 * j) if j % 3 == 2 else snow(fig, x, y, 0.9, op=1 - thin))
        # les éclats de cristal partent en gerbe dans toutes les directions (tout de lumière, petite traîne courbe)
        ts = (tl - LAUNCH) / 420.0
        if 0 < ts < 1.3:
            for i, ((tx, ty), dl) in enumerate(SHARDS):
                t = (ts - dl) / 1.0
                if t <= 0 or t > 1.15:
                    continue
                (mx_, my_), _ = orbit_pos(10 + 120 * (i % 3), 50, 20)
                M = (mx_, my_ - 4)
                T_ = (HC[0] + tx, HC[1] + 30 + ty)
                p1 = (M[0] + 0.12 * (T_[0] - M[0]), M[1] - 40)
                p2 = (M[0] + 0.78 * (T_[0] - M[0]), min(M[1] - 34, M[1] + (T_[1] - M[1]) * 0.55 - 26))
                tt = min(1.0, t)
                at = lambda u: bezc(M, p1, p2, T_, u)  # noqa: E731
                c = at(tt)
                q, p_ = at(min(1, tt + 0.02)), at(max(0, tt - 0.02))
                ang = math.degrees(math.atan2(q[0] - p_[0], -(q[1] - p_[1])))
                op = 1 - ease((t - 0.85) / 0.3)
                tr = [at(max(0.0, tt - 0.025 * k)) for k in range(10)][::-1]
                lay = back if i in (5, 6) else front
                lay.append(frost(fig, tr, 1.8, op=op * 0.9, tones=('#ffffff', '#c8f6ff', '#5ccaee'), head=0.8))
                lay.append(shard(fig, c, 8.5 if i < 7 else 9.5, ang, op=op))
        # la lumière glacée posée un instant sur elle au lancement
        fl = env(tl, LAUNCH - 10, LAUNCH + 20, LAUNCH + 90, LAUNCH + 260)
        if fl > 0:
            front.append('<ellipse cx="%s" cy="%s" rx="40" ry="62" fill="%s"/>' % (fm(68), fm(62), g_rad(fig, (68, 62), 40, [
                (0, '#ffffff', 0.38 * fl), (0.6, '#c8f6ff', 0.22 * fl), (1, '#c8f6ff', 0)], ry=62)))
        # la neige retombe doucement quand tout se défait
        fz = env(tl, 1250, 1360, 1600, 1900)
        if fz > 0:
            for j in range(10):
                x = 30 + 8.4 * j + 3 * math.sin(j * 2.3 + tl / 300)
                y = 20 + ((j * 37) % 70) + (tl - 1250) * 0.035
                front.append(snow(fig, x, y, 0.8 + 0.2 * (j % 2), op=fz))
    return f


# ---- la respiration : souffle de givre à l'expiration, reflet qui glisse sur le grand cristal, flocons qui tombent

def fx_idle(T):
    def f(fig, ctx):
        u = (T % IDLE_T) / IDLE_T
        front = fig.fx_front
        # le souffle de givre : à l'expiration, il sort des lèvres, monte et s'enroule
        k = (u - 0.58) / 0.36
        if 0 <= k <= 1:
            mx, my = ctx['mouth']
            op = env(k, 0, 0.2, 0.6, 1.0)
            pts = [(mx + 2.5 + 5 * t + 3.4 * math.cos(math.radians(200 - 300 * t)) * t, my - 1 - 7 * k * t - 3.4 * math.sin(math.radians(200 - 300 * t)) * t)
                   for t in [i / 14 for i in range(15)]]
            front.append(frost(fig, pts, 1.6 + 0.6 * k, op=0.85 * op))
        # le reflet qui glisse sur le grand cristal
        k = (u - 0.06) / 0.32
        if 0 <= k <= 1 and P_CRY[0]:
            x, y, a, s, _ = P_CRY[0][1]
            L = C.CRY0[1][1] * s
            yy = y - L * 0.3 + L * 0.55 * k
            front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="%g" transform="rotate(-12 %s %s)"/>' % (
                fm(x + 1.0), fm(yy), fm(0.9), fm(2.6), 0.9 * env(k, 0, 0.2, 0.7, 1), fm(x + 1.0), fm(yy)))
        # deux flocons qui tombent lentement
        for j, (x0, ph) in enumerate(((108.0, 0.0), (93.0, 0.5))):
            v = (u + ph) % 1.0
            front.append(snow(fig, x0 + 2.0 * math.sin(2 * math.pi * v + j), 30 + 34 * v, 0.75, op=env(v, 0, 0.15, 0.75, 1)))
    return f


P_CRY = [None]


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
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 28 * k, fy - 3.0 * k, cx + 28 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    seq = [('idle', 2 * IDLE_T), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
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
    if act == 'attack':
        tl = (T - t0) * 1000
        P['cryst'] = None
        P['sparks'] = 0.0
        if tl < 20 or tl > 1060:
            P['cryst'] = 'rest'
            P['sparks'] = 1.0 if tl > 1060 else 0.0
        fx = [fx_attack(tl)]
    elif act == 'special':
        tl = (T - t0) * 1000
        P['cryst'] = None
        P['sparks'] = 0.0 if 60 < tl < 1800 else 1.0
        if tl < 5 or tl > 1960:
            P['cryst'] = 'rest'
        fx = [fx_special(tl)]
    else:
        fx = [fx_idle(T)]

    def keep(fig, ctx):
        # la place du grand cristal (pour le reflet de la respiration)
        b = P['bob']
        W = ctx['W']
        c = C.CRY0[1][0]
        P_CRY[0] = (None, (c[0] + W[0] - C.W0[0], c[1] + W[1] - C.W0[1] + b[1], 0, 1.0, 0))
    return C.build(ow=ow, pose=P, fx=[keep] + fx, frame=view).svg()


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


def find_offset(sprite, frame):
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


SPRITE_FEET = (55, 104)          # les pieds dans l'image pixel de la pose (src/game/hd-figures.ts)


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées
    et la place du dessin de la pose dans ces images."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-celia-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'angels-1.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan de l'eau (Kesha), le pixel art à gauche et
    le vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kesha.webp')).convert('RGBA')
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
    _CTX0.clear()
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
        layer.paste(big, (round(feet[0] - (ox + SPRITE_FEET[0]) * SC), round(feet[1] - (oy + SPRITE_FEET[1]) * SC)), big)
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
        moments = [0.5, 1.6, a_s + 0.2, a_s + 0.34, a_s + 0.42, a_s + 0.5, a_s + 0.65, a_s + 0.8, a_s + 0.95,
                   s_s + 0.25, s_s + 0.5, s_s + 0.62, s_s + 0.78, s_s + 0.9, s_s + 1.05, s_s + 1.25, s_s + 1.5, s_s + 1.75]
        if len(sys.argv) > 2:
            moments = [float(x) for x in sys.argv[2:]]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 3
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(DBG, exist_ok=True)
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    _CTX0.clear()
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
