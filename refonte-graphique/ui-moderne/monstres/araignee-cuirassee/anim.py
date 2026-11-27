# L'araignée cuirassée vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# araignee-cuirassee/build.py) — respiration, attaque de base « Coup de massue », attaque spéciale « Séisme de grenat »
# — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/araignee-cuirassee/anim.py            # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/araignee-cuirassee/anim.py --planche [instants en s]   # contrôle
#
# Méthode (celle de Kael et de Nyrra) : le dessin (araignee-cuirassee.py) est fait de morceaux ; chaque image le
# redessine dans une POSE. Un costaud : tout est lent et lourd, les impacts sont tenus. Le corps monte, se cabre ou
# plonge autour du bassin ; les pointes des pattes posées restent plantées et leurs os gardent leur longueur (le genou
# se replace, toujours plié du même côté) ; les deux pattes qui frappent (la « pilier » proche et la lointaine de
# devant) se lèvent très haut puis s'abattent comme deux massues ; l'abdomen se gonfle, les cristaux de grenat
# s'allument. Les poses clés reprennent celles du pixel art (mêmes gestes, même rythme, un peu étiré : K) et sont
# reliées par des courbes douces sans dépassement. Les effets (éclats de pierre, poussière, fissure, dalles et
# cristaux qui jaillissent du sol) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG,
# formes courbes, jamais de rayons droits.
import importlib
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
A = importlib.import_module('araignee-cuirassee')
from atelier import sm, ribbon, ellipse, rpoly, f as fm  # noqa: E402
from outils import cristal  # noqa: E402

ROOT = A.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', A.NOM)
TMP = os.environ.get('CUIRASSEE_TMP') or '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-araignee-cuirassee/images'
FPS = 24
VIEW = (-2, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael et Nyrra
VW, VH = 1280, 720
INK = '#1f1238'
SINK = '#4a3656'                     # le contour doux de la poussière
GR = A.GRD
STONE = ['#f0dcc4', '#d6bea8', '#927268', '#60484e', '#3c2a38']
GARC = ['#ffffff', '#ffb4bc', '#ec5a6e', '#b8284e', '#7a1840', '#3e1230']
K = 1.15                             # le rythme du pixel art, un peu étiré (plus fluide)

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


NUM = ['spx', 'spy', 'rot', 'sw', 'croc', 'glow', 'eyes',
       'pUp', 'pHigh', 'pMid', 'pHit', 'pOff', 'fUp', 'fHigh', 'fMid', 'fHit', 'fOff',
       'pTx', 'pTy', 'fTx', 'fTy']


def keyed(keys, t):
    ts = [k[0] * K for k in keys]
    return {n: monotone(ts, [k[1].get(n, 0.0) for k in keys], t) for n in NUM}


def up(**k):
    """Les deux pattes de frappe dans une pose donnée (mêmes poids pour la pilier et la lointaine)."""
    out = {}
    for name, w in k.items():
        out['p' + name] = w
        out['f' + name] = w
    return out


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) « Coup de massue » : il se ramasse ; il recule et se cabre (la tête monte), lève très haut ses deux pattes avant,
# crochets écartés, cristaux allumés ; il tient. Tout s'abat d'un coup (traînées de poussière) : les deux massues
# frappent le sol devant lui, la tête plonge, les crochets se referment ; impact tenu (éclat, cailloux, fissure,
# poussière sous les pointes et sous ses huit pieds). Retour lent, patte après patte.
ATTACK = [
    (0, {}),
    (140, dict(spy=1.0, sw=1.0)),
    (330, dict(spx=-3.0, spy=-0.4, rot=-5.5, sw=1.2, croc=1.0, glow=1.0, eyes=0.4, **up(Up=1.0))),
    (500, dict(spx=-4.0, spy=-0.8, rot=-7.0, sw=2.0, croc=2.0, glow=2.0, eyes=1.0, **up(High=1.0))),
    (780, dict(spx=-4.3, spy=-1.0, rot=-7.4, sw=2.0, croc=2.0, glow=2.0, eyes=1.0, **up(High=1.0))),
    (830, dict(spx=1.5, spy=1.0, rot=0.6, sw=0.6, croc=1.0, glow=1.2, eyes=0.8, **up(Mid=1.0))),
    (870, dict(spx=5.0, spy=2.6, rot=2.4, croc=0.0, glow=0.7, eyes=0.7, **up(Hit=1.0))),
    (1080, dict(spx=4.6, spy=2.2, rot=2.0, glow=0.4, eyes=0.5, **up(Hit=1.0))),
    (1200, dict(spx=3.6, spy=1.2, rot=1.0, glow=0.2, eyes=0.3, **up(Off=1.0))),
    (1330, dict(spx=2.0, spy=0.2, rot=0.3, pOff=0.25, fOff=0.45)),
    (1460, dict(spx=1.0, pTx=1.5, pTy=-2.2, fTx=2.0, fTy=-3.0)),
    (1600, dict(spy=0.8, fTx=0.8, fTy=-0.8)),
    (1780, {}),
]
AT_FALL, AT_HIT = 800 * K, 870 * K

# 3) « Séisme de grenat » : il s'écrase sur ses genoux (abdomen gonflé), les cristaux s'allument et pétillent ; il se
# cabre très haut, pattes avant dressées, et tient ; puis il abat tout son corps de pierre (arrêt sur image). La terre
# se fend devant lui et une ONDE de pierre court vers la droite : l'une après l'autre, des dalles et des cristaux de
# grenat jaillissent du sol puis s'effondrent en éclats et en poussière. Il se relève lourdement, patte après patte.
SPECIAL = [
    (0, {}),
    (120, dict(spy=1.0, sw=1.0, glow=1.0)),
    (310, dict(spx=-2.0, spy=3.6, rot=1.0, sw=2.0, glow=1.3, croc=1.0, eyes=0.5)),
    (480, dict(spx=-3.0, spy=-2.0, rot=-8.5, sw=1.0, glow=2.0, croc=2.0, eyes=1.0, **up(High=1.0))),
    (780, dict(spx=-4.0, spy=-2.8, rot=-9.5, sw=2.0, glow=2.0, croc=2.0, eyes=1.0, **up(High=1.0))),
    (830, dict(spx=2.0, spy=1.0, rot=0.6, sw=0.8, glow=2.0, croc=1.0, eyes=1.0, **up(Mid=1.0))),
    (880, dict(spx=5.0, spy=4.4, rot=2.6, glow=1.2, eyes=0.9, **up(Hit=1.0))),
    (1120, dict(spx=5.0, spy=4.0, rot=2.4, glow=1.0, eyes=0.8, **up(Hit=1.0))),
    (1530, dict(spx=4.2, spy=2.4, rot=1.6, glow=0.5, eyes=0.5, **up(Hit=1.0))),
    (1650, dict(spx=4.0, spy=1.8, rot=0.9, glow=0.3, eyes=0.3, **up(Off=1.0))),
    (1780, dict(spx=2.0, spy=0.8, rot=0.3, pOff=0.3, fOff=0.5)),
    (1910, dict(spx=1.0, pTx=1.5, pTy=-2.2, fTx=2.0, fTy=-3.0)),
    (2070, dict(spy=1.0, sw=1.0, fTx=0.6, fTy=-0.6)),
    (2280, {}),
]
SP_SPARK0, SP_FALL, SP_SLAM = 120 * K, 805 * K, 880 * K
# l'onde : les grappes (x au sol, moment du sommet en ms d'action, taille, cristal ou non)
WAVE = [(140.0, 1000, 1.0, 1), (164.0, 1090, 1.25, 0), (189.0, 1180, 1.45, 1), (214.0, 1270, 1.35, 0), (239.0, 1360, 1.2, 1)]

# ======================================================================== la respiration (en boucle)


def idle_offsets(T):
    """Il respire lentement et lourdement : l'abdomen se gonfle d'abord, puis tout le haut du corps monte (la tête avec
    un peu de retard : le corps bascule à peine) ; il expire et se tasse sur ses genoux. Les crochets s'écartent et se
    referment une fois ; un éclat court sur le grand cristal ; la patte lointaine de devant se replace (pointe levée,
    reposée) : jamais toutes les pattes ensemble."""
    per = 2.2
    u = 2 * math.pi * T / per
    br = 0.5 - 0.5 * math.cos(u - 0.5)
    sw = 0.5 - 0.5 * math.cos(u + 0.4)
    ph = (T % per) / per
    croc = 0.5 * math.sin(math.pi * min(1.0, max(0.0, (ph - 0.35) / 0.3))) ** 2
    lift = math.sin(math.pi * min(1.0, max(0.0, (ph - 0.6) / 0.3))) ** 2
    glint = ((T % 4.4) / 4.4 - 0.15) / 0.3
    return dict(breath=br, sw=0.8 * sw, rot=-0.5 * math.sin(u - 1.2), spy=0.35 * (0.5 - 0.5 * math.cos(u - 2.6)),
                croc=croc, fTx=0.8 * lift, fTy=-1.6 * lift, glint=glint)


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0] * K
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or {n: 0.0 for n in NUM}
    Q = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P = dict(breath=w * idl['breath'], sp=(Q['spx'], Q['spy']), rot=Q['rot'], sw=max(0.0, Q['sw']),
             croc=max(0.0, Q['croc']), glow=max(0.0, Q['glow']), eyes=max(0.0, min(1.0, Q['eyes'])),
             alt={'P': {'up': Q['pUp'], 'high': Q['pHigh'], 'mid': Q['pMid'], 'hit': Q['pHit'], 'off': Q['pOff']},
                  'F2': {'up': Q['fUp'], 'high': Q['fHigh'], 'mid': Q['fMid'], 'hit': Q['fHit'], 'off': Q['fOff']}},
             tw={'P': (Q['pTx'], Q['pTy']), 'F2': (Q['fTx'], Q['fTy'])},
             glint=idl['glint'] if w > 0.9 else -1.0)
    P['blink'] = 1.0 if (w > 0.95 and 1.5 <= (T % 3.4) < 1.62) else 0.0
    return P, tl


# ======================================================================== outils des effets


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=INK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def circ(cx, cy, r, n=16):
    return sm([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, 1 jusqu'à c, redescend jusqu'à d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        u = (t - a) / (b - a)
    elif t <= c:
        return 1.0
    else:
        u = 1 - (t - c) / (d - c)
    return u * u * (3 - 2 * u)


def hsh(i, k):
    """Un « hasard » fixe (même valeur à chaque image)."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


def stone(fig, x, y, r, k=0, op=1.0, rot=0.0):
    """Un éclat de pierre : un caillou anguleux mais adouci, éclairé en haut à droite, un seul contour."""
    if op <= 0.02 or r < 0.2:
        return ''
    shapes = [[(-1, -0.7), (0.3, -1.0), (1.0, -0.2), (0.7, 0.8), (-0.6, 0.9), (-1.1, 0.1)],
              [(-0.8, -0.9), (0.9, -0.7), (1.0, 0.5), (-0.2, 1.0), (-1.0, 0.3)],
              [(-1.0, -0.4), (-0.1, -1.0), (1.1, -0.5), (0.8, 0.7), (-0.5, 0.8)]][k % 3]
    a = math.radians(rot)
    pts = [(x + r * (p[0] * math.cos(a) - p[1] * math.sin(a)), y + r * (p[0] * math.sin(a) + p[1] * math.cos(a))) for p in shapes]
    sh = rpoly(pts, r * 0.3)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, STONE[0]), (0.45, STONE[1]), (1, STONE[3])])
    top = rpoly([pts[0], pts[1], pts[2], (x + r * 0.1, y - r * 0.1)], r * 0.2)
    return outlined([(sh, gr, 1), (top, STONE[0], 0.45)], w=1.1, op=op)


def shard(fig, x, y, r, op=1.0, rot=0.0):
    """Un éclat de grenat (losange effilé, une facette claire)."""
    if op <= 0.02 or r < 0.2:
        return ''
    a = math.radians(rot)

    def P(u, v):
        return (x + r * (u * math.cos(a) - v * math.sin(a)), y + r * (u * math.sin(a) + v * math.cos(a)))
    sh = sm([P(0, -1.5), P(0.6, 0), P(0, 1.1), P(-0.6, 0)], sharp=(0, 1, 2, 3), t=0.4)
    lt = sm([P(0, -1.5), P(0.6, 0), P(0.05, 0.1)], sharp=(0, 1, 2), t=0.4)
    return outlined([(sh, g_lin(fig, P(0.6, -1), P(-0.6, 1), [(0, GARC[2]), (1, GARC[4])]), 1), (lt, GARC[1], 0.9)],
                    ink='#2a0a20', w=0.9, op=op)


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière brun-gris : quelques boules sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#efe0d2'), (0.5, '#bba494'), (1, '#7e6676')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def flash(fig, c, r, op):
    if op <= 0.02:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(c[0]), fm(c[1]), fm(r), fm(r * 0.8), g_rad(fig, c, r, [(0, '#ffffff', 0.9 * op), (0.35, '#fff2dc', 0.55 * op), (1, '#f6e0c8', 0)]))


def pop(fig, c, r, facing=-90.0, op=1.0):
    """Un éclat d'impact (la pierre éclate) : un cœur et des lobes arrondis (plus gros vers « facing »), cœur blanc,
    bord ocre clair ; un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, [(0, '#ffffff'), (0.35, '#fff4e0'), (0.7, STONE[0]), (1, STONE[1])])
    return outlined([(circ(x, y, rr, 14), gr, 1) for x, y, rr in lobes], ink='#6a4a4e', w=1.3, op=op)


def crack(fig, x0, x1, level, op=1.0, seed=0, hot=0.0):
    """Le sol qui se fend (couché, vu de côté) : une fente sombre en fuseau le long du sol, une lèvre claire ; avec
    hot, une lueur grenat au fond. level 0..1 : la fente s'ouvre de x0 vers x1."""
    if op <= 0.02 or level <= 0.01 or x1 - x0 < 1:
        return ''
    xe = x0 + (x1 - x0) * level
    n = 10
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (xe - x0) * t
        pts.append((x, GR + 0.6 + 0.5 * (hsh(seed, i) - 0.5) * (1 - abs(2 * t - 1))))
    ws = [0.15] + [0.5 + 1.3 * math.sin(math.pi * i / n) * (1 - 0.3 * hsh(seed + 3, i)) for i in range(1, n)] + [0.12]
    sh = ribbon(pts, ws)
    out = ''
    if hot > 0.02:
        out += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm((x0 + xe) / 2), fm(GR + 0.6), fm((xe - x0) / 2 + 3), fm(3.2),
            fig.rad((x0 + xe) / 2, GR + 0.6, (xe - x0) / 2 + 3, 3.2, [(0, '#ff5a6a', 0.55 * hot * op), (1, '#ff5a6a', 0)]))
    core = ribbon(pts, [w * 0.45 for w in ws])
    out += '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
        op, sh.d(), '#2a1a2e', core.d(), '#ff6a7a' if hot > 0.3 else '#140a1a')
    return out


def smear(fig, pts, w, op=1.0, col=('#fff4e6', '#d8c4b4')):
    """Une traînée de vitesse : un ruban courbe effilé, clair, sous un contour doux."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    n = len(pts)
    ws = [w * (0.15 + 0.85 * math.sin(math.pi * (i / (n - 1)) ** 0.8)) for i in range(n)]
    ws[0], ws[-1] = 0.1, 0.1
    sh = ribbon(pts, ws)
    gr = g_lin(fig, pts[0], pts[-1], [(0, col[1], 0.2), (1, col[0], 0.95)])
    return '<g opacity="%g"><path d="%s" fill="%s" stroke="%s" stroke-width="0.9" stroke-opacity="0.5"/></g>' % (op, sh.d(), gr, SINK)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def slab(fig, bx, h, w, lean=0.0, seed=0, op=1.0, sink=0.0):
    """Une dalle de pierre soulevée, plantée dans le sol : deux faces (la droite éclairée), un sommet cassé."""
    if h < 0.8 or op <= 0.02:
        return ''
    g = GR + 1.0 + sink
    tl = (bx - w * 0.5 + lean, g - h * (0.8 + 0.14 * hsh(seed, 1)))
    tm = (bx - w * 0.06 + lean * 1.05, g - h)
    tr = (bx + w * 0.46 + lean * 0.95, g - h * (0.72 + 0.18 * hsh(seed, 2)))
    bl, bm, br_ = (bx - w * 0.55, g), (bx - w * 0.02, g + 0.4), (bx + w * 0.55, g)
    left = rpoly([bl, tl, tm, bm], 0.5)
    right = rpoly([bm, tm, tr, br_], 0.5)
    gl = g_lin(fig, tm, bl, [(0, STONE[2]), (1, STONE[3])])
    gr = g_lin(fig, tr, bm, [(0, STONE[0]), (1, STONE[2])])
    top = ribbon([tl, tm, tr], [0.1, 0.9, 0.1])
    return outlined([(left, gl, 1), (right, gr, 1), (top, '#fff2dc', 0.6)], w=1.3, op=op)


def prism(fig, x, h, w, lean, op=1.0, cut=0.0):
    """Un grand cristal de grenat qui sort du sol, comme ceux de son dos (le même prisme pointu) : facette gauche
    sombre, facette droite claire, arête blanche ; cut : brisé (il en reste 1 − cut)."""
    if h < 1.0 or op <= 0.02:
        return ''
    L = h * (1 - 0.6 * cut) + 2.0
    ang = math.degrees(math.atan2(lean, 1.0))
    a = math.radians(ang)
    base = (x, GR + 2.0)
    c = (base[0] + math.sin(a) * L / 2, base[1] - math.cos(a) * L / 2)
    sil, left, right, ridge, top, bot = cristal(c, L, w, ang, tip=0.28 if cut < 0.05 else 0.05)
    return outlined([(sil, g_lin(fig, top, bot, [(0, GARC[2]), (1, GARC[4])]), 1),
                     (left, g_lin(fig, top, bot, [(0, GARC[3]), (1, GARC[5])]), 1),
                     (right, g_lin(fig, top, bot, [(0, GARC[0]), (0.35, GARC[1]), (1, GARC[3])]), 1),
                     (ridge, '#fff0f2', 0.9)], ink='#2a0a20', w=1.3, op=op)


def glowball(fig, c, r, op):
    if op <= 0.02:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(c[0]), fm(c[1]), fm(r), fm(r), g_rad(fig, c, r, [(0, '#ffffff', op), (0.3, '#ffb4bc', 0.8 * op), (1, '#ec5a6e', 0)]))


# ======================================================================== les effets des deux attaques


def impact(fig, c, t, big=1.0, seed=0):
    """L'impact d'une massue au point c (au sol), t ms après : éclat, cailloux projetés en cloche, poussière.
    Rend (poussière, le reste) : toutes les poussières se posent avant tous les cailloux."""
    out_b, out_f = [], []
    if t < 0:
        return out_b, out_f
    out_f.append(flash(fig, (c[0], c[1] - 4), 14 * big, env(t, 0, 20, 60, 220)))
    out_f.append(pop(fig, (c[0], c[1] - 4 * big), 6.5 * big * (1 + t / 300), -90, env(t, 0, 10, 90, 230)))
    # les cailloux : en cloche, ils retombent et s'arrêtent au sol
    for i in range(6):
        vx = (hsh(seed + i, 1) - 0.42) * 70 * big
        vy = -(55 + 50 * hsh(seed + i, 2)) * big
        s = t / 1000
        x = c[0] + vx * s
        y = c[1] - 3 + vy * s + 0.5 * 260 * s * s
        if y > GR - 0.8:
            y = GR - 0.8
        op = env(t, 0, 30, 380, 560)
        out_f.append(stone(fig, x, y, (1.4 + 1.2 * hsh(seed + i, 3)) * big, i, op, rot=t * (0.4 if i % 2 else -0.4)))
    # la poussière : deux gros nuages qui s'ouvrent et retombent
    for i, dx in enumerate((-6, 6)):
        k = min(1.0, t / 260)
        out_b.append(dust(fig, c[0] + dx * (1 + k) * big, GR - 3 - 2 * k, (3.0 + 3.6 * k) * big, env(t, 0, 40, 260, 620)))
    return out_b, out_f


def feet_dust(fig, ctx, t, names, level=1.0):
    """Le sol tremble : une petite bouffée sous chaque pied posé."""
    out = []
    for i, nm in enumerate(names):
        tip = ctx['tips'][nm]
        k = min(1.0, t / 300)
        out.append(dust(fig, tip[0] + (hsh(i, 5) - 0.5) * 2, GR - 1.2 - k, (1.2 + 1.4 * k) * level, env(t, 0, 40, 200, 520)))
    return out


FEET_ALL = ['A', 'B', 'C', 'G1', 'G2', 'F1']


def fx_attack(tl):
    def f(fig, ctx):
        back, front = [], []
        # les traînées de la chute (de la pose haute vers le sol)
        a = env(tl, AT_FALL - 40, AT_FALL, AT_FALL + 30, AT_HIT + 60)
        if a > 0:
            for nm, (p0, p1, p2) in (('P', ((122, 40), (134, 52), (129, 116))), ('F2', ((146, 26), (156, 46), (150.5, 116)))):
                pts = bezier(p0, p1, (p2[0] + 4, p2[1] - 30), p2, 16)
                front.append(smear(fig, pts, 4.6, a * 0.7))
        t = tl - AT_HIT
        if t >= 0:
            b1, f1 = impact(fig, ctx['tips']['P'], t, 0.9, seed=3)
            b2, f2 = impact(fig, ctx['tips']['F2'], t - 20, 1.0, seed=11)
            front += b1 + b2 + f1 + f2
            front.insert(0, crack(fig, ctx['tips']['P'][0] - 6, ctx['tips']['F2'][0] + 12, min(1, t / 120), env(t, 0, 40, 500, 800), seed=4))
            front += feet_dust(fig, ctx, t, FEET_ALL, 0.9)
        fig.fx_back.extend(back)
        fig.fx_front.extend(front)
    return f


SPARK = [(35.0, 7.0), (16.0, 20.0), (52.0, 24.0), (83.0, 47.0), (75.0, 52.0)]


def fx_special(tl):
    def f(fig, ctx):
        back, front = [], []
        P = ctx['P']
        # les cristaux pétillent : de petites lueurs rondes et des éclats qui montent au-dessus des pointes
        sp = env(tl, SP_SPARK0, SP_SPARK0 + 150, SP_FALL - 60, SP_SLAM + 120)
        if sp > 0:
            from atelier import mapp
            for i, (x, y) in enumerate(SPARK):
                M = ctx['ABD'] if x < 60 else ctx['BODY']
                base = mapp(M, (x, y))
                for j in range(3):
                    ph = ((tl / 1000) * 1.6 + hsh(i, j)) % 1.0
                    c = (base[0] + (hsh(i, j + 7) - 0.5) * 6, base[1] - 1 - 9 * ph)
                    o = sp * math.sin(math.pi * ph)
                    front.append(glowball(fig, c, 1.8 + 0.6 * hsh(i, j), o))
                    if j == 0:
                        front.append(shard(fig, c[0], c[1], 0.9, o, rot=40 * ph))
        a = env(tl, SP_FALL - 40, SP_FALL, SP_FALL + 30, SP_SLAM + 60)
        if a > 0:
            for nm, (p0, p1, p2) in (('P', ((122, 34), (134, 46), (129, 116))), ('F2', ((148, 20), (158, 42), (150.5, 116)))):
                front.append(smear(fig, bezier(p0, p1, (p2[0] + 4, p2[1] - 30), p2, 16), 5.0, a * 0.7))
        t = tl - SP_SLAM
        if t >= 0:
            b1, f1 = impact(fig, ctx['tips']['P'], t, 1.0, seed=5)
            b2, f2 = impact(fig, ctx['tips']['F2'], t - 10, 1.1, seed=13)
            front += b1 + b2 + f1 + f2
            front += feet_dust(fig, ctx, t, FEET_ALL + ['P'], 1.2)
            # sous le corps qui s'écrase, une large poussière
            k = min(1.0, t / 300)
            for i, x in enumerate((30, 60, 90)):
                front.append(dust(fig, x + (i - 1) * 4 * k, GR - 2 - 2 * k, 3.2 + 3.0 * k, env(t, 0, 60, 280, 700) * 0.9))
            # la terre se fend devant lui, jusqu'au bout de l'onde
            back.append(crack(fig, 118.0, 252.0, min(1.0, t / 520), env(t, 0, 40, 900, 1300), seed=9, hot=env(t, 0, 80, 500, 1000)))
        # l'onde : des grappes de dalles et de cristaux qui jaillissent puis s'effondrent
        for i, (x, tp, s, cr) in enumerate(WAVE):
            tc = tl - tp * K
            rise = env(tc, -180, 0, 120, 330)
            if tc < -180 or tc > 900:
                continue
            crumble = min(1.0, max(0.0, (tc - 160) / 220))
            h = 18 * s * rise
            op = 1.0 if crumble < 0.6 else max(0.0, 1 - (crumble - 0.6) / 0.4)
            front.append(slab(fig, x - 5 * s, h * 0.75, 6.5 * s, -0.8, seed=i, op=op))
            front.append(slab(fig, x + 6 * s, h * 0.55, 5.5 * s, 0.9, seed=i + 7, op=op))
            if cr:
                front.append(prism(fig, x, h * 1.15, 5.0 * s, 0.12, op=op, cut=crumble))
            else:
                front.append(slab(fig, x + 0.5, h, 7.0 * s, 0.3, seed=i + 3, op=op))
            # les éclats et la poussière quand la grappe s'effondre
            if tc > 120:
                tt = tc - 120
                for j in range(5):
                    vx = (hsh(i, j) - 0.5) * 50
                    vy = -(40 + 40 * hsh(i, j + 3))
                    ss = tt / 1000
                    px = x + vx * ss
                    py = min(GR - 0.8, GR - h * 0.6 + vy * ss + 0.5 * 240 * ss * ss)
                    o = env(tt, 0, 30, 300, 520)
                    front.append(shard(fig, px, py, 1.1 * s, o, rot=tt * 0.5) if (j % 2 and cr) else stone(fig, px, py, 1.3 * s, j, o, rot=tt * 0.3))
                k = min(1.0, tt / 300)
                front.append(dust(fig, x, GR - 2 - 3 * k, (3 + 3.5 * k) * s, env(tt, 0, 60, 260, 620)))
        fig.fx_back.extend(back)
        fig.fx_front.extend(front)
    return f


# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael et Nyrra)."""
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
    # l'ombre douce au sol sous lui (entre les pointes des pattes)
    sh = Image.new('RGBA', (w, h))
    cx = (64 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 62 * k, fy - 3.4 * k, cx + 62 * k, fy + 3.4 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 4.4), ('attack', ATTACK[-1][0] * K / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] * K / 1000),
           ('idle', 1.2), ('special', SPECIAL[-1][0] * K / 1000), ('idle', 1.8)]
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
    return A.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
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
    n = int(round(total * FPS))
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.38, a_s + 0.6, a_s + 0.93, a_s + 1.0, a_s + 1.1, a_s + 1.3, a_s + 1.6,
                            s_s + 0.35, s_s + 0.7, s_s + 0.95, s_s + 1.02, s_s + 1.12, s_s + 1.3, s_s + 1.45,
                            s_s + 1.6, s_s + 1.8, s_s + 2.0, s_s + 2.3, s_s + 2.6]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(out)
        print('planche :', out)
        shutil.rmtree(TMP)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
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
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
