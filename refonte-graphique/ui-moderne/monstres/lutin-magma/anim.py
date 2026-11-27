# Le Lutin de magma vectoriel ANIMÉ : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/lutin-magma/build.py) — repos (souffle nerveux), attaque de base « Bond griffu »,
# attaque spéciale « Ruée de magma » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/lutin-magma/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/lutin-magma/)
#   python3 refonte-graphique/ui-moderne/monstres/lutin-magma/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et de Gribou) : le dessin (lutin-magma.py) est fait de morceaux ; chaque image le redessine
# dans une POSE. C'est une petite bête nerveuse : il ne marche pas, il BONDIT (comme une grenouille, jambes repliées
# en vol), griffe, et rebondit à sa place. Ses pieds restent au sol pendant qu'il se ramasse (genoux pliés autour des
# vraies jointures, recalculées à chaque image : outils.ik) ; ses deux bras sont replacés à chaque image (épaule →
# coude → poignet) et les mains suivent l'avant-bras. La tête suit avec retard, la mèche de flamme vit sans arrêt et
# file en arrière quand il fonce. Les effets ont la lave du lutin (blanc, jaune, orange, rouge), la fumée de Kael et
# sa roche : griffures en croissant, langues de flamme, braises, bouffées, éclats de roche, gouttes de lave ; un seul
# contour par objet, aucun flou SVG, jamais de rayons droits répétés.
import importlib.util
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
_spec = importlib.util.spec_from_file_location('lutin_magma', os.path.join(HERE, 'lutin-magma.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, resample, sides, bez, lock, f as fm  # noqa: E402
from lib import sparkle_shape  # noqa: E402
from outils import fused  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'lutin-magma')
TMP = os.environ.get('LUTIN_TMP') or os.path.join('/tmp', 'lutin-magma-anim')
FPS = 24
VIEW = (14, -24, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael et Gribou
VW, VH = 1280, 720
GR = K.GRD
LAVA = K.LAVA
FINK = '#4a0f12'                     # le contour des effets de feu (rouge très sombre)
SMOKE = ['#ece2de', '#beacb0', '#8a7684', '#604e60']      # la fumée de Kael (lumière → creux)
SINK = '#3a2a40'
HIT = (154.0, 97.0)                  # l'ennemi (le milieu de son corps), là où griffes et boule de feu éclatent

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


def ramp(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)


# ======================================================================== les effets (dessinés, un seul contour)


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def stroke_shape(center, widths):
    left, right = sides(center, widths)
    pts = [center[0]] + left[1:-1] + [center[-1]] + right[1:-1][::-1]
    return sm(pts, sharp=(0, len(left) - 1), t=0.85)


def arc_pts(C, R, a0, a1, n=28, ry=None):
    ry = R if ry is None else ry
    return [(C[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def crescent(fig, pts, w, op=1.0, head=1.0):
    """Une griffure de feu en croissant le long d'une courbe : pointue aux deux bouts, la plus large vers la griffe
    (le bout de la courbe), blanche à la griffe, jaune, orange, rouge à la queue. head < 1 : seul le début est tracé."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    n = max(3, int(len(pts) * head))
    c = pts[:n]
    m = len(c)
    ws = [max(0.05, w * math.sin(math.pi * min(1.0, (i / (m - 1)) * 0.85 + 0.08)) ** 0.8 * (0.35 + 0.65 * i / (m - 1))) for i in range(m)]
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(c, ws)
    core = stroke_shape(c, [x * 0.45 for x in ws])
    gr = g_lin(fig, c[0], c[-1], [(0, LAVA[4]), (0.4, LAVA[3]), (0.75, LAVA[2]), (1, LAVA[1])])
    gc = g_lin(fig, c[0], c[-1], [(0, LAVA[2]), (0.6, LAVA[1]), (1, '#ffffff')])
    return outlined([(sh, gr, 1), (core, gc, 0.95)], w=1.1, op=op)


def tongue(fig, base, h, w, lean=0.0, ph=0.0, op=1.0):
    """Une langue de flamme dressée (sol, griffes) : silhouette orange-rouge, coeur jaune, pointe qui ondule."""
    if op <= 0.02 or h < 0.6:
        return ''
    x, y = base
    tip = (x + lean * h + 0.35 * h * math.sin(ph), y - h)
    outer = lock((x, y), (x + 0.1 * h * math.sin(ph + 1), y - 0.35 * h), (x + lean * h * 0.6 - 0.2 * h * math.sin(ph), y - 0.7 * h), tip, w, bulge=0.4)
    inner = lock((x, y + 0.1), (x, y - 0.25 * h), (x + lean * h * 0.4, y - 0.45 * h), (x + lean * h * 0.55 + 0.15 * h * math.sin(ph), y - 0.62 * h), w * 0.55, bulge=0.3)
    base_b = ellipse(x, y, w * 0.5, w * 0.22)
    o = fused([outer, base_b], smooth=0.15)
    return outlined([(o, g_lin(fig, (x, y), tip, [(0, LAVA[2]), (0.5, LAVA[3]), (1, LAVA[4])]), 1),
                     (inner, g_lin(fig, (x, y), tip, [(0, '#ffffff'), (0.4, LAVA[1]), (1, LAVA[2])]), 1)], w=1.0, op=op)


def ember(fig, x, y, r, op=1.0):
    """Une braise : petite goutte de lumière (coeur blanc, bord orange), un contour rouge sombre."""
    if op <= 0.02 or r < 0.15:
        return ''
    sh = ellipse(x, y, r, r)
    return outlined([(sh, g_rad(fig, (x - r * 0.2, y - r * 0.2), r * 1.2, [(0, '#ffffff'), (0.45, LAVA[1]), (1, LAVA[3])]), 1)], w=0.7, op=op)


def spark(fig, x, y, R, op=1.0):
    if op <= 0.02 or R < 0.3:
        return ''
    sh = sparkle_shape(x, y, R, 0.28)
    return outlined([(sh, g_rad(fig, (x, y), R, [(0, '#ffffff'), (0.55, LAVA[1]), (1, LAVA[2])]), 1)], w=0.8, op=op)


def puff(fig, cx, cy, r, op=1.0, seed=0, hollow=0.0):
    """Une bouffée de fumée (gris-violet, comme celle de Kael) : quelques boules sous un contour doux, éclairées en
    haut à droite. hollow : elle se défait (les boules s'écartent et rapetissent)."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.78, 0.28, 0.72), (-0.8, 0.3, 0.7), (0.22, -0.56, 0.64), (-0.4, -0.38, 0.52), (0.95, -0.3, 0.45)]
    J = J[:4 + seed % 3]
    balls = [(cx + r * dx * (1 + 0.6 * hollow), cy + r * dy * (1 + 0.6 * hollow), r * rr * (1 - 0.45 * hollow)) for dx, dy, rr in J]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.6, cy + r), [(0, SMOKE[0]), (0.5, SMOKE[1]), (1, SMOKE[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.55"/>' % (
        fm(x + rr * 0.3), fm(y - rr * 0.45), fm(rr * 0.35), fm(rr * 0.18)) for x, y, rr in balls[:2])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, hi)


def chunk(fig, x, y, a, s=1.0, op=1.0):
    """Un éclat de roche du lutin (violet nuit), une fêlure de lave, la lumière en haut à droite."""
    if op <= 0.02:
        return ''
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.4, -0.6), P(-0.2, -1.4), P(1.5, -0.8), P(1.2, 0.9), P(-0.6, 1.2)], sharp=(0, 1, 2, 3, 4), t=0.5)
    vein = ribbon([P(-0.8, 0.2), P(0.1, -0.2), P(0.9, 0.3)], [0.05, 0.35 * s, 0.05])
    gr = g_lin(fig, P(1.4, -1.4), P(-1.2, 1.2), [(0, K.ROCK.light), (0.5, K.ROCK.base), (1, K.ROCK.shadow)])
    return outlined([(sh, gr, 1), (vein, LAVA[2], 1)], ink='#1f1238', w=0.8, op=op)


def drop(fig, x, y, vx, vy, s=1.0, op=1.0):
    """Une goutte de lave qui vole (pointe tournée vers l'arrière de son mouvement)."""
    if op <= 0.02:
        return ''
    a = math.atan2(vy, vx)
    c, si = math.cos(a), math.sin(a)
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-2.2, 0), P(0, -0.8), P(0.9, 0), P(0, 0.8)], sharp=(0,), t=0.9)
    return outlined([(sh, g_lin(fig, P(1, 0), P(-2, 0), [(0, '#ffffff'), (0.4, LAVA[1]), (1, LAVA[3])]), 1)], w=0.7, op=op)


def fireball(fig, c, r, spin, op=1.0, hollow=0.0):
    """La boule de feu de la spéciale : un coeur rond, quatre langues de feu tourbillonnantes de tailles inégales
    (pas de rayons), coeur blanc ; hollow : elle se défait en fumée (le coeur pâlit, les langues s'amincissent)."""
    if op <= 0.02 or r < 0.5:
        return ''
    shapes = [ellipse(c[0], c[1], r * 0.62, r * 0.62)]
    for i, (k, w) in enumerate(((1.0, 0.62), (0.78, 0.5), (0.92, 0.56), (0.66, 0.46))):
        a0 = math.radians(spin + i * 90 + (8 if i % 2 else -6))
        p0 = (c[0] + r * 0.35 * math.cos(a0), c[1] + r * 0.35 * math.sin(a0))
        a1, a2 = a0 + 0.55, a0 + 1.15
        p1 = (c[0] + r * 0.8 * k * math.cos(a1 - 0.2), c[1] + r * 0.8 * k * math.sin(a1 - 0.2))
        p2 = (c[0] + r * 1.05 * k * math.cos(a2 - 0.3), c[1] + r * 1.05 * k * math.sin(a2 - 0.3))
        p3 = (c[0] + r * 1.25 * k * math.cos(a2 + 0.2), c[1] + r * 1.25 * k * math.sin(a2 + 0.2))
        shapes.append(lock(p0, p1, p2, p3, r * w * (1 - 0.4 * hollow), bulge=0.3))
    o = fused(shapes, smooth=0.2)
    inner = ellipse(c[0], c[1], r * 0.5 * (1 - 0.5 * hollow), r * 0.5 * (1 - 0.5 * hollow))
    hot = [(0, '#ffffff'), (0.35, LAVA[1]), (0.7, LAVA[2]), (1, LAVA[3])] if hollow < 0.5 else [(0, LAVA[1]), (0.6, LAVA[3]), (1, LAVA[4])]
    return outlined([(o, g_rad(fig, c, r * 1.3, [(0, LAVA[1]), (0.4, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])]), 1),
                     (inner, g_rad(fig, (c[0] + r * 0.1, c[1] - r * 0.1), r * 0.55, hot), 1)], w=1.2, op=op)


def glow(fig, c, r, color, op):
    """Une lueur ronde (dégradé radial, aucun flou)."""
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)]))


def scorch(fig, x0, x1, op=1.0):
    """L'empreinte de lave refroidie au sol (un trait rouge sombre posé sur la dalle)."""
    if op <= 0.02:
        return ''
    sh = ribbon([(x0, GR + 0.3), ((x0 + x1) / 2, GR + 0.6), (x1, GR + 0.3)], [0.1, 1.0, 0.1])
    return '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), '#7a281e', 0.85 * op)


# ======================================================================== les poses

NUM = ['Tx', 'Ty', 'bas', 'dosx', 'dosy', 'headx', 'heady', 'tilt', 'arrx', 'arry', 'nwrx', 'nwry', 'fwrx', 'fwry',
       'nha', 'fha', 'curl', 'trail', 'flare', 'rise', 'glow', 'burn', 'ear', 'shut']
NWR0, FWR0 = K.REST['nwr'], K.REST['fwr']


def flat(k):
    d = {n: 0.0 for n in NUM}
    d['nwrx'], d['nwry'] = NWR0
    d['fwrx'], d['fwry'] = FWR0
    for key, v in k.items():
        if key in ('T', 'dos', 'head', 'arr', 'nwr', 'fwr'):
            d[key + 'x'], d[key + 'y'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# 2) L'attaque de base « Bond griffu » (pixel : ATTAQUE). Il se ramasse (tassé, penché en arrière, la main levée tirée
# haut derrière, la mèche qui se dresse), courte attente, puis BONDIT vers l'ennemi, jambes repliées comme une
# grenouille, la mèche filant derrière ; en l'air il arme la griffe au-dessus de sa tête et l'abat en diagonale : une
# griffure de feu en croissant. Il retombe tassé sur l'ennemi : gerbe de flammes et de braises, tenue. Puis il rebondit
# en arrière (la mèche file vers l'avant) et retombe à sa place, tassé, dans un petit nuage.
ATTACK = [
    (0, {}),
    (110, dict(dos=(-2.2, 2.2), head=(-0.8, 1.0), bas=-3, fwr=(20, -8), nwr=(18, 14), rise=0.8, curl=0.2)),
    (300, dict(dos=(-3.2, 3.4), head=(-1.2, 1.6), tilt=-3, bas=-5, fwr=(20, -11), nwr=(16, 13), rise=1.3, curl=0.3, ear=1)),
    (370, dict(T=(16, -12), bas=-8, arr=(5, -6), head=(0.4, 0), fwr=(20, -14), nwr=(19, 9), trail=1.4, curl=0.2)),
    (440, dict(T=(34, -18), bas=-2, arr=(8, -9), head=(0.8, 0), fwr=(21, -15), nwr=(18, 8), trail=1.6, curl=0.4)),
    (500, dict(T=(44, -8), bas=8, arr=(5, -5), head=(1, 0.8), tilt=3, fwr=(23, 6), fha=25, nwr=(21, 12), trail=1.1, curl=0.8)),
    (550, dict(T=(46, 0), dos=(1.2, 2.6), bas=5, head=(1.2, 1.4), tilt=3, fwr=(22, 9), fha=30, nwr=(22, 15), trail=0.3, curl=0.9)),
    (680, dict(T=(46, 0), dos=(0.8, 1.8), bas=3, head=(0.8, 1.0), tilt=2, fwr=(21, 7), fha=24, nwr=(22, 15), curl=0.6)),
    (770, dict(T=(27, -14), bas=-5, arr=(5, -7), head=(-0.6, 0), fwr=(20, -5), nwr=(18, 10), trail=-1.2, curl=0.2)),
    (870, dict(T=(3, 0), dos=(0, 3.2), head=(0, 1.4), fwr=(19, -2), trail=-0.5, ear=1)),
    (980, dict(dos=(0, 1.0), head=(0, 0.4))),
    (1100, {}),
]
AT_SLASH0, AT_HIT = 440, 540            # la griffe part au-dessus de la tête / touche (ms)

# 3) L'attaque spéciale « Ruée de magma » (pixel : SPECIALE). Il se charge : le coeur blanchit, toutes ses fissures
# s'allument, la mèche flambe et se dresse, ses griffes prennent feu, des braises montent et de petites flammes lèchent
# le sol. Longue attente. Puis il FILE sur l'ennemi au ras du sol (un sillage de flammes) et griffe deux fois, très vite :
# la griffe levée descend, la griffe basse remonte — deux croissants de feu qui se croisent en X sur l'ennemi. Il
# rebondit au-dessus de lui, griffes levées (arrêt sur l'image, éclair), et plonge : ses griffes s'enfoncent au coeur
# du X, qui éclate en boule de feu avec des éclats de roche et des gouttes de lave. Il rebondit à sa place ; la boule
# de feu retombe en fumée.
SPECIAL = [
    (0, {}),
    (160, dict(dos=(-2, 2.6), head=(-0.6, 1.2), glow=1.4, burn=0.5, flare=0.8, rise=0.6, fwr=(20, -8), curl=0.4)),
    (430, dict(dos=(-3, 3.6), head=(-1, 1.6), tilt=-2, glow=3, burn=1, flare=1.5, rise=1.0, fwr=(20, -10), nwr=(17, 13), curl=0.5, ear=1)),
    (490, dict(T=(28, -1), bas=7, dos=(1, 1), arr=(-2, -1), glow=2.6, burn=1, flare=0.8, trail=2.0, fwr=(20, -12), nwr=(19, 12), curl=0.4)),
    (550, dict(T=(44, 0), dos=(1, 2.4), bas=4, glow=2.4, burn=1, flare=0.6, trail=1.2, fwr=(20, -14), nwr=(20, 14), curl=0.5)),
    (620, dict(T=(46, 0), dos=(1.4, 2.8), bas=6, head=(1, 1), glow=2.4, burn=1, trail=0.6, fwr=(24, 8), fha=30, nwr=(20, 15), curl=0.9)),
    (700, dict(T=(46, 0), dos=(1.2, 2.2), bas=2, head=(1, 0.4), glow=2.4, burn=1, trail=0.4, fwr=(22, 6), fha=20, nwr=(27, -1), nha=-40, curl=0.9)),
    (790, dict(T=(42, -28), bas=-6, arr=(7, -9), head=(0, -0.4), glow=2.6, burn=1, flare=1.0, rise=0.8, fwr=(20, -15), nwr=(25, -4), nha=-50, curl=0.7)),
    (930, dict(T=(43, -30), bas=-7, arr=(7, -9), head=(0, -0.6), glow=3, burn=1, flare=1.2, rise=1.0, fwr=(20, -16), nwr=(25, -5), nha=-52, curl=0.8)),
    (990, dict(T=(48, -8), bas=16, arr=(4, -4), head=(1, 1), tilt=4, glow=2.6, burn=1, trail=-0.6, fwr=(23, 10), fha=30, nwr=(25, 14), curl=1)),
    (1040, dict(T=(48, 0), dos=(1.4, 3.2), bas=10, head=(1.2, 1.6), tilt=4, glow=2.2, burn=0.8, fwr=(22, 12), fha=30, nwr=(24, 16), curl=1)),
    (1180, dict(T=(48, 0), dos=(1, 2.6), bas=7, head=(1, 1.2), tilt=3, glow=1.6, burn=0.5, fwr=(21, 10), fha=24, nwr=(23, 16), curl=0.8)),
    (1300, dict(T=(27, -16), bas=-5, arr=(5, -7), head=(-0.6, 0), glow=1.0, burn=0.2, trail=-1.2, fwr=(20, -5), nwr=(18, 10), curl=0.3)),
    (1420, dict(T=(2, 0), dos=(0, 3.4), head=(0, 1.4), glow=0.6, trail=-0.5, fwr=(19, -2), ear=1)),
    (1580, dict(dos=(0, 1.2), head=(0, 0.4), glow=0.2)),
    (1750, {}),
]
SP_DASH0, SP_DASH1 = 430, 560          # la ruée au ras du sol
SP_S1, SP_H1 = 560, 640                # premier coup : la griffe levée descend
SP_S2, SP_H2 = 640, 720                # deuxième coup : la griffe basse remonte
SP_FLASH = 900                         # en l'air, griffes levées : éclair
SP_DIVE = 1040                         # il plonge : la boule de feu éclate


def idle_offsets(T):
    """Le repos d'une petite bête nerveuse, à l'affût : souffle court (≈ 0,85 s), il se tasse comme un ressort, la tête
    suit avec retard, les doigts de la main levée frémissent (et un petit tic vers l'ennemi), l'oreille tressaille."""
    u = 2 * math.pi * T / 0.85
    br = 0.5 - 0.5 * math.cos(u)
    tic = math.sin(math.pi * min(1.0, max(0.0, ((T % 2.9) - 2.2) / 0.35))) ** 2
    flick = math.sin(math.pi * min(1.0, max(0.0, ((T % 3.4) - 1.0) / 0.25)))
    return dict(br=br, dosy=0.45 * math.sin(u - 0.4), heady=-0.35 * math.sin(u - 1.1) + 0.1, headx=0.12 * math.sin(u - 1.3),
                tilt=0.5 * math.sin(u * 0.5), fwrx=0.25 * math.sin(u - 1.6) + 0.9 * tic, fwry=-0.45 * math.sin(u - 1.4) - 0.5 * tic,
                fha=1.5 * math.sin(u - 1.8) + 4 * tic, nwry=0.25 * math.sin(u - 0.9), curl=0.08 * math.sin(3 * u) + 0.12 * tic,
                ear=max(0.0, flick), glow=0.25 * br)


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
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    out = dict(T=(P['Tx'], P['Ty']), bas=P['bas'], dos=(P['dosx'], P['dosy']), br=w * idl['br'],
               head=(P['headx'], P['heady']), tilt=P['tilt'], arr=(P['arrx'], P['arry']),
               nwr=(P['nwrx'], P['nwry']), fwr=(P['fwrx'], P['fwry']), nha=P['nha'], fha=P['fha'],
               curl=max(0.0, min(1.0, P['curl'])), trail=P['trail'], flare=P['flare'], rise=P['rise'],
               glow=max(0.0, P['glow']), burn=max(0.0, min(1.0, P['burn'])), ear=P['ear'],
               ph=2 * math.pi * T / 0.55)
    blink = 1.0 if (w > 0.95 and 1.6 <= (T % 3.1) < 1.72) else 0.0
    out['blink'] = max(blink, 1.0 if P['shut'] > 0.5 else 0.0)
    return out, tl


# ======================================================================== les effets propres au lutin


def ember_rise(fig, ctx, T, n=1, spread=1.0, seed=0):
    """Des braises qui montent de la mèche en ondulant et s'éteignent."""
    out = ''
    fx_, fy_ = ctx['flame']
    for i in range(n):
        per = 1.3 + 0.37 * ((i + seed) % 3)
        ph = ((T + 0.53 * i + 0.21 * seed) % per) / per
        x = fx_ + (i * 3.1 % 7 - 3) * spread + 2.2 * math.sin(ph * 7 + i)
        y = fy_ - 2 - 16 * ph * spread
        out += ember(fig, x, y, 0.75 * (1 - 0.6 * ph), op=env(ph, 0, 0.1, 0.6, 1))
    return out


def fx_idle(T):
    def f(fig, ctx):
        fig.fx_front.append(ember_rise(fig, ctx, T, 1))
    return f


def land_cloud(fig, x, t, size=1.0, seed=0):
    """Un petit nuage de poussière brûlante à l'atterrissage (deux bouffées qui s'écartent et se défont)."""
    if t < 0 or t > 1:
        return ''
    op = 1 - ramp(t, 0.5, 1.0)
    r = (1.6 + 1.6 * t) * size
    return (puff(fig, x - 5 - 5 * t, GR - r * 0.7, r, op, seed, hollow=0.6 * t)
            + puff(fig, x + 4 + 5 * t, GR - r * 0.6, r * 0.85, op, seed + 1, hollow=0.6 * t))


def fx_attack(tl, T):
    def f(fig, ctx):
        P = ctx['P']
        back, front = [], []
        # l'envol : une bouffée et deux langues de feu au point de départ
        back.append(land_cloud(fig, 60, (tl - 330) / 320, 1.0, 1))
        for i, (dx, hh) in enumerate(((-4, 3.2), (2, 4.4), (7, 2.6))):
            k = env(tl, 340 + 20 * i, 380 + 20 * i, 430, 560)
            back.append(tongue(fig, (52 + dx, GR), hh * k, 2.4, lean=-0.25, ph=T * 18 + i, op=k))
        # la griffure : un croissant de feu qui suit la griffe, de la tête de l'ennemi vers le bas
        s = START['a_path']
        k = ramp(tl, AT_SLASH0, AT_HIT)
        fade = 1 - ramp(tl, AT_HIT + 60, AT_HIT + 240)
        if tl >= AT_SLASH0:
            front.append(crescent(fig, s, 6.0, op=fade, head=max(0.15, k)))
        # la touche : gerbe de flammes et de braises au point de griffe (tenue)
        if tl >= AT_HIT - 10:
            u = (tl - AT_HIT + 10) / 300
            c = s[-1]
            front.append(glow(fig, c, 14 * (0.6 + 0.6 * min(1, u * 3)), LAVA[2], 0.55 * (1 - ramp(u, 0.4, 1))))
            for i, (dx, hh, ln) in enumerate(((-3.5, 6.5, -0.2), (0.5, 9.0, 0.1), (4.0, 5.5, 0.3))):
                kk = env(u, 0, 0.15, 0.55, 1.0)
                front.append(tongue(fig, (c[0] + dx, c[1] + 4), hh * kk, 3.4, lean=ln, ph=T * 20 + i, op=kk))
            for i in range(6):
                a = math.radians(-150 + 47 * i + 9 * (i % 2))
                d = (4 + 14 * u) * (0.8 + 0.12 * (i % 3))
                front.append(ember(fig, c[0] + d * math.cos(a), c[1] + d * math.sin(a) + 10 * u * u, 0.9 - 0.4 * u,
                                   op=1 - ramp(u, 0.6, 1)))
        # le rebond : une bouffée au départ, et le petit nuage à l'arrivée chez lui
        back.append(land_cloud(fig, 108, (tl - 700) / 300, 0.8, 2))
        back.append(land_cloud(fig, 64, (tl - 860) / 360, 1.0, 0))
        fig.fx_back.extend(back)
        fig.fx_front.extend(front)
        fig.fx_front.append(ember_rise(fig, ctx, T, 1))
    return f


def fx_special(tl, T):
    def f(fig, ctx):
        P = ctx['P']
        back, front = [], []
        # la charge : le coeur blanchit (lueur), les braises montent, de petites flammes lèchent le sol autour de lui
        ch = env(tl, 60, 380, 470, 620)
        back.append(glow(fig, ctx['chest'], 16 * ch, LAVA[2], 0.45 * ch))
        for i, (x, hh, ln) in enumerate(((38, 3.6, -0.2), (47, 5.0, 0.1), (57, 3.0, -0.1), (72, 4.4, 0.2), (81, 2.8, 0.0))):
            k = env(tl, 120 + 40 * i, 300 + 30 * i, 470, 640)
            back.append(tongue(fig, (x, GR), hh * k * (1 + 0.15 * math.sin(T * 13 + i)), 2.4, lean=ln, ph=T * 16 + i * 1.7, op=k))
        for i in range(5):
            ph = ((tl - 100 - 70 * i) % 520) / 520
            if 100 < tl < 620:
                x = 40 + 9 * i + 3 * math.sin(ph * 6 + i)
                front.append(ember(fig, x, GR - 4 - 34 * ph, 0.8 * (1 - 0.5 * ph), op=env(ph, 0, 0.1, 0.7, 1) * ch))
        # la ruée : un sillage de langues de feu au ras du sol, de tailles inégales, qui s'éteignent dans l'ordre
        for i in range(7):
            x = 60 + 13 * i
            t_on = SP_DASH0 + 18 * i
            k = env(tl, t_on, t_on + 40, t_on + 160, t_on + 420)
            hh = (6.0 - 0.4 * i) * (0.75 + 0.25 * ((i * 7) % 3))
            back.append(tongue(fig, (x, GR), hh * k, 3.0, lean=-0.45, ph=T * 18 + i, op=k))
            back.append(scorch(fig, x - 5, x + 5, env(tl, t_on, t_on + 60, 1300, 1700)))
        # les deux griffures en X sur l'ennemi : elles restent un moment, puis s'éteignent quand il plonge
        p1, p2 = X_A, X_B
        hold = 1 - ramp(tl, SP_DIVE, SP_DIVE + 120)
        if tl >= SP_S1:
            front.append(crescent(fig, p1, 6.2, op=hold * (1 - 0.25 * ramp(tl, SP_H1, SP_H1 + 300)), head=max(0.15, ramp(tl, SP_S1, SP_H1))))
        if tl >= SP_S2:
            front.append(crescent(fig, p2, 6.2, op=hold * (1 - 0.25 * ramp(tl, SP_H2, SP_H2 + 300)), head=max(0.15, ramp(tl, SP_S2, SP_H2))))
        # en l'air, griffes levées : l'éclair (une lueur blanche-jaune autour de lui)
        fl = env(tl, SP_FLASH - 90, SP_FLASH - 30, SP_FLASH + 10, SP_FLASH + 60)
        if fl > 0:
            back.append(glow(fig, (ctx['head'][0], ctx['head'][1] + 6), 30, LAVA[1], 0.6 * fl))
            for c_ in (ctx['clawF'], ctx['clawN']):
                front.append(spark(fig, c_[0], c_[1], 3.2 * fl, op=fl))
        # la boule de feu : elle éclate au coeur du X, tourbillonne, puis retombe en fumée ; éclats et gouttes
        u = (tl - SP_DIVE) / 600.0
        if 0 <= u <= 1.25:
            c = HIT
            grow = ramp(u, 0, 0.18)
            hol = ramp(u, 0.45, 1.0)
            back.append(glow(fig, c, 34 * (0.5 + 0.5 * grow), LAVA[2], 0.55 * (1 - hol)))
            front.append(fireball(fig, (c[0], c[1] - 2 - 6 * hol), 11 * (0.4 + 0.6 * grow) * (1 + 0.15 * hol), 40 + 260 * u,
                                  op=1 - ramp(u, 0.7, 1.0), hollow=hol))
            for i in range(3):
                front.append(puff(fig, c[0] - 6 + 6 * i, c[1] - 6 - 12 * hol - 3 * i, (3.0 + 1.2 * i) * hol + 0.5,
                                  op=env(u, 0.45, 0.7, 0.95, 1.25), seed=i, hollow=ramp(u, 0.8, 1.25)))
            for i in range(5):
                a = math.radians(-160 + 36 * i + 7 * (i % 2))
                v = 26 + 6 * (i % 3)
                x = c[0] + v * u * math.cos(a)
                y = c[1] + v * u * math.sin(a) + 42 * u * u
                if y < GR and u > 0.12:
                    front.append(chunk(fig, x, y, 200 * u + 50 * i, 1.1 + 0.25 * (i % 2), op=1 - ramp(u, 0.9, 1.2)))
            for i in range(4):
                a = math.radians(-120 + 40 * i)
                v = 30 + 4 * i
                vx, vy = v * math.cos(a), v * math.sin(a) + 84 * u
                x = c[0] + v * u * math.cos(a)
                y = c[1] + v * u * math.sin(a) + 42 * u * u
                if y < GR and u > 0.1:
                    front.append(drop(fig, x, y, vx, vy, 0.9, op=1 - ramp(u, 0.8, 1.1)))
        # le rebond chez lui : bouffée au départ, petit nuage à l'arrivée
        back.append(land_cloud(fig, 112, (tl - 1180) / 300, 0.8, 2))
        back.append(land_cloud(fig, 64, (tl - 1410) / 380, 1.0, 0))
        fig.fx_back.extend(back)
        fig.fx_front.extend(front)
        fig.fx_front.append(ember_rise(fig, ctx, T, 2 if tl < 900 else 1, 1.2))
    return f


START = {}
# les deux griffures de la spéciale : deux croissants qui se croisent en X sur l'ennemi (le premier descend, le
# second remonte ; la tête du croissant est là où finit la griffe)
X_A = resample(bez((143, 83), (154, 85), (162, 96), (162, 110), 30), 22)
X_B = resample(bez((143, 110), (153, 109), (161, 98), (163, 84), 30), 22)


def claw_path(act, t0, ms0, ms1, key='clawF', n=10):
    """La trajectoire réelle d'une griffe entre deux instants (pour tracer le croissant de feu)."""
    pts = []
    for i in range(n + 1):
        Ph, _ = pose_at(t0 + (ms0 + (ms1 - ms0) * i / n) / 1000.0, act, t0)
        pts.append(K.build(pose=Ph).ctx[key])
    # une courbe souple qui passe par ces points, rééchantillonnée
    return resample(pts, 22)


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
    g = Image.new('RGBA', (w, h))
    ImageDraw.Draw(g).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous lui : elle le suit dans ses bonds, rétrécit et pâlit quand il saute."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    Tx, Ty = P['T']
    cx = (60 + Tx - x0) * k
    s = max(0.5, 1 + Ty / 34)
    sd.ellipse([cx - 32 * k * s, fy - 2.6 * k * s, cx + 32 * k * s, fy + 2.6 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
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
    if act == 'attack':
        if ('a', t0) not in START:
            START[('a', t0)] = claw_path(act, t0, AT_SLASH0, AT_HIT, 'clawF')
        START['a_path'] = START[('a', t0)]
        fx = [fx_attack(tl, T)]
    elif act == 'special':
        if ('s', t0) not in START:
            START[('s', t0)] = (claw_path(act, t0, SP_S1, SP_H1, 'clawF'), claw_path(act, t0, SP_S2, SP_H2, 'clawN'))
        START['s_path1'], START['s_path2'] = START[('s', t0)]
        fx = [fx_special(tl, T)]
    else:
        fx = [fx_idle(T)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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
        moments = extra or [0.5, 1.0, a_s + 0.3, a_s + 0.4, a_s + 0.47, a_s + 0.54, a_s + 0.62, a_s + 0.78,
                            s_s + 0.42, s_s + 0.5, s_s + 0.6, s_s + 0.68, s_s + 0.75, s_s + 0.9, s_s + 1.06,
                            s_s + 1.15, s_s + 1.3, s_s + 1.45]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, fr[i][1]))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('PLANCHE') or os.path.join(TMP, 'planche.png')
        sheet.save(out)
        print('planche :', out)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, fr[i][1]))
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
