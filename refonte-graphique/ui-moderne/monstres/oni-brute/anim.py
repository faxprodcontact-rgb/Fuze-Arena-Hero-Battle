# L'oni brute vectoriel ANIMÉ (refonte des monstres, 27/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/oni-brute/build.py) — respiration, attaque de base « Écrase-crâne », attaque spéciale
# « Faille de lave » — mais dans le style lisse de l'interface, sur le modèle de Lenore (son chef de clan,
# ../../heros/lenore/anim.py) et de Taurok (../../heros/taurok/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/oni-brute/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/oni-brute/)
#   python3 refonte-graphique/ui-moderne/monstres/oni-brute/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (oni-brute.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette : buste qui
# respire et se penche depuis les hanches, ventre qui se gonfle, tête, mâchoire qui s'ouvre, mèches qui ondulent, bras
# lointain, pagne ; le bras proche est placé par cinématique inverse depuis le poing, qui tient le kanabō ; les jambes
# aussi, pieds au sol). Il est plus lourd et plus lent que Lenore : il ne quitte jamais le sol ; préparations longues,
# coups qui tombent de tout leur poids, impacts tenus, retours lents (comme le pixel art). Les poses clés reprennent
# celles du pixel art et sont reliées par des courbes douces sans dépassement (24 images par seconde). Les effets
# (souffle chaud du naseau, traînée de fer, poussière en bouffées, mottes de terre, braises, flammes en langues courbes,
# faille de lave et geysers, fumée en volutes) sont dessinés dans le même style : dégradés, un seul contour, aucun flou
# SVG ; jamais de rayons droits répétés.
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('oni_brute', os.path.join(HERE, 'oni-brute.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import sm, lock, ribbon, ellipse, rpoly, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'oni-brute')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-oni-brute/_images'
LAVA = K.LAVA
FPS = 24
VIEW = (-34, -40, 288, 162)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour du feu
SINK = '#4a3656'                     # le contour de la fumée
EINK = '#3e2a36'                     # le contour de la terre et des roches
GR = K.GRD
EARTH = ['#e8d2b0', '#c8a884', '#8e6e5a', '#5e4648', '#3e2a36']           # poussière claire → roche sombre

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


PAIRS = {'G': ('gx', 'gy'), 'head': ('headx', 'heady'), 'far': ('farx', 'fary'), 'nsh': ('nshx', 'nshy'), 'wr': ('wrs', 'wrt')}
SCAL = ['crouch', 'lean', 'tilt', 'jaw', 'ml', 'pg', 'rn', 'rf', 'far_rot', 'eyes', 'hot', 'ang', 'bend', 'length', 'breath']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: K.REST[n] for n in SCAL}
    for key, (a, b) in PAIRS.items():
        d[a], d[b] = K.REST[key]
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


def wr_of(ang, dx, dy):
    """Le poignet dans le repère de la massue (le long, en travers), d'après son décalage voulu depuis le poing."""
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    nv = (-u[1], u[0])
    return (dx * u[0] + dy * u[1], dx * nv[0] + dy * nv[1])


# ======================================================================== les actions (poses clés)
# G : le milieu du poing sur le manche (repère du haut du corps) ; ang : la direction poing → tête de fer (degrés, y vers
# le bas : −90 = vers le haut), continue d'une clé à l'autre ; wr : le poignet. Points et angles du pixel art (angle du
# pixel art changé de signe).
def club(G, ang, wd, **kw):
    return dict(G=G, ang=ang, wr=wr_of(ang, *wd), **kw)


LIFT = club((24.5, 74.5), -118, (4.6, -7.4), crouch=1, lean=-1, head=(0, 1), tilt=-1, ml=1, pg=1)
HOLD = club((40.5, 17.5), -214, (0.8, 8.2), bend=-1, crouch=-1, lean=-4, breath=1.0, head=(-1, -1), tilt=-5, ml=1, pg=1, far=(1, -1),
            far_rot=-6, nsh=(1, -2))
SWING = club((62.5, 30.5), -48, (-6.6, 5.2), bend=-1, crouch=1, lean=1, head=(1, 0), tilt=2, ml=0, pg=0, nsh=(2, -1))
SMASH = club((55.5, 78.5), 19, (-4.4, -7.2), bend=-1, crouch=3, lean=4, head=(1, 1), tilt=4, ml=-1, pg=-1, far=(-1, 0), far_rot=8,
             nsh=(3, 1))
REC1 = club((46.5, 80.5), -10, (-2.4, -8.2), bend=-1, crouch=1, lean=2, head=(0, 1), tilt=1, ml=1, pg=1, nsh=(1, 0))
REC2 = club((30.0, 86.6), -106, (0.8, -8.6), crouch=1, lean=1, ml=0, pg=0)

# 2) L'attaque de base « Écrase-crâne » : il soulève la massue (elle bascule en arrière), puis l'arme loin derrière sa
# tête, couchée au-dessus de la bosse du dos, cambré, ventre gonflé, menton levé (temps de pose ; il souffle par le
# naseau). Tout tombe d'un coup : la massue passe au-dessus de lui (traînée de fer en croissant) et s'écrase au sol devant
# lui, le buste plongé en avant (impact tenu : poussière, mottes, braises, le sol se fend). Il la laisse posée un instant,
# puis la relève lentement et la ramène debout, en garde.
ATTACK = [
    (0, {}),
    (150, dict(LIFT)),
    (330, dict(HOLD)),
    (600, dict(HOLD, G=(40.0, 18.5), lean=-4.4, crouch=-1.2, tilt=-6)),
    (650, dict(SWING)),
    (690, dict(SMASH)),
    (900, dict(SMASH, crouch=3.3, head=(1, 1.6))),
    (1030, dict(SMASH, crouch=2.4, ml=1, pg=1)),
    (1190, dict(REC1)),
    (1340, dict(REC2)),
    (1490, dict(crouch=1, ml=0, pg=-1)),
    (1650, {}),
]
ATTACK_HIT = 690

# 3) L'attaque spéciale « Faille de lave » : il ne bondit pas (il est trop lourd) : il ouvre la terre. Il soulève la
# massue puis la dresse tout droit au-dessus de sa tête, le ventre gonflé ; il RUGIT (la gueule s'ouvre en grand, les
# yeux deviennent blancs de feu) et le fer chauffe au rouge puis au blanc : des langues de flamme lèchent la tête de la
# massue, des braises montent (temps de pose). Il l'abat de tout son poids (traînée de feu) : arrêt sur l'image, éclair,
# le sol tremble. Le sol se fend et la faille court au ras du sol vers la droite, à travers tout le premier rang
# ennemi : la lave jaillit en geysers l'un après l'autre (langues de feu, gouttes de lave qui retombent, mottes de
# roche), puis chaque geyser retombe en fumée ; derrière, la faille refroidit (jaune, orange, rouge, puis croûte sombre).
# Il relève la massue encore rouge, qui fume, et revient en garde.
RAISE = club((42.5, 12.5), -94, (1.2, 8.4), bend=-1, crouch=-1, lean=-1, breath=1.0, head=(0, -1), tilt=-3, ml=1, pg=1, far=(1, -1),
             far_rot=-6, nsh=(1, -3), hot=0.8)
ROAR = dict(RAISE, lean=-2.2, head=(-1, -2), tilt=-7, jaw=2.4, eyes=1.0, hot=2.0, ml=-1, pg=-1, far=(1, -2))
SPECIAL = [
    (0, {}),
    (150, dict(LIFT)),
    (320, dict(RAISE)),
    (430, dict(ROAR)),
    (800, dict(ROAR, G=(42.0, 13.5), tilt=-8, head=(-1, -2.4))),
    (855, dict(SWING, jaw=1.2, eyes=1.0, hot=2.0, lean=2)),
    (900, dict(SMASH, crouch=4, lean=5, head=(1, 2), jaw=2.2, eyes=1.0, hot=2.0)),
    (1120, dict(SMASH, crouch=4, lean=5, head=(1, 1.4), jaw=2.0, eyes=1.0, hot=2.0, ml=1, pg=1)),
    (1500, dict(SMASH, crouch=3, lean=4, head=(1, 1), jaw=0.6, eyes=0.4, hot=1.5)),
    (1640, dict(SMASH, crouch=2.6, lean=4, head=(1, 1), jaw=0, eyes=0, hot=1.3, pg=-1)),
    (1800, dict(REC1, hot=1.1)),
    (1960, dict(REC2, hot=0.8)),
    (2120, dict(crouch=1, ml=0, pg=-1, hot=0.4)),
    (2320, dict(hot=0.0)),
]
SP_HIT = 900


# ======================================================================== la respiration (en boucle, 2,4 s)

def idle_offsets(T):
    """Il inspire à fond (le buste et la tête montent, le ventre se gonfle), les épaules roulent l'une après l'autre (la
    proche, qui tient la massue, puis la lointaine), la tête suit en retard ; à l'expiration il se tasse sur ses petites
    jambes et souffle par le naseau ; les mèches et le pagne se balancent en retard."""
    u = 2 * math.pi * T / 2.4
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 2.8)), heady=0.45 * math.sin(u - 0.8),
                tilt=-0.8 * math.sin(u - 1.0), rn=0.9 * (0.5 - 0.5 * math.cos(u - 0.4)), rf=0.8 * (0.5 - 0.5 * math.cos(u - 1.3)),
                ml=0.7 * math.sin(u - 1.6), pg=0.6 * math.sin(u + 0.4))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
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
    src = act or keyed([(0, {})], 0)
    P = {}
    for n in SCAL:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['G'] = (src['gx'], src['gy'])
    P['wr'] = (src['wrs'], src['wrt'])
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['far'] = (src['farx'], src['fary'])
    P['nsh'] = (src['nshx'], src['nshy'])
    P['ph'] = 2 * math.pi * T * 0.55 + (1.4 * T if act and action == 'special' else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.62 <= (T % 4.8) < 1.71) else 0.0
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, cool=False):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S. lean : elle penche (x par unité de h)."""
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
    if cool:
        gout = g_lin(fig, p0, p3, [(0, LAVA[2]), (0.5, LAVA[3]), (1, LAVA[5])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[1]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3, op=op)


def tongue_dir(fig, base, d, h, w, bend=0.0, op=1.0):
    """Une langue de feu qui part dans une direction quelconque (d : vecteur unité), pour le feu de la massue."""
    bx, by = base
    nx, ny = -d[1], d[0]
    p0 = (bx, by)
    p1 = (bx + d[0] * h * 0.33 + nx * bend * w * 0.5, by + d[1] * h * 0.33 + ny * bend * w * 0.5)
    p2 = (bx + d[0] * h * 0.68 - nx * bend * w * 0.45, by + d[1] * h * 0.68 - ny * bend * w * 0.45)
    p3 = (bx + d[0] * h, by + d[1] * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    core = lock(p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), w * 0.5, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.4, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, p2, [(0, LAVA[0]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.2, op=op)


def ember(fig, x, y, r=0.7, op=1.0, hot=True):
    if op <= 0.02:
        return ''
    c1, c2, c3 = (LAVA[0], LAVA[1], LAVA[3]) if hot else (LAVA[2], LAVA[3], LAVA[5])
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, c1, op), (0.6, c2, op), (1, c3, op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def balls(fig, cx, cy, r, stops, ink, op):
    if r < 0.3 or op <= 0.02:
        return ''
    bl = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in bl)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in bl)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée (gris chaud un peu rosé, comme celle de Lenore), éclairée en haut à droite."""
    return balls(fig, cx, cy, r, [(0, '#f4e8e6'), (0.5, '#c8b0b8'), (1, '#8a6c84')], SINK, op)


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière de terre (beige), éclairée en haut à droite."""
    return balls(fig, cx, cy, r, [(0, '#fff2d4'), (0.5, '#dcb486'), (1, '#9a7058')], '#5a3e46', op)


def curl(fig, c, r, a0, turn, w, op=1.0, kind='smoke'):
    """Une volute qui s'enroule (un ruban courbe qui s'affine), sous un contour doux."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    if kind == 'smoke':
        gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f4e8e6'), (0.6, '#c8b0b8'), (1, '#8a6c84')])
        return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fff2d4'), (0.6, '#dcb486'), (1, '#9a7058')])
    return outlined([(sh, gr, 1)], ink='#5a3e46', w=1.0, op=op)


def hsh(i, k):
    """Un « hasard » fixe (même valeur à chaque image) : pour les formes des roches."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


def rock(fig, c, r, seed=0, rot=0.0, op=1.0):
    """Une motte de terre ou un éclat de roche : un polygone irrégulier à facettes (face éclairée en haut à droite), un
    seul contour."""
    if r < 0.25 or op <= 0.02:
        return ''
    n = 6
    pts = []
    for i in range(n):
        a = math.radians(rot + 360 * i / n + 25 * (hsh(seed, i) - 0.5))
        rr = r * (0.72 + 0.4 * hsh(seed, i + 7))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    body = rpoly(pts, r * 0.18)
    lit = sorted(range(n), key=lambda i: -((pts[i][0] - c[0]) * 0.6 - (pts[i][1] - c[1]) * 0.8))[:2]
    lit.sort()
    cc = (c[0] + r * 0.08, c[1] - r * 0.1)
    face = rpoly([cc, pts[lit[0]], pts[lit[1]]], r * 0.1)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, EARTH[1]), (0.55, EARTH[2]), (1, EARTH[3])])
    return outlined([(body, gr, 1), (face, EARTH[0], 0.85)], ink=EINK, w=1.2, op=op)


def lava_drop(fig, c, r, op=1.0):
    """Une goutte de lave qui vole : un coeur jaune pâle, un bord orange, un contour sombre."""
    if r < 0.25 or op <= 0.02:
        return ''
    gr = g_rad(fig, (c[0] + 0.25 * r, c[1] - 0.25 * r), r * 1.2, [(0, LAVA[0]), (0.45, LAVA[1]), (0.8, LAVA[2]), (1, LAVA[3])])
    return outlined([(ellipse(c[0], c[1], r, r * 0.92), gr, 1)], w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0, cool=False):
    """Un éclat d'impact en nuage de feu : un coeur et des lobes arrondis (plus gros vers « facing »), un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    stops = [(0, LAVA[0]), (0.35, LAVA[1]), (0.65, LAVA[2]), (0.88, LAVA[3]), (1, LAVA[4])] if not cool else \
        [(0, LAVA[1]), (0.5, LAVA[2]), (0.85, LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, stops)
    return outlined([(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes], w=1.4, op=op)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28, squash=1.0):
    """Un croissant le long d'un arc autour de C, de a0 (fin) à a1 (plein) ; degrés, y vers le bas."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * squash * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * squash * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def trail(fig, C, R, a0, a1, w, op=1.0, fire=False):
    """La traînée de la massue : un croissant courbe qui s'efface vers l'arrière (fer clair bordé de braise, ou feu)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.36)
    if fire:
        g1 = g_lin(fig, pa, pb, [(0, LAVA[3], 0), (0.5, LAVA[2], 0.7 * op), (1, LAVA[1], 0.95 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.9 * op), (1, LAVA[0], op)])
    else:
        g1 = g_lin(fig, pa, pb, [(0, '#c8d0ea', 0), (1, '#f0f4ff', 0.8 * op)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.7 * op), (1, LAVA[1], 0.9 * op)])
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


def crack(fig, x0, x1, level, seed=0, op=1.0, cool=0.0):
    """Le sol fendu au ras du sol (couché, vu en perspective), de x0 à x1 : une lueur, la fente sombre, le coeur de
    lave (jaune → orange → rouge → croûte quand il refroidit : cool de 0 à 1)."""
    if op <= 0.02 or x1 - x0 < 1:
        return []
    out = []
    n = max(3, int((x1 - x0) / 6))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.3 + (1.0 * hsh(seed, i) - 0.5) * (0.6 if 0 < i < n else 0)) for i in range(n + 1)]
    ws = [0.3] + [1.1 + 0.6 * level * (0.6 + 0.4 * hsh(seed, i + 3)) for i in range(1, n)] + [0.2]
    if cool < 0.9:
        hot = 1 - cool
        gl = g_lin(fig, (x0, GR), (x1, GR), [(0, LAVA[2], 0.35 * op * hot), (1, LAVA[3], 0.2 * op * hot)])
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm((x0 + x1) / 2), fm(GR), fm((x1 - x0) / 2 + 4), fm(2.4), gl))
    out.append('<path d="%s" fill="%s" opacity="%g"/>' % (ribbon(pts, ws).d(), '#2a0e14', op))
    core = [LAVA[0], LAVA[1], LAVA[2], LAVA[3], LAVA[4], LAVA[5], '#4a1a1a'][min(6, int(cool * 6.99))]
    out.append('<path d="%s" fill="%s" opacity="%g"/>' % (ribbon(pts, [w * 0.45 for w in ws]).d(), core, op))
    return out


def club_pt(ctx, s):
    return ctx['club_pt'](s)


# ---- le souffle chaud par le naseau (une petite volute de fumée)

def snort(fig, ctx, k, big=1.0):
    if not 0 < k < 1:
        return
    n = ctx['nostril']
    o = env(k, 0, 0.15, 0.55, 1)
    x = n[0] + 4 + 7 * k * big
    y = n[1] + 0.5 - 6 * k * big
    fig.fx_front.append(smoke(fig, x, y, (0.8 + 1.6 * k) * big, op=0.8 * o))
    if k > 0.3:
        fig.fx_front.append(curl(fig, (x + 2.2 * big, y - 2.4 * big), 1.6 * big, 200, 260, 1.0 * big, op=0.7 * o))


# ---- l'attaque de base

HIT_AT = {}


def fx_attack(tl):
    def f(fig, ctx):
        # il souffle fort par le naseau en armant le coup
        if 200 < tl < 640:
            snort(fig, ctx, (tl - 200) / 440, big=1.3)
        # la massue passe au-dessus de lui : un croissant de fer autour de l'épaule, bordé de braise
        if 610 <= tl <= 790:
            S = ctx['S']
            tip = club_pt(ctx, 80)
            R = math.dist(S, tip) + 1
            a_to = math.degrees(math.atan2(tip[1] - S[1], tip[0] - S[0]))
            a_from = -150.0
            while a_from > a_to:
                a_from -= 360
            e = env(tl, 610, 640, 700, 790)
            fig.fx_back.append(trail(fig, S, R, a_from, a_to, 18 * e + 2, op=e))
            fig.fx_back.append(trail(fig, S, R * 0.7, a_from + 12, a_to, 6 * e + 1, op=0.8 * e))
        tau = (tl - ATTACK_HIT) / 1000.0
        c = HIT_AT.get('c')
        if tau >= -0.01 and c:
            cx = c[0]
            # l'éclat au point d'impact (arrêt sur l'image) : poussière claire, une étincelle de fer chaud
            fl = env(tau, -0.01, 0.0, 0.05, 0.16)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(GR - 4), fm(60), g_rad(
                    fig, (cx, GR - 4), 60, [(0, '#fffbe4', 0.7 * fl), (0.18, LAVA[1], 0.35 * fl), (0.5, LAVA[2], 0.1 * fl), (1, LAVA[3], 0)])))
            e = env(tau, 0, 0.03, 0.12, 0.3)
            if e > 0:
                fig.fx_front.append(pop(fig, (cx - 2, GR - 4), 5.6 * (0.6 + 0.4 * e), facing=-70, op=e))
            # le sol fendu sous le fer
            co = env(tau, 0, 0.04, 0.45, 0.85)
            fig.fx_back.extend(crack(fig, cx - 16, cx + 14 + 6 * min(1, tau * 8), 1, seed=3, op=co, cool=min(1, tau * 1.6)))
            # mottes de terre en cloche (vers l'avant surtout)
            for i, (vx, vy, r) in enumerate(((40, -70, 1.8), (64, -48, 1.4), (22, -84, 1.2), (80, -30, 1.1), (-30, -64, 1.3),
                                             (-50, -40, 0.9), (52, -88, 0.8), (96, -50, 0.8), (8, -96, 0.7))):
                if tau < 0.85:
                    x, y = ballistic((cx, GR - 3), (vx, vy), 190, tau)
                    if y < GR - 0.6:
                        fig.fx_front.append(rock(fig, (x, y), r, seed=i + 11, rot=tau * 500 + i * 40, op=min(1, 2.4 * (0.85 - tau))))
            # quelques braises (le fer chauffé du clan du feu)
            for i, (vx, vy) in enumerate(((30, -60), (55, -36), (12, -78), (-20, -50), (70, -20))):
                if tau < 0.6:
                    x, y = ballistic((cx, GR - 4), (vx, vy), 120, tau)
                    if y < GR - 1:
                        fig.fx_front.append(ember(fig, x, y, 0.6, op=max(0, 1 - tau / 0.6), hot=tau < 0.3))
            # la poussière qui roule des deux côtés
            if 0.03 < tau < 1.0:
                k = (tau - 0.03) / 0.97
                o = env(k, 0, 0.12, 0.5, 1)
                for side, big in ((-1, 1.0), (1, 0.9)):
                    fig.fx_back.append(dust(fig, cx + side * (6 + 18 * k), GR - 3.5 - 3 * k, (3 + 3.6 * k) * big, op=0.9 * o))
                    fig.fx_front.append(dust(fig, cx + side * (3 + 10 * k), GR - 2.0, (2 + 2.2 * k) * big, op=0.85 * o))
                fig.fx_back.append(curl(fig, (cx + 14 + 10 * k, GR - 10 - 8 * k), 3.4 + 1.6 * k, 200 + 90 * k, 280, 2.2, op=0.8 * o, kind='dust'))
        # il relève la massue : quelques gravillons
        if 1030 < tl < 1300 and c:
            tt = (tl - 1030) / 1000.0
            for i, (vx, vy) in enumerate(((-20, -40), (16, -46), (-6, -54))):
                x, y = ballistic((c[0], GR - 2), (vx, vy), 160, tt)
                if y < GR - 0.5:
                    fig.fx_front.append(rock(fig, (x, y), 0.7, seed=30 + i, rot=tt * 600, op=max(0, 1 - tt / 0.25)))
    return f


# ---- l'attaque spéciale

IMP_AT = {}
GEYSERS = [(14, 0.06, 1.0), (40, 0.16, 1.15), (66, 0.26, 1.0), (92, 0.36, 1.2), (116, 0.46, 0.95)]   # (écart, départ s, taille)
FAULT_LEN = 128.0


def club_fire(fig, ctx, level, tr):
    """Le kanabō chauffé à blanc : des langues de flamme sur la tête de fer, couchées à l'opposé du mouvement."""
    a = math.radians(ctx['ang'])
    u = (math.cos(a), math.sin(a))
    nv = (-u[1], u[0])
    for i, s_ in enumerate((42.0, 56.0, 70.0)):
        for side in (-1, 1):
            hw = 7.0 + 1.4 * (s_ - 33.6) / 46.0
            p = club_pt(ctx, s_)
            p = (p[0] + side * hw * nv[0], p[1] + side * hw * nv[1])
            d = (side * nv[0] * 0.5 + tr[0], side * nv[1] * 0.5 + tr[1] - 0.7)
            L = math.hypot(*d) or 1
            d = (d[0] / L, d[1] / L)
            wob = math.sin(ctx['P']['ph'] * 3 + i * 1.7 + side)
            h = (8 + 3 * wob) * (0.6 + 0.4 * level)
            fig.fx_back.append(tongue_dir(fig, p, d, h, 4.0, bend=0.6 * side))
    tip = club_pt(ctx, 80.0)
    d = (u[0] * 0.6 + tr[0], u[1] * 0.6 + tr[1] - 0.5)
    L = math.hypot(*d) or 1
    fig.fx_back.append(tongue_dir(fig, tip, (d[0] / L, d[1] / L), 11 + 4 * level, 6.0, bend=0.5))


def geyser(fig, x, age, big=1.0, seed=0, t=0.0):
    """Un geyser de lave : des langues de feu qui jaillissent de la faille, des gouttes de lave qui retombent en cloche,
    des mottes ; puis il retombe en fumée qui s'enroule (age en secondes)."""
    if age < 0:
        return
    up = env(age, 0, 0.06, 0.2, 0.5)
    if up > 0:
        for (dx, h, w, bd) in ((-3, 18, 6, -0.6), (1, 30, 8, 0.4), (5, 22, 7, 0.9)):
            fl_ = 1 + 0.1 * math.sin(t / 30.0 + dx + seed)
            fig.fx_front.append(tongue(fig, (x + dx * big, GR + 0.5), h * up * big * fl_, w * big * (0.6 + 0.4 * up), bend=bd, lean=0.05 * dx))
        fig.fx_back.append(pop(fig, (x + 1, GR - 6 * big), 4.5 * big * up, facing=-90, op=up))
    if age < 0.9:
        for i, (vx, vy, r) in enumerate(((-14, -70, 1.1), (12, -84, 1.3), (24, -56, 0.9), (-26, -48, 0.8), (4, -96, 0.9))):
            p = ballistic((x, GR - 6), (vx * big, vy * big), 200, age)
            if p[1] < GR - 0.5:
                fig.fx_front.append(lava_drop(fig, p, r * big, op=min(1, 2.0 * (0.9 - age))))
        for i, (vx, vy) in enumerate(((-30, -60), (34, -52))):
            p = ballistic((x, GR - 3), (vx, vy), 190, age)
            if p[1] < GR - 0.5:
                fig.fx_front.append(rock(fig, p, 1.1 * big, seed=seed * 7 + i, rot=age * 400, op=min(1, 2.2 * (0.9 - age))))
    sk = (age - 0.25) / 1.0
    if 0 < sk < 1:
        o = env(sk, 0, 0.15, 0.5, 1)
        fig.fx_back.append(smoke(fig, x + 2 + 4 * sk, GR - 12 * big - 14 * sk, (2.6 + 3 * sk) * big, op=0.8 * o))
        fig.fx_back.append(curl(fig, (x + 6 + 5 * sk, GR - 20 * big - 14 * sk), (2.4 + 1.4 * sk) * big, 200 + 90 * sk, 280, 1.8, op=0.7 * o))


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        # 1) le rugissement : l'air brûlant sort de la gueule en croissants courbes qui s'écartent (pas des rayons)
        if 380 < t < 820:
            m = ctx['mouth']
            for j in range(3):
                k = ((t - 380) / 440 * 1.6 + j * 0.33) % 1
                o = env(t, 380, 440, 720, 820) * (1 - k)
                R = 5 + 16 * k
                fig.fx_front.append(trail(fig, (m[0] - 2, m[1]), R, -44, 40, 2.4 + 1.3 * (1 - k), op=o, fire=True))
        # 2) le fer chauffe au rouge puis au blanc et flambe ; des braises montent du fer
        hot_l = env(t, 300, 440, 1200, 1700)
        if hot_l > 0.05:
            tr = (0.0, 0.0)
            if 820 < t < 905:
                tr = (-0.7, -0.5)
            club_fire(fig, ctx, hot_l, tr)
            for i in range(6):
                k = ((t / 1000.0) * 0.9 + i * 0.17) % 1
                p = club_pt(ctx, 50 + 26 * ((i * 0.37) % 1))
                fig.fx_front.append(ember(fig, p[0] + 6 * math.sin(k * 5 + i), p[1] - 30 * k, 0.55, op=hot_l * (1 - k) * min(1, k * 5)))
        # 3) il l'abat : une large traînée de feu en croissant autour de l'épaule
        if 815 <= t <= 1000:
            S = ctx['S']
            tip = club_pt(ctx, 80)
            R = math.dist(S, tip) + 1
            a_to = math.degrees(math.atan2(tip[1] - S[1], tip[0] - S[0]))
            a_from = -110.0
            while a_from > a_to:
                a_from -= 360
            e = env(t, 815, 840, 900, 1000)
            fig.fx_back.append(trail(fig, S, R, a_from, a_to, 18 * e + 2, op=e, fire=True))
            fig.fx_back.append(trail(fig, S, R * 0.66, a_from + 10, a_to, 6 * e + 1, op=e, fire=True))
        # 4) l'éclair (arrêt sur l'image)
        cx = IMP_AT.get('x', 120.0)
        fl = env(t, SP_HIT - 5, SP_HIT, SP_HIT + 30, SP_HIT + 170)
        if fl > 0:
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(GR - 10), fm(170), g_rad(
                fig, (cx, GR - 10), 170, [(0, '#fffbe4', 0.85 * fl), (0.12, '#ffe68a', 0.5 * fl), (0.45, '#ffb43a', 0.16 * fl), (1, '#ff7a1e', 0)])))
        # 5) la faille de lave court au ras du sol vers la droite ; les geysers éclatent l'un après l'autre
        if t >= SP_HIT:
            tau = (t - SP_HIT) / 1000.0
            front_x = cx + FAULT_LEN * min(1.0, tau / 0.5) ** 0.8
            fo = env(tau, 0, 0.02, 1.2, 1.7)
            # la faille refroidit derrière : par morceaux, du plus vieux (près de lui) au plus jeune
            nseg = 6
            for i in range(nseg):
                xa = cx - 10 + (front_x - cx + 10) * i / nseg
                xb = cx - 10 + (front_x - cx + 10) * (i + 1) / nseg
                born = max(0.0, (xa - cx) / FAULT_LEN * 0.5)
                cool = min(1.0, max(0.0, (tau - born - 0.25) / 0.9))
                fig.fx_back.extend(crack(fig, xa, xb + 0.5, 2, seed=11 + i, op=fo, cool=cool))
            e = env(tau, 0, 0.03, 0.14, 0.34)
            if e > 0:
                fig.fx_front.append(pop(fig, (cx - 2, GR - 5), 7.0 * (0.6 + 0.4 * e), facing=-80, op=e))
            for j, (dx, t0, big) in enumerate(GEYSERS):
                geyser(fig, cx + dx, tau - t0, big=big, seed=j, t=t)
            # la poussière soulevée par le choc, autour du fer
            if 0.02 < tau < 0.9:
                k = (tau - 0.02) / 0.88
                o = env(k, 0, 0.12, 0.5, 1)
                fig.fx_back.append(dust(fig, cx - 8 - 12 * k, GR - 3 - 2 * k, 3 + 3 * k, op=0.85 * o))
                fig.fx_front.append(dust(fig, cx - 4 - 6 * k, GR - 2, 2.2 + 1.6 * k, op=0.8 * o))
        # 6) la massue encore rouge fume en revenant
        if 1500 < t < 2350:
            k = (t - 1500) / 850
            p = club_pt(ctx, 70)
            o = env(k, 0, 0.15, 0.6, 1)
            fig.fx_back.append(smoke(fig, p[0] + 3 + 4 * k, p[1] - 6 - 14 * k, 1.8 + 2.2 * k, op=0.7 * o))
            fig.fx_back.append(curl(fig, (p[0] + 6 + 4 * k, p[1] - 12 - 14 * k), 1.8 + k, 200 + 80 * k, 260, 1.4, op=0.6 * o))
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
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre douce au sol sous lui."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (68 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 44 * k, fy - 3.0 * k, cx + 44 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
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
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if 'c' not in HIT_AT:
            Ph, _ = pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)
            HIT_AT['c'] = K.build(pose=Ph).ctx['tip']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'x' not in IMP_AT:
            Ph, _ = pose_at(t0 + SP_HIT / 1000.0, act, t0)
            IMP_AT['x'] = K.build(pose=Ph).ctx['tip'][0]
        fx = [fx_special(tl)]
    else:
        # au repos : à l'expiration, un petit souffle chaud sort du naseau
        k = ((T % 2.4) - 1.3) / 0.9
        fx = [lambda fig, ctx: snort(fig, ctx, k, big=0.9)]
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
    subprocess.run(['node', os.path.join(K.HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        extra = []
        for x in sys.argv[sys.argv.index('--planche') + 1:]:
            try:
                extra.append(float(x))
            except ValueError:
                break
        moments = extra or [1.2, 2.6, a_s + 0.15, a_s + 0.33, a_s + 0.6, a_s + 0.65, a_s + 0.7, a_s + 0.85, a_s + 1.19,
                            a_s + 1.34, s_s + 0.32, s_s + 0.6, s_s + 0.86, s_s + 0.92, s_s + 1.05, s_s + 1.25, s_s + 1.5,
                            s_s + 1.8, s_s + 2.0, s_s + 2.2]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        sh = shadow_layer(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(sh)
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = sys.argv[sys.argv.index('--sortie') + 1] if '--sortie' in sys.argv else os.path.join(TMP, '..', 'planche.png')
        sheet.save(dst)
        print('planche :', os.path.abspath(dst))
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    sh = shadow_layer(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(sh)
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
