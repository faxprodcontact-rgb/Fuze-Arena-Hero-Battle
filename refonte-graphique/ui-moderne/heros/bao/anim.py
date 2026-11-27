# Bao vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/singe-chaman/build.py)
# — repos (il flotte sur son nuage), attaque de base « Bouffée de la gourde », attaque spéciale « Le grand souffle du
# sage » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/bao/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/bao/
#   python3 refonte-graphique/ui-moderne/heros/bao/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et d'Oboro, ../kael/anim.py, ../oboro/anim.py) : le dessin (bao.py) est fait de morceaux ;
# chaque image le redessine dans une POSE. C'est un VIEUX sage qui FLOTTE : tout monte et descend doucement avec son
# nuage, dont les bouffées gonflent par une vague qui court de gauche à droite ; le dos respire, la tête suit avec
# retard, la crosse de la queue traîne derrière le flottement, le bas de la barbe, le chapelet et les pans de la
# ceinture se balancent. Ses sorts partent de la GOURDE : il pousse le bâton vers l'ennemi (le bâton tourne autour de
# sa main, le haut part loin) et la gourde souffle. Les poses clés reprennent celles du pixel art (mêmes gestes, même
# rythme), reliées par des courbes douces sans dépassement. Les effets ont la palette du vent d'Eldra (blanc, cyan
# pâle, jade) et la crème et le lilas de son nuage : rubans de vent qui finissent en volute, bouffées, feuilles ; un
# seul contour, aucun flou SVG, jamais de rayons droits répétés.
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
import bao as K  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, sides, bez, f as fm  # noqa: E402
from lib import sparkle_shape  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'bao')
# les images de travail : dans le brouillon de la session si on le donne (BAO_TMP), sinon à côté du script
TMP = os.environ.get('BAO_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (16, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
GR = K.GRD
WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']
WINK = '#123c4a'                     # le contour des effets de vent (sarcelle très sombre)
CINK = '#5a4a7c'                     # le contour doux des bouffées de nuage (lilas sombre)
CREAM = ['#ffffff', '#fffbea', '#f8e6cc', '#d8c4d4', '#a08cb8']
HIT = (226.0, 82.0)                  # l'ennemi (le milieu de son corps), où les sorts éclatent

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


NUM = ['L', 'swell', 'lean', 'tilt', 's', 'glow', 'ro', 'bs', 'q', 'sash', 'eyes', 'beads', 'shut', 'headx', 'heady']


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# 2) L'attaque de base « Bouffée de la gourde » (pixel : ATTAQUE). Il ferme les yeux et se recule, ramène le bâton
# contre lui (la gourde s'éclaire, de petites volutes de vent s'y enroulent), puis pousse le bâton vers l'ennemi d'un
# coup sec en ouvrant les yeux : la gourde lâche une bouffée de nuage enroulée de vent, qui file en ondulant vers la
# droite et éclate sur l'ennemi en volutes et en feuilles. Il revient en garde.
ATTACK = [
    (0, {}),
    (140, dict(L=1.0, lean=-1.0, head=(-0.4, 0.4), s=-3.0, glow=0.8, ro=-3, bs=0.8, q=2.0, sash=0.6, shut=1)),
    (360, dict(L=2.0, lean=-2.2, head=(-1.0, -0.6), tilt=-2, s=-6.5, glow=2.0, ro=-4, bs=1.6, q=4.0, sash=1.0, shut=1)),
    (440, dict(L=2.0, lean=-2.4, head=(-1.1, -0.7), tilt=-2.2, s=-7.0, glow=2.2, ro=-4, bs=1.8, q=4.4, sash=1.1, shut=1)),
    (500, dict(L=1.0, lean=2.6, head=(1.4, 0.6), tilt=2.2, s=9.5, glow=3.0, ro=4, bs=-1.8, q=-2.0, sash=-1.2, eyes=1)),
    (580, dict(L=0.4, lean=2.4, head=(1.4, 0.8), tilt=2.0, s=10.5, glow=2.4, ro=4.5, bs=-1.4, q=-3.0, sash=-1.0, eyes=1)),
    (700, dict(L=0.2, lean=1.6, head=(1.0, 0.4), tilt=1.0, s=8.0, glow=1.4, ro=2, bs=0.4, q=-1.0, sash=0.2, eyes=0.6)),
    (860, dict(L=0.6, lean=0.9, head=(0.5, 0.2), s=4.5, glow=0.8, ro=-1.5, bs=1.0, q=1.0, sash=0.6)),
    (1020, dict(L=0.8, lean=0.3, head=(0.0, 0.4), s=1.5, glow=0.3, ro=-1, bs=0.3, q=0.6)),
    (1200, {}),
]
AT_LAUNCH, AT_HIT = 500, 790           # la bouffée part de la gourde / éclate sur l'ennemi (ms)

# 3) L'attaque spéciale « Le grand souffle du sage » (pixel : SPECIALE). Il ferme les yeux et égrène son chapelet (les
# perles s'allument une à une) ; son nuage se gonfle et l'élève ; le vent s'enroule autour de lui et se fait avaler
# par la gourde, qui brille. Il se recule, puis pousse le bâton vers l'ennemi en ouvrant des yeux d'or : arrêt sur
# l'image, la gourde crache un grand nuage roulé de vent. Le nuage roule vers l'ennemi et s'ouvre sur lui en
# tourbillon (des rubans de vent qui tournent, des feuilles qui montent), puis se défait en volutes. Il redescend.
SPECIAL = [
    (0, {}),
    (180, dict(L=1.5, swell=0.5, head=(0, 0.6), ro=3, bs=0.6, q=1.0, shut=1, beads=1.0)),
    (360, dict(L=4.0, swell=1.1, head=(0, 0.4), ro=0, bs=1.2, q=2.4, sash=0.8, shut=1, beads=2.4, glow=0.6)),
    (540, dict(L=6.0, swell=1.6, head=(0, 0), ro=-2, bs=1.0, q=3.0, sash=1.0, shut=1, beads=3.8, glow=1.4)),
    (760, dict(L=7.0, swell=2.0, head=(0, -0.2), tilt=-1, ro=-1, bs=0.6, q=2.0, sash=0.6, shut=1, beads=5.0, glow=2.4)),
    (900, dict(L=7.0, swell=2.0, lean=-2.4, head=(-1.0, -0.8), tilt=-2.4, s=-7.5, ro=-4, bs=1.8, q=4.4, sash=1.2,
               shut=1, beads=5.0, glow=3.0)),
    (1020, dict(L=7.0, swell=2.0, lean=-2.6, head=(-1.1, -0.9), tilt=-2.6, s=-8.0, ro=-4, bs=2.0, q=4.6, sash=1.3,
                shut=1, beads=5.0, glow=3.0)),
    (1080, dict(L=6.4, swell=1.6, lean=3.2, head=(1.8, 0.8), tilt=2.6, s=12.0, ro=5, bs=-2.0, q=-2.6, sash=-1.4,
                eyes=1, beads=5.0, glow=3.0)),
    (1260, dict(L=6.0, swell=1.4, lean=2.8, head=(1.6, 0.8), tilt=2.2, s=12.5, ro=5, bs=-1.6, q=-3.2, sash=-1.2,
                eyes=1, beads=4.0, glow=2.2)),
    (1420, dict(L=5.2, swell=1.1, lean=1.8, head=(1.0, 0.4), tilt=1.0, s=9.0, ro=2, bs=0.2, q=-1.4, sash=0.2,
                eyes=0.6, beads=2.0, glow=1.2)),
    (1700, dict(L=4.0, swell=0.7, lean=1.0, head=(0.6, 0.2), s=6.0, ro=-1.5, bs=1.0, q=0.6, sash=0.8, glow=0.6)),
    (2000, dict(L=2.2, swell=0.3, lean=0.4, head=(0.2, 0.4), s=2.5, ro=-1, bs=0.4, q=1.4, sash=0.4)),
    (2350, {}),
]
SP_BLAST = 1080                        # la gourde crache le grand nuage
SP_ARRIVE = 1380                       # il s'ouvre sur l'ennemi (tourbillon)

# ======================================================================== le repos (en boucle)


IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la gourde d'or au bout du bâton s'allume lentement du dedans (le vent qu'elle a avalé), puis s'éteint.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(glow=1.4 * (0.5 - 0.5 * math.cos(u)))


def idle_offsets(T):
    """Le repos d'un vieux sage qui flotte : tout monte et descend doucement avec le nuage (2 px), le dos respire, la
    tête suit avec retard, la crosse de la queue traîne, la barbe, le chapelet et les pans se balancent en retard."""
    u = 2 * math.pi * T / IDLE_T
    lift = 1.0 - math.cos(u)                       # 0..2
    br = 0.5 - 0.5 * math.cos(u - 0.6)
    return dict(L=lift, breath=br, heady=-0.45 * math.sin(u - 1.1) + 0.2, headx=0.12 * math.sin(u - 1.3),
                tilt=0.5 * math.sin(u - 1.0), bs=0.8 * math.sin(u - 1.7), q=2.2 * math.sin(u - 1.4),
                sash=0.6 * math.sin(u - 1.9), ro=2.4 * math.sin(u + 0.8))     # la gourde : signe()


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath']
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['glow'] = P['glow'] + w * signe(T)['glow']
    P['cp'] = (T / IDLE_T) % 1.0
    blink = 1.0 if (w > 0.95 and 1.6 <= (T % IDLE_T) < 1.72) else 0.0
    P['blink'] = max(blink, 1.0 if P.pop('shut') > 0.5 else 0.0)
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def stroke_shape(center, widths):
    """Un ruban fermé le long d'une ligne, largeur donnée en chaque point (bouts pointus)."""
    left, right = sides(center, widths)
    pts = [center[0]] + left[1:-1] + [center[-1]] + right[1:-1][::-1]
    return sm(pts, sharp=(0, len(left) - 1), t=0.85)


def spiral(p, d, r0, turn, s, n=14):
    """Une volute : depuis p dans la direction d, elle s'enroule (s = +1 sens horaire à l'écran) sur `turn` degrés,
    le rayon diminuant de r0 à r0 × 0,35."""
    L = math.hypot(*d) or 1
    dx, dy = d[0] / L, d[1] / L
    nx, ny = (-dy * s, dx * s)
    C = (p[0] + nx * r0, p[1] + ny * r0)
    a0 = math.atan2(p[1] - C[1], p[0] - C[0])
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = a0 + s * math.radians(turn) * t
        r = r0 * (1 - 0.65 * t)
        out.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290):
    """Une rafale de vent : un ruban effilé le long d'une courbe, qui s'enroule en volute au bout (vent « à la
    chinoise »). tail : l'arrière s'efface (0..1)."""
    if op <= 0.02 or w < 0.15:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 18)
    d = (p3[0] - p2[0], p3[1] - p2[1])
    if curl > 0.3:
        c = c + spiral(p3, d, curl, turn, s, 14)
    n = len(c)
    i0 = int(tail * (n - 4))
    c = c[i0:]
    n = len(c)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        ws.append(max(0.08, w * (math.sin(math.pi * min(1, t * 1.25)) ** 0.8) * (1 - 0.55 * t)))
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(c, ws)
    core = stroke_shape(c, [x * 0.42 for x in ws])
    gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.35, WIND[2]), (0.7, WIND[1]), (1, WIND[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.1, op=op)


def curl(fig, c, r, a0, turn, w, op=1.0, cw=True, dark=False):
    """Une volute de vent qui s'enroule autour de c (a0 en degrés, sens horaire à l'écran si cw)."""
    if op <= 0.02 or r < 0.5:
        return ''
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (turn if cw else -turn) * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    ws = [max(0.06, w * math.sin(math.pi * min(1.0, 0.15 + t * 1.1)) * (1 - 0.5 * t)) for t in (i / n for i in range(n + 1))]
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(pts, ws)
    if dark:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (1, WIND[3])])
        return outlined([(sh, gr, 1)], w=1.0, op=op)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[2]), (1, WIND[1])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def ring_arc(fig, C, rx, ry, a0, a1, w, op=1.0, dark=False):
    """Un anneau de vent (un arc d'ellipse effilé aux deux bouts)."""
    if op <= 0.02:
        return ''
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.7) for i in range(25)]
    sh = stroke_shape(pts, ws)
    if dark:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
        return outlined([(sh, gr, 1)], w=1.0, op=op)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.8)], w=1.0, op=op)


def leaf(fig, x, y, a, s=1.6, op=1.0):
    """Une feuille de bambou qui tourbillonne (vert jade, nervure claire)."""
    if op <= 0.02:
        return ''
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.6, 0), P(-0.2, -0.75), P(1.6, 0), P(-0.2, 0.75)], sharp=(0, 2), t=0.9)
    vein = ribbon([P(-1.3, 0), P(0, -0.05), P(1.3, 0)], [0.05, 0.22 * s, 0.05])
    gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, '#b8f0a0'), (0.5, '#5cc070'), (1, '#2a7a5a')])
    return outlined([(sh, gr, 1), (vein, '#e6ffd0', 0.8)], ink='#173c34', w=0.9, op=op)


def twinkle(fig, x, y, R, op=1.0):
    """Une petite étincelle blanche (le vent qui brille), cœur clair."""
    if op <= 0.02:
        return ''
    sh = sparkle_shape(x, y, R, 0.3)
    return outlined([(sh, g_rad(fig, (x, y), R, [(0, '#ffffff'), (0.6, WIND[1]), (1, WIND[2])]), 1)], w=0.8, op=op)


def puff(fig, cx, cy, r, op=1.0, seed=0, hollow=0.0):
    """Une bouffée de nuage (crème, ombres lilas) : quelques boules sous un contour doux, éclairées en haut à droite.
    hollow : elle se défait (les boules s'écartent et rapetissent)."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.78, 0.28, 0.72), (-0.8, 0.3, 0.7), (0.22, -0.56, 0.64), (-0.4, -0.38, 0.52), (0.95, -0.3, 0.45)]
    J = J[:4 + seed % 3]
    balls = [(cx + r * dx * (1 + 0.6 * hollow), cy + r * dy * (1 + 0.6 * hollow), r * rr * (1 - 0.45 * hollow)) for dx, dy, rr in J]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.6, cy + r), [(0, CREAM[1]), (0.5, CREAM[2]), (1, CREAM[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), CINK, CINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.7"/>' % (
        fm(x + rr * 0.3), fm(y - rr * 0.45), fm(rr * 0.35), fm(rr * 0.18)) for x, y, rr in balls[:2])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, hi)


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté de « facing »."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.9 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper=0.0)
    out += outlined([(ring, WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


def arc_band(C, R, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper) if taper else w * math.sin(math.pi * t) ** 0.6
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.5)


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


def along(pts, s):
    s = max(0.0, min(1.0, s))
    x = s * (len(pts) - 1)
    i = min(len(pts) - 2, int(x))
    t = x - i
    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)


def cloud_ball(fig, c, r, spin, trail, op=1.0, big=False):
    """La bouffée du sort : une boule de nuage crème, un ruban de vent enroulé autour (qui tourne : spin, degrés),
    des rafales qui ondulent derrière elle (trail = longueur)."""
    cx, cy = c
    out = []
    if trail > 1:
        out.append(gust(fig, (cx - trail, cy + 1), (cx - trail * 0.65, cy - 7), (cx - trail * 0.3, cy + 6), (cx - r * 0.6, cy),
                        r * (0.75 if big else 0.95), curl=0, op=op))
        if big:
            out.append(gust(fig, (cx - trail * 0.9, cy - 6), (cx - trail * 0.55, cy - 13), (cx - trail * 0.25, cy - 10),
                            (cx - r * 0.5, cy - r * 0.6), r * 0.5, curl=0, op=op))
    out.append(puff(fig, cx, cy, r * 0.62, op=op, seed=1 if big else 0))
    out.append(curl(fig, (cx + 0.3, cy), r * 1.05, 200 + spin, 320, 1.6 + 0.12 * r, op=op))
    return ''.join(out)


# ---- l'attaque de base


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        g = ctx['gourd']
        # l'anticipation : de petites volutes de vent s'enroulent autour de la gourde, qui s'éclaire
        k = env(t, 60, 300, 460, 540)
        if k > 0:
            fig.fx_back.append(curl(fig, (g[0] + 0.5, g[1] + 0.5), 10 - 2 * k, 30 + 0.5 * t, 250, 2.0, op=k, cw=False))
            fig.fx_front.append(curl(fig, (g[0], g[1] + 1.5), 12 - 3 * k, 200 + 0.45 * t, 220, 2.2, op=k * 0.95, cw=False))
            fig.fx_front.append(twinkle(fig, g[0] + 6.5, g[1] - 7.5, 1.6 + 0.8 * k, op=k))
        # le départ : la gourde souffle (un éclat devant sa bouche, deux virgules de vent)
        e = env(t, AT_LAUNCH - 20, AT_LAUNCH, AT_LAUNCH + 40, AT_LAUNCH + 170)
        if e > 0:
            fig.fx_back.append(pop(fig, (g[0] + 8, g[1] - 1), 4.6 * (0.6 + 0.4 * e), facing=0, op=e))
            fig.fx_back.append(gust(fig, (g[0] + 2, g[1] + 5), (g[0] + 10, g[1] + 9), (g[0] + 18, g[1] + 7), (g[0] + 22, g[1] + 2),
                                    2.4, curl=2.4, s=-1, op=e))
            fig.fx_back.append(gust(fig, (g[0] + 2, g[1] - 6), (g[0] + 10, g[1] - 11), (g[0] + 18, g[1] - 10), (g[0] + 21, g[1] - 5),
                                    2.0, curl=2.2, s=1, op=e))
        # le vol : la bouffée file en ondulant vers l'ennemi
        if AT_LAUNCH <= t < AT_HIT:
            s = (t - AT_LAUNCH) / (AT_HIT - AT_LAUNCH)
            p0 = START['a']
            x = p0[0] + (HIT[0] - 4 - p0[0]) * s
            y = p0[1] + (HIT[1] - p0[1]) * s - 9 * math.sin(math.pi * s)
            fig.fx_front.append(cloud_ball(fig, (x, y), 5.6, 1.6 * (t - AT_LAUNCH), 26 * min(1, s * 3 + 0.3)))
        if t >= AT_HIT:
            impact_small(fig, t - AT_HIT)
    return f


def impact_small(fig, t):
    """La bouffée éclate sur l'ennemi : un éclat de vent, des volutes, des feuilles, une bouffée qui se défait."""
    x, y = HIT
    e0 = env(t, -1, 0, 60, 220)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (x, y), 8 * (0.6 + 0.5 * min(1, t / 60)), facing=180, op=e0))
    e1 = env(t, 20, 90, 240, 520)
    if e1 > 0:
        k = t / 520
        fig.fx_back.append(puff(fig, x + 1 + 3 * k, y - 2 - 8 * k, 6 * (0.9 + 0.3 * k), op=e1, seed=2, hollow=min(1, k * 1.4)))
        fig.fx_front.append(curl(fig, (x + 11 + 4 * k, y - 9 - 6 * k), 6, 90 + 200 * k, 300, 2.2, op=e1))
        fig.fx_front.append(curl(fig, (x - 9 - 4 * k, y + 8 - 3 * k), 5, 260 + 200 * k, 300, 2.0, op=e1, cw=False))
    for j, (vx, vy, a0) in enumerate(((-0.05, -0.05, 20), (0.05, 0.02, 120), (0.02, -0.07, 240), (-0.06, 0.03, 300))):
        e = env(t, 20, 80, 380, 620)
        if e > 0:
            tt = t - 20
            fig.fx_front.append(leaf(fig, x + vx * tt, y + vy * tt + 0.00004 * tt * tt, a0 + 0.9 * tt, 1.5, op=e))


# ---- la spéciale


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        g = ctx['gourd']
        L = ctx['lift']
        cx = 70.0
        gy = GR - L
        # le nuage se gonfle : des bouffées crème naissent à ses deux bouts (derrière lui, à sa hauteur)
        e = env(t, 80, 300, 1100, 1500)
        if e > 0:
            for (dx, dy, r, sd) in ((-41, -8, 4.6, 0), (-34, -3, 3.6, 1), (41, -7, 4.4, 2), (34, -2, 3.4, 0)):
                fig.fx_back.append(puff(fig, cx + dx * (0.9 + 0.1 * e), gy + dy, r * e, op=min(1, e * 1.4), seed=sd))
        # le vent se lève : un anneau qui tourne autour de lui et monte avec lui (le bout de devant passe devant)
        e = env(t, 160, 420, 960, 1120)
        if e > 0:
            lv = min(1.0, (t - 160) / 700)
            ry = 11 + 3 * lv
            C = (cx + 2, gy - 22 - 6 * lv)
            ph = 0.35 * t
            fig.fx_back.append(ring_arc(fig, C, 46, ry, 190 + ph % 40, 340 + ph % 40, 2.6 + 0.8 * lv, op=e, dark=True))
            fig.fx_front.append(ring_arc(fig, C, 46, ry, 20 + ph % 40, 150 + ph % 40, 3.0 + 0.8 * lv, op=e))
            # deux rafales qui montent de chaque côté, en volute
            k = env(t, 300, 520, 960, 1120)
            if k > 0:
                fig.fx_back.append(gust(fig, (cx - 44, gy - 4), (cx - 55, gy - 20), (cx - 47, gy - 40), (cx - 31, gy - 50),
                                        3.0, curl=3.4, s=1, op=k))
                fig.fx_front.append(gust(fig, (cx + 47, gy - 4), (cx + 57, gy - 16), (cx + 53, gy - 32), (cx + 41, gy - 42),
                                         2.8, curl=3.0, s=-1, op=k))
            # des feuilles qui montent en tournant autour de lui
            for i, (a0, h0) in enumerate(((0, 8), (130, 20), (250, 34), (60, 46))):
                a = math.radians(a0 + 0.4 * t)
                x = cx + 2 + 44 * math.cos(a)
                y = gy - h0 - 0.02 * (t - 160)
                lay = fig.fx_front if math.sin(a) > 0 else fig.fx_back
                lay.append(leaf(fig, x, y, a0 + 0.7 * t, 1.5, op=e))
        # le vent avalé : deux volutes s'enroulent vers la gourde, qui brille
        e = env(t, 520, 700, 1000, 1110)
        if e > 0:
            fig.fx_back.append(curl(fig, (g[0] + 0.5, g[1] + 0.5), 15 - 4 * e, 0.6 * t, 300, 2.8, op=e, cw=False))
            fig.fx_front.append(curl(fig, (g[0], g[1] + 1), 11 - 3 * e, 180 + 0.6 * t, 280, 2.3, op=e, cw=False))
            fig.fx_front.append(twinkle(fig, g[0] - 7, g[1] - 9, 2.4, op=e))
            fig.fx_front.append(twinkle(fig, g[0] + 9, g[1] + 6, 1.6, op=e * 0.9))
        # le grand moment : l'éclair blanc de vent, la gourde crache un grand nuage roulé entouré de rafales
        fl = env(t, SP_BLAST - 10, SP_BLAST, SP_BLAST + 40, SP_BLAST + 170)
        if fl > 0:
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(g[0]), fm(g[1]), fm(130), g_rad(
                fig, g, 130, [(0, '#ffffff', 0.85 * fl), (0.12, WIND[1], 0.55 * fl), (0.45, WIND[2], 0.16 * fl), (1, WIND[3], 0)])))
        e = env(t, SP_BLAST - 10, SP_BLAST + 10, SP_BLAST + 90, SP_BLAST + 200)
        if e > 0:
            gx, gy2 = g[0] + 10, g[1] + 2
            fig.fx_back.append(pop(fig, (gx + 2, gy2 - 1), 8 * e, facing=0, op=e))
            fig.fx_back.append(gust(fig, (gx - 4, gy2 + 8), (gx + 10, gy2 + 18), (gx + 28, gy2 + 18), (gx + 40, gy2 + 8),
                                    3.6, curl=3.6, s=-1, op=e))
            fig.fx_back.append(gust(fig, (gx - 4, gy2 - 8), (gx + 10, gy2 - 20), (gx + 26, gy2 - 22), (gx + 38, gy2 - 12),
                                    3.0, curl=3.2, s=1, op=e))
            # le recul du souffle : une petite bouffée derrière son nuage
            fig.fx_back.append(puff(fig, cx - 46, gy - 9, 4.4, op=e, seed=1))
        # le grand nuage roulé file vers l'ennemi
        if SP_BLAST <= t < SP_ARRIVE:
            s = (t - SP_BLAST) / (SP_ARRIVE - SP_BLAST)
            p0 = START['s']
            x = p0[0] + (HIT[0] - p0[0]) * s
            y = p0[1] + (HIT[1] + 2 - p0[1]) * s - 10 * math.sin(math.pi * s)
            fig.fx_front.append(cloud_ball(fig, (x, y), 7.5 + 2.5 * s, 1.4 * (t - SP_BLAST), 30 + 14 * s, big=True))
        if t >= SP_ARRIVE:
            storm(fig, t - SP_ARRIVE)
    return f


def tornado(fig, cx, base, hgt, wid, phase, fade=0.0):
    """Le tourbillon : deux larges rubans de vent enroulés en hélice autour d'un entonnoir (étroit en bas, large en
    haut) ; les morceaux qui passent derrière sont plus sombres et peints d'abord. phase (degrés) : l'hélice tourne ;
    fade (0..1) : il se défait par le bas, les rubans s'amincissent."""
    back, front = [], []
    for j in range(2):
        th0 = phase + 180 * j
        n = 60
        cur, side = [], None
        segs = []
        for i in range(n + 1):
            s = i / n
            y = base - 2 - s * hgt
            r = wid * (0.28 + 0.72 * s ** 0.85)
            th = math.radians(th0 + 400 * s)
            x = cx + r * math.cos(th) + 2.0 * math.sin(math.radians(phase * 0.7) + s * 3)
            fr = math.sin(th) > 0
            w = (1.6 + 4.2 * s) * (1 - 0.5 * fade)
            w *= max(0.0, min(1.0, (s - fade * 0.8) / 0.12)) if s > fade * 0.8 else 0.0
            w *= min(1.0, (1 - s) / 0.1)
            if side is None or fr == side:
                cur.append((x, y, w))
            else:
                segs.append((side, cur))
                cur = [cur[-1], (x, y, w)]
            side = fr
        segs.append((side, cur))
        for fr, pts in segs:
            if len(pts) < 3 or max(p[2] for p in pts) < 0.2:
                continue
            c = [(x, y) for x, y, _ in pts]
            ws = [max(0.05, w) for _, _, w in pts]
            ws[0] = ws[-1] = 0.05
            sh = stroke_shape(c, ws)
            if fr:
                core = stroke_shape(c, [x * 0.4 for x in ws])
                gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[2])])
                front.append(outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.2))
            else:
                gr = g_lin(fig, c[0], c[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
                back.append(outlined([(sh, gr, 1)], w=1.0, op=0.95))
    return back, front


def storm(fig, t):
    """Le nuage s'ouvre sur l'ennemi en tourbillon (t en ms depuis l'arrivée), puis se défait en volutes."""
    x, y = HIT
    base = GR
    # l'éclat
    e0 = env(t, -1, 0, 60, 240)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (x, y), 13 * (0.6 + 0.4 * min(1, t / 60)), facing=180, op=e0))
        fig.fx_front.append(puff(fig, x - 5, y - 6, 8 * (0.8 + 0.4 * min(1, t / 120)), op=e0, seed=2, hollow=min(1, t / 240)))
    grow = min(1.0, t / 180)
    fade = max(0.0, (t - 520) / 380)
    if t < 900:
        hgt = (44 + 14 * grow) * (0.4 + 0.6 * grow)
        wid = (14 + 6 * grow + 4 * fade)
        back, front = tornado(fig, x, base, hgt, wid, 0.75 * t, fade=min(0.95, fade))
        op = 1.0 - max(0.0, (t - 760) / 140)
        fig.fx_back.extend('<g opacity="%g">%s</g>' % (op, b) for b in back)
        fig.fx_front.extend('<g opacity="%g">%s</g>' % (op, f_) for f_ in front)
        # le nuage qui coiffe le tourbillon, et les bouffées qui roulent au sol
        top = base - hgt - 2
        fig.fx_back.append(puff(fig, x + 3 * math.cos(t / 150), top, (wid * 0.42) * (1 - 0.4 * fade), op=op, seed=3, hollow=fade * 0.7))
        fig.fx_back.append(puff(fig, x - wid * 0.62, top + 3, wid * 0.3 * (1 - 0.4 * fade), op=op, seed=4, hollow=fade * 0.7))
        fig.fx_back.append(puff(fig, x + wid * 0.66, top + 2, wid * 0.32 * (1 - 0.4 * fade), op=op, seed=5, hollow=fade * 0.7))
        fig.fx_back.append(puff(fig, x - 18 - 6 * fade, base - 5 - 4 * fade, (6 + 2 * grow) * (1 - 0.3 * fade), op=op * grow, seed=0, hollow=fade * 0.8))
        fig.fx_back.append(puff(fig, x + 20 + 6 * fade, base - 5 - 4 * fade, (5 + 2 * grow) * (1 - 0.3 * fade), op=op * grow, seed=1, hollow=fade * 0.8))
    # des feuilles qui montent en tournant autour du tourbillon
    for i, (a0, h0) in enumerate(((0, 10), (120, 24), (240, 38), (60, 50), (180, 62))):
        e = env(t, 40, 140, 600, 900)
        if e > 0:
            a = math.radians(a0 + 0.5 * t)
            lx = x + (16 + 2 * i) * math.cos(a)
            ly = base - h0 - 0.03 * t
            (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(leaf(fig, lx, ly, a0 + 0.8 * t, 1.6, op=e))
    # il se défait en volutes
    e = env(t, 600, 720, 860, 1000)
    if e > 0:
        k = (t - 600) / 400
        fig.fx_front.append(curl(fig, (x + 22, base - 70 - 6 * k), 6, 60 + 200 * k, 300, 2.0, op=e))
        fig.fx_front.append(curl(fig, (x - 24, base - 58 - 6 * k), 5, 120 + 200 * k, 300, 1.8, op=e, cw=False))
        fig.fx_front.append(twinkle(fig, x + 6, base - 80 - 8 * k, 2.0, op=e))


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael, Oboro et Eldra)."""
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


def shadow_layer(w, h, view, lift=0.0, floor_y=GR):
    """L'ombre douce au sol sous le nuage (elle rétrécit et pâlit quand il s'élève)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (69 - x0) * k
    s = max(0.6, 1 - lift / 22)
    sd.ellipse([cx - 42 * k * s, fy - 2.8 * k * s, cx + 42 * k * s, fy + 2.8 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 5.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.2),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.8)]
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
        if 'a' not in START:
            Ph, _ = pose_at(t0 + AT_LAUNCH / 1000.0, act, t0)
            g = K.build(pose=Ph).ctx['gourd']
            START['a'] = (g[0] + 9, g[1] - 1)
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 's' not in START:
            Ph, _ = pose_at(t0 + SP_BLAST / 1000.0, act, t0)
            g = K.build(pose=Ph).ctx['gourd']
            START['s'] = (g[0] + 18, g[1] + 2)
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
    n = int(round(total * FPS))
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.3, 2.6, a_s + 0.36, a_s + 0.5, a_s + 0.6, a_s + 0.7, a_s + 0.85, a_s + 1.0,
                            s_s + 0.3, s_s + 0.6, s_s + 0.85, s_s + 1.0, s_s + 1.1, s_s + 1.25, s_s + 1.45,
                            s_s + 1.6, s_s + 1.8, s_s + 2.0, s_s + 2.2, s_s + 2.4]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, fr[i][1]['L']))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, fr[i][1]['L']))
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
