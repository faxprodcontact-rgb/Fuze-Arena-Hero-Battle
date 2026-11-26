# Taurok vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/cyclope/build.py, ancien nom) — respiration, attaque de base « Coup de hache du
# colosse », attaque spéciale « Ruée du taureau » — mais dans le style lisse de l'interface, sur le modèle de Kael
# (../kael/anim.py) et de Lenore (../lenore/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/taurok/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/taurok/)
#   python3 refonte-graphique/ui-moderne/heros/taurok/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (taurok.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette : buste qui
# respire et se penche depuis les hanches, tête, mèches qui ondulent, épaules, pagne ; les deux bras sont placés par
# cinématique inverse depuis les poings, qui tiennent la hache ; les jambes aussi, sabots au sol). C'est un colosse :
# tout est lourd — longues préparations, coups très courts, impacts tenus, retours lents (comme le pixel art). Les
# poses clés sont reliées par des courbes douces sans dépassement (24 images par seconde). Les effets de la terre
# (vapeur des naseaux, poussière ocre, mottes et éclats de roche, dalles soulevées, fissures et lueur dorée de la terre,
# traînée d'acier) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG ; jamais de rayons
# droits répétés.
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
import taurok as K  # noqa: E402
from atelier import sm, ribbon, ellipse, rpoly, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'taurok')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-taurok/_images'
E = K.EARTH                          # blanc doré, or, ambre, ocre clair, ocre, brun, creux
FPS = 24
VIEW = (-30, -40, 288, 162)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
EINK = '#3e2a36'                     # le contour de la terre et des roches
SINK = '#4a3e5e'                     # le contour de la vapeur
GR = K.GRD

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


PAIRS = {'G': ('gx', 'gy'), 'head': ('headx', 'heady'), 'legl': ('llh', 'llb'), 'legn': ('lnh', 'lnb'),
         'fsh': ('fshx', 'fshy'), 'nsh': ('nshx', 'nshy')}
SCAL = ['crouch', 'lean', 'tilt', 'ml', 'pg', 'rn', 'rf', 'lift', 'shift', 'glow', 'hot', 'ang', 'sf', 'bn', 'bf', 'length', 'farfront']
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


# ======================================================================== les actions (poses clés)
# G : le milieu du poing proche sur le manche ; ang : la direction du manche vers le fer (degrés, y vers le bas :
# −90 = vers le haut) ; sf : la main lointaine le long du manche.

# 2) L'attaque de base « Coup de hache du colosse » : la main gauche glisse le long du manche, il lève la hache droite
# au-dessus de lui (le fer haut au-dessus des cornes, un peu en arrière), se cambre et se tasse — longue attente — puis
# l'abat d'un coup vers l'avant : le fer mord la terre devant lui. Arrêt sur l'image : éclair doré de la terre, le sol
# se fend, des mottes et des éclats de roche giclent en éventail, la poussière roule des deux côtés. Puis il arrache la
# hache du sol et revient en garde.
RAISED = dict(farfront=1, G=(50.0, 68.0), ang=-98, sf=11, lean=-3, crouch=2, head=(-0.5, 1), tilt=-4, fsh=(-8, -1), nsh=(3, -1),
              ml=1, pg=1)
CHOP = dict(farfront=1, G=(60.0, 60.5), ang=21, sf=29, lean=4, crouch=3, head=(1, 2), tilt=6, fsh=(0, 0), nsh=(2, 1), ml=-1, pg=-1)
ATTACK = [
    (0, {}),
    (120, dict(G=(38.0, 86.0), ang=-40, sf=30, crouch=1, lean=-0.5, head=(0, 0.5), ml=0.5, farfront=1)),
    (280, dict(RAISED)),
    (560, dict(RAISED, G=(49.0, 67.0), ang=-101, lean=-3.4, crouch=2.3, tilt=-5)),
    (612, dict(farfront=1, G=(63.0, 60.0), ang=-34, sf=20, lean=1.5, crouch=1.6, head=(0.5, 1), tilt=0, fsh=(-4, 0), nsh=(2, 0), ml=0, pg=0)),
    (640, dict(CHOP)),
    (820, dict(CHOP, G=(60.0, 61.0), ang=21.5, crouch=3.2)),
    (940, dict(farfront=1, G=(54.0, 71.0), ang=4, sf=40, lean=2.5, crouch=2, head=(0.5, 1), tilt=2, nsh=(1, 0), ml=0.5, pg=0.5)),
    (1090, dict(G=(36.0, 85.5), ang=-7, sf=53, lean=0.8, crouch=1, ml=-0.3)),
    (1260, {}),
]
ATTACK_HIT = 640

# 3) L'attaque spéciale « Ruée du taureau » : il souffle par les naseaux, gratte deux fois le sol du sabot (la terre
# vole derrière lui), ses yeux s'embrasent ; à chaque coup de sabot le sol se fend d'une lueur dorée. Il baisse la tête,
# cornes en avant, se tasse — longue attente — puis fonce en labourant la terre (un sillon fendu, la poussière qui roule
# derrière, des mottes devant). Arrêt sur l'image à l'impact : éclair doré, la terre explose en couronne de dalles
# autour de l'ennemi, des rochers volent. Il relève la tête d'un coup (il encorne), revient en deux bonds lourds,
# retombe en soulevant la poussière et se remet en garde.
RAM = 84.0
LOW = dict(crouch=3, lean=-1, head=(4, 8), tilt=24, glow=2, ml=1, pg=1)
SPECIAL = [
    (0, {}),
    (140, dict(crouch=1, head=(0, 1), glow=0.3)),
    (240, dict(crouch=1, head=(0, 1), glow=0.6, legl=(3.4, 1.0))),
    (340, dict(crouch=1, head=(0, 1), glow=0.9, legl=(1.0, 6.0))),
    (440, dict(crouch=1.2, head=(0, 1), glow=1.2, legl=(3.4, 1.0))),
    (540, dict(crouch=1.4, head=(0, 1.5), glow=1.5, legl=(1.0, 6.0))),
    (640, dict(crouch=2, head=(0, 2), glow=1.8, legl=(0, 0))),
    (760, dict(LOW)),
    (960, dict(LOW, head=(4.4, 8.4), tilt=25)),
    (1010, dict(LOW, lean=4, shift=34, head=(6, 9), tilt=26, ml=2, pg=2)),
    (1060, dict(LOW, lean=4, shift=70, head=(6, 9), tilt=26, ml=2, pg=2)),
    (1100, dict(LOW, lean=3, shift=RAM, head=(7, 9), tilt=26, ml=-1, pg=-1)),
    (1290, dict(LOW, lean=3, shift=RAM, head=(7, 9.2), tilt=26.5, ml=-1, pg=-1)),
    (1400, dict(crouch=1, lean=1, shift=RAM, head=(1, -2), tilt=-8, glow=1.6, ml=1, pg=1)),
    (1500, dict(crouch=-1, lean=-2, shift=58, lift=7, head=(0, -1), tilt=-3, glow=1.2, ml=1.5, pg=1.5)),
    (1560, dict(crouch=1.5, lean=0, shift=42, lift=0, head=(0, 1), tilt=1, glow=1.0, ml=-1, pg=-1)),
    (1640, dict(crouch=-1, lean=-2, shift=20, lift=6, head=(0, -1), tilt=-2, glow=0.8, ml=1.5, pg=1.5)),
    (1720, dict(crouch=3, shift=0, lift=0, head=(0, 2), tilt=2, glow=0.5, ml=-1, pg=-1)),
    (1860, dict(crouch=1, head=(0, 1), glow=0.2)),
    (2020, {}),
]
SP_HIT = 1100


# ======================================================================== la respiration (en boucle, 2,4 s)

def scrape_curve(tau):
    """Le grattement du sabot avant (le lointain) : il le lève, le tire en arrière en raclant, le repose (tau en s)."""
    if not 0 <= tau <= 0.9:
        return (0.0, 0.0)
    keys = [(0, 0, 0), (0.18, 3.2, 1.0), (0.42, 1.0, 5.6), (0.6, 0.6, 2.4), (0.9, 0, 0)]
    ts = [k[0] for k in keys]
    return (monotone(ts, [k[1] for k in keys], tau), monotone(ts, [k[2] for k in keys], tau))


def idle_offsets(T):
    """Il inspire (le buste monte), les épaules roulent l'une après l'autre (la proche, puis la lointaine), la tête suit
    en retard ; à l'expiration il souffle par les naseaux et se tasse sur ses jambes ; la crinière ondule ; un cycle sur
    deux, il gratte le sol du sabot avant."""
    u = 2 * math.pi * T / 2.4
    br = 0.5 - 0.5 * math.cos(u)
    lh, lb = scrape_curve((T % 4.8) - 3.3)
    return dict(breath=br, crouch=0.6 * (0.5 - 0.5 * math.cos(u - 2.6)), heady=0.4 * math.sin(u - 0.7),
                tilt=-0.7 * math.sin(u - 0.9), rn=0.8 * (0.5 - 0.5 * math.cos(u - 0.4)), rf=0.7 * (0.5 - 0.5 * math.cos(u - 1.3)),
                ml=0.6 * math.sin(u - 1.6), pg=0.6 * math.sin(u + 0.4), llh=lh, llb=lb)


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
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['legl'] = (src['llh'] + (idl['llh'] if not act else 0), src['llb'] + (idl['llb'] if not act else 0))
    P['legn'] = (src['lnh'], src['lnb'])
    P['fsh'] = (src['fshx'], src['fshy'])
    P['nsh'] = (src['nshx'], src['nshy'])
    P['breath'] = w * idl['breath']
    P['ph'] = 2 * math.pi * T * 0.6 + (1.2 * T if act and action == 'special' else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.86 <= (T % 4.8) < 1.95) else 0.0
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=EINK, w=1.4, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def puff(fig, cx, cy, r, op=1.0, kind='dust'):
    """Une bouffée (poussière ocre ou vapeur gris tiède) : quelques boules réunies sous un contour doux, éclairées en haut
    à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    if kind == 'dust':
        stops, ink = [(0, '#fff2d4'), (0.5, '#dcb486'), (1, '#9a7058')], '#5a3e46'
    else:
        stops, ink = [(0, '#fbfaff'), (0.5, '#d4cee0'), (1, '#9e94b2')], SINK
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0, kind='steam'):
    """Une volute qui s'enroule (un ruban courbe qui s'affine), sous un contour doux."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    if kind == 'steam':
        gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fbfaff'), (0.6, '#d4cee0'), (1, '#9e94b2')])
        return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fff2d4'), (0.6, '#dcb486'), (1, '#9a7058')])
    return outlined([(sh, gr, 1)], ink='#5a3e46', w=1.0, op=op)


def hsh(i, k):
    """Un « hasard » fixe (même valeur à chaque image) : pour les formes des roches."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


def rock(fig, c, r, seed=0, rot=0.0, op=1.0, flat=1.0):
    """Un éclat de roche ou une motte : un polygone irrégulier à facettes (face éclairée en haut à droite, face d'ombre
    en bas à gauche), un seul contour."""
    if r < 0.25 or op <= 0.02:
        return ''
    n = 6
    pts = []
    for i in range(n):
        a = math.radians(rot + 360 * i / n + 25 * (hsh(seed, i) - 0.5))
        rr = r * (0.72 + 0.4 * hsh(seed, i + 7))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a) * flat))
    body = rpoly(pts, r * 0.18)
    # la face éclairée : le centre et les sommets tournés vers le haut à droite
    lit = sorted(range(n), key=lambda i: -((pts[i][0] - c[0]) * 0.6 - (pts[i][1] - c[1]) * 0.8))[:2]
    lit.sort()
    cc = (c[0] + r * 0.08, c[1] - r * 0.1)
    face = rpoly([cc, pts[lit[0]], pts[lit[1]]], r * 0.1)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, E[3]), (0.55, E[4]), (1, E[5])])
    return outlined([(body, gr, 1), (face, E[3], 0.85)], w=1.2, op=op)


def slab(fig, bx, h, w, lean=0.0, seed=0, op=1.0):
    """Une dalle de terre soulevée, plantée dans le sol : deux faces (la droite éclairée), un sommet cassé."""
    if h < 0.8 or op <= 0.02:
        return ''
    g = GR + 1.2
    tl = (bx - w * 0.5 + lean, g - h * (0.82 + 0.14 * hsh(seed, 1)))
    tm = (bx - w * 0.08 + lean * 1.05, g - h)
    tr = (bx + w * 0.45 + lean * 0.95, g - h * (0.7 + 0.2 * hsh(seed, 2)))
    bl, bm, br_ = (bx - w * 0.55, g), (bx - w * 0.02, g + 0.4), (bx + w * 0.55, g)
    left = rpoly([bl, tl, tm, bm], 0.5)
    right = rpoly([bm, tm, tr, br_], 0.5)
    gl = g_lin(fig, tm, bl, [(0, E[4]), (1, E[5])])
    gr = g_lin(fig, tr, bm, [(0, E[3]), (1, E[4])])
    crack = ribbon([lerp_(tm, bm, 0.15), (lerp_(tm, bm, 0.45)[0] + 0.8, lerp_(tm, bm, 0.45)[1]), lerp_(tm, bm, 0.8)], [0.1, 0.6, 0.1])
    top = ribbon([tl, tm, tr], [0.1, 0.9, 0.1])
    return outlined([(left, gl, 1), (right, gr, 1), (top, '#fff0cc', 0.6), (crack, E[6], 0.6)], w=1.3, op=op)


def lerp_(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def crack(fig, x, half, level, seed=0, op=1.0):
    """Le sol qui se fend au ras du sol (vu en perspective, la fissure est couchée) : une lueur dorée, le creux, le
    cœur d'or. level : 0..2."""
    if op <= 0.02 or half < 1:
        return []
    out = []
    gl = g_rad(fig, (x, GR), half * 1.4, [(0, E[1], 0.6 * op * min(1, 0.4 + 0.3 * level)), (1, E[2], 0)])
    out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR), fm(half * 1.4), fm(half * 0.28), gl))
    for side in (-1, 1):
        pts = [(x, GR + 0.2)]
        n = 4
        for i in range(1, n + 1):
            t = i / n
            pts.append((x + side * half * t, GR + 0.2 + (1.2 * hsh(seed + side, i) - 0.6) * (1 - t) + 0.25 * t))
        w = 1.0 + 0.4 * level
        sh = ribbon(pts, [w] + [w * (1 - i / n) + 0.1 for i in range(1, n)] + [0.05])
        core = ribbon(pts, [w * 0.45] + [w * 0.45 * (1 - i / n) + 0.05 for i in range(1, n)] + [0.02])
        out.append('<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
            op, sh.d(), E[6], core.d(), E[1] if level < 2 else E[0]))
    return out


def pop(fig, c, r, facing=0.0, op=1.0):
    """Un éclat d'impact doré (la terre répond) : un coeur et des lobes arrondis (plus gros vers « facing »), coeur
    blanc, bord or puis ambre ; un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, [(0, '#fffef4'), (0.35, E[0]), (0.65, E[1]), (0.9, E[2]), (1, '#b86a2a')])
    return outlined([(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes], ink='#6a3a1e', w=1.4, op=op)


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


def steel_trail(fig, C, R, a0, a1, w, op=1.0):
    """La traînée du fer : un croissant d'acier clair qui s'efface vers l'arrière, bordé de poussière dorée."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 1.0, a0, a1, w * 0.3)
    g1 = g_lin(fig, pa, pb, [(0, '#c8d0ea', 0), (1, '#f4f6ff', 0.8 * op)])
    g2 = g_lin(fig, pa, pb, [(0, E[2], 0), (0.6, E[1], 0.8 * op), (1, E[0], op)])
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


# ---- la vapeur des naseaux : deux jets qui descendent en avant et s'enroulent

def steam(fig, ctx, k, big=1.0):
    if not 0 < k < 1:
        return
    o = env(k, 0, 0.15, 0.55, 1)
    for j, n in enumerate(ctx['nostrils']):
        kk = max(0.0, min(1.0, k - 0.08 * j))
        x = n[0] + (2 + 6 * kk) * big
        y = n[1] + (1.5 + 5 * kk) * big
        fig.fx_front.append(puff(fig, x, y, (0.7 + 1.4 * kk) * big * (1 - 0.25 * j), op=0.8 * o, kind='steam'))
        if kk > 0.3:
            fig.fx_front.append(curl(fig, (x + 2.4 * big, y + 1.6 * big), 1.5 * big, 160, -260, 0.9 * big, op=0.7 * o))


# ---- le sabot avant qui gratte le sol : des mottes qui volent vers l'arrière, un peu de poussière

def scrape_fx(fig, ctx, tau, seed=0, glow_lv=-1):
    """tau : le temps (s) depuis le début d'un grattement (0,9 s)."""
    if not 0 < tau < 1.1:
        return
    hx, hy = ctx['hooves'][1]
    hx0 = hx
    # quand le sabot racle (vers l'arrière), la terre gicle derrière lui
    if tau > 0.2:
        tt = tau - 0.2
        for i, (vx, vy, r) in enumerate(((-46, -38, 1.3), (-60, -24, 0.9), (-34, -50, 1.0), (-70, -14, 0.7), (-52, -44, 0.6))):
            x, y = ballistic((hx0 - 6, GR - 1.5), (vx, vy), 160, tt)
            if y < GR - 0.5 and tt < 0.7:
                fig.fx_front.append(rock(fig, (x, y), r, seed=seed + i, rot=tt * 400 + i * 50, op=1 - tt / 0.7))
        o = env(tau, 0.2, 0.3, 0.55, 1.0)
        fig.fx_back.append(puff(fig, hx0 - 10 - 8 * tt, GR - 3 - 2 * tt, 2.4 + 2.2 * tt, op=0.85 * o))
        fig.fx_front.append(puff(fig, hx0 - 4 - 4 * tt, GR - 1.8, 1.8 + 1.0 * tt, op=0.8 * o))
    if glow_lv >= 0 and tau > 0.36:
        o = env(tau, 0.36, 0.42, 0.7, 1.1)
        for x_, hf in ((ctx['hooves'][0][0], 9), (ctx['hooves'][1][0], 11)):
            fig.fx_back.extend(crack(fig, x_ + 2, hf + 3 * glow_lv, glow_lv, seed=int(x_) + seed, op=o))


# ---- l'attaque de base

HIT_AT = {}
IMP_AT = {}


def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        # le fer qui tombe : un croissant d'acier autour des poings, bordé de poussière dorée
        if 585 <= tl <= 720:
            C = ctx['G']
            hp = ctx['head_pt']
            R = math.dist(C, hp) + 6
            a_to = math.degrees(math.atan2(hp[1] - C[1], hp[0] - C[0]))
            a_from = -120.0
            e = env(tl, 585, 610, 650, 720)
            if a_to > a_from:
                fig.fx_back.append(steel_trail(fig, C, R + 8, a_from, a_to, 20 * e + 2, op=e))
                fig.fx_back.append(steel_trail(fig, C, R - 8, a_from + 12, a_to, 6 * e + 1, op=0.8 * e))
        tau = (tl - ATTACK_HIT) / 1000.0
        c = HIT_AT.get('c')
        if tau >= -0.01 and c:
            cx = c[0]
            # l'éclair doré au point d'impact (arrêt sur l'image)
            fl = env(tau, -0.01, 0.0, 0.05, 0.16)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(GR - 4), fm(80), g_rad(
                    fig, (cx, GR - 4), 80, [(0, '#fffef0', 0.8 * fl), (0.15, E[0], 0.45 * fl), (0.5, E[1], 0.12 * fl), (1, E[2], 0)])))
            e = env(tau, 0, 0.03, 0.14, 0.34)
            if e > 0:
                fig.fx_front.append(pop(fig, (cx + 2, GR - 4), 7.5 * (0.6 + 0.4 * e), facing=-60, op=e))
            # le sol se fend devant et derrière le fer, une lueur dorée qui pâlit
            co = env(tau, 0, 0.04, 0.3, 0.7)
            fig.fx_back.extend(crack(fig, cx, 14 + 8 * min(1, tau * 6), 2, seed=3, op=co))
            # deux petites dalles qui se soulèvent de part et d'autre du fer
            so = env(tau, 0, 0.05, 0.3, 0.55)
            k = min(1.0, tau / 0.08)
            fig.fx_back.append(slab(fig, cx - 9, 7 * k, 6, lean=-1.6, seed=5, op=so))
            fig.fx_front.append(slab(fig, cx + 10, 9 * k, 7, lean=2.2, seed=6, op=so))
            # mottes et éclats de roche en éventail (vers l'avant surtout), qui retombent
            for i, (vx, vy, r) in enumerate(((40, -70, 1.8), (64, -48, 1.4), (22, -84, 1.2), (80, -30, 1.1), (-30, -64, 1.3),
                                             (-50, -40, 0.9), (52, -88, 0.8), (96, -50, 0.8), (8, -96, 0.7), (-16, -80, 0.7))):
                if tau < 0.85:
                    x, y = ballistic((cx, GR - 3), (vx, vy), 190, tau)
                    if y < GR - 0.6:
                        fig.fx_front.append(rock(fig, (x, y), r, seed=i + 11, rot=tau * 500 + i * 40, op=min(1, 2.4 * (0.85 - tau))))
            # la poussière qui roule des deux côtés
            if 0.04 < tau < 1.0:
                k = (tau - 0.04) / 0.96
                o = env(k, 0, 0.12, 0.5, 1)
                for side, big in ((-1, 1.0), (1, 0.9)):
                    fig.fx_back.append(puff(fig, cx + side * (6 + 18 * k), GR - 3.5 - 3 * k, (3 + 3.6 * k) * big, op=0.9 * o))
                    fig.fx_front.append(puff(fig, cx + side * (3 + 10 * k), GR - 2.0, (2 + 2.2 * k) * big, op=0.85 * o))
                fig.fx_back.append(curl(fig, (cx + 14 + 10 * k, GR - 10 - 8 * k), 3.4 + 1.6 * k, 200 + 90 * k, 280, 2.2, op=0.8 * o, kind='dust'))
        # au retour, il arrache le fer : quelques gravillons
        if 900 < tl < 1150 and c:
            tt = (tl - 900) / 1000.0
            for i, (vx, vy) in enumerate(((-20, -40), (16, -46), (-6, -54))):
                x, y = ballistic((c[0], GR - 2), (vx, vy), 160, tt)
                if y < GR - 0.5:
                    fig.fx_front.append(rock(fig, (x, y), 0.7, seed=30 + i, rot=tt * 600, op=1 - tt / 0.25))
    return f


# ---- l'attaque spéciale

def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        # la vapeur : il souffle fort avant de gratter, puis en baissant la tête
        if 0 < t < 520:
            steam(fig, ctx, t / 520, big=1.5)
        if 640 < t < 1000:
            steam(fig, ctx, (t - 640) / 360, big=1.7)
        # deux coups de sabot : la terre vole, le sol se fend d'or (de plus en plus fort)
        for j, t0 in enumerate((170, 370)):
            scrape_fx(fig, ctx, (t - t0) / 1000.0, seed=10 * j, glow_lv=j + 1)
        # sous ses sabots pendant l'attente : la lueur dorée de la terre
        lo = env(t, 700, 760, 960, 1010)
        if lo > 0:
            for x_, hf in ((ctx['hooves'][0][0], 10), (ctx['hooves'][1][0], 12)):
                fig.fx_back.extend(crack(fig, x_ + 2, hf + 5, 2, seed=int(x_), op=lo))
        # la ruée : le sillon labouré derrière ses sabots, la poussière qui roule, des mottes devant
        x_start = 100.0
        if 960 < t < 1700:
            hoof = ctx['hooves'][1][0] + 12
            fo = env(t, 960, 1000, 1350, 1700)
            if hoof > x_start + 2:
                pts = [(x_start, GR + 0.4), ((x_start + hoof) / 2, GR + 0.6), (hoof, GR + 0.5)]
                fig.fx_back.append('<path d="%s" fill="%s" opacity="%g"/>' % (
                    ribbon(pts, [0.3, 2.2, 1.6]).d(), g_lin(fig, (x_start, GR), (hoof, GR), [(0, E[6]), (0.75, E[5]), (1, E[1])]), fo))
            dk = env(t, 970, 1010, 1150, 1500)
            if dk > 0:
                sx = P['shift']
                for i in range(5):
                    tt = i / 4
                    x = x_start - 6 + (sx - 4) * (1 - tt) * 0.85 + 20
                    r = (4 + 6 * tt) * (0.6 + 0.4 * dk)
                    fig.fx_back.append(puff(fig, x - 30 * tt, GR - 3 - 4 * tt, r, op=0.9 * dk))
                fig.fx_front.append(puff(fig, ctx['hooves'][0][0] - 6, GR - 2.5, 3.6 * dk, op=0.85 * dk))
                fig.fx_front.append(puff(fig, ctx['hooves'][1][0] + 8, GR - 2.0, 3.0 * dk, op=0.85 * dk))
        # l'impact : l'éclair doré, la couronne de dalles autour de l'ennemi, les rochers qui volent, la poussière
        cx = IMP_AT.get('x', 214.0)
        if t >= SP_HIT - 6:
            tg = t - SP_HIT
            fl = env(tg, -6, 0, 40, 170)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(GR - 24), fm(150), g_rad(
                    fig, (cx, GR - 24), 150, [(0, '#fffef0', 0.85 * fl), (0.12, E[0], 0.5 * fl), (0.45, E[1], 0.15 * fl), (1, E[2], 0)])))
            if tg >= 0:
                tau = tg / 1000.0
                e = env(tau, 0, 0.03, 0.16, 0.36)
                if e > 0:
                    fig.fx_front.append(pop(fig, (cx - 2, GR - 26), 10 * (0.6 + 0.4 * e), facing=-90, op=e))
                co = env(tau, 0, 0.05, 0.5, 0.9)
                fig.fx_back.extend(crack(fig, cx, 26 + 10 * min(1, tau * 5), 2, seed=7, op=co))
                # la couronne de dalles : elles jaillissent tout autour (celles de derrière plus petites), puis retombent
                rise = min(1.0, tau / 0.09)
                so = env(tau, 0, 0.04, 0.42, 0.75)
                sink = max(0.0, (tau - 0.42) / 0.33)
                for i, (dx, h, w, ln, front) in enumerate(((-24, 12, 8, -3.4, False), (-13, 18, 9, -2.0, False), (0, 22, 10, 0.4, False),
                                                           (13, 17, 9, 2.4, False), (25, 12, 8, 3.6, False),
                                                           (-18, 10, 8, -3.0, True), (19, 11, 8, 3.2, True))):
                    hh = h * rise * (1 - 0.7 * sink)
                    (fig.fx_front if front else fig.fx_back).append(slab(fig, cx + dx, hh, w, lean=ln, seed=40 + i, op=so))
                # des rochers qui volent haut et retombent
                for i, (vx, vy, r) in enumerate(((-40, -110, 2.4), (30, -124, 2.8), (62, -90, 2.0), (-70, -80, 1.8),
                                                 (90, -60, 1.5), (-12, -140, 1.4), (46, -150, 1.2), (-90, -50, 1.2))):
                    if tau < 1.3:
                        x, y = ballistic((cx, GR - 12), (vx, vy), 210, tau)
                        if y < GR - 0.8:
                            fig.fx_front.append(rock(fig, (x, y), r, seed=60 + i, rot=tau * 360 + i * 30, op=min(1, 2.2 * (1.3 - tau))))
                # la poussière qui monte et roule
                if 0.05 < tau < 1.4:
                    k = (tau - 0.05) / 1.35
                    o = env(k, 0, 0.1, 0.5, 1)
                    for dx, dy, r in ((-22, -4, 5), (22, -5, 5.5), (0, -14, 6.5), (-10, -26, 4.5), (12, -30, 4.0)):
                        fig.fx_back.append(puff(fig, cx + dx * (1 + 0.8 * k), GR + dy - 8 * k, r * (0.7 + 0.8 * k), op=0.85 * o))
                    fig.fx_back.append(curl(fig, (cx + 30 + 8 * k, GR - 30 - 10 * k), 4 + 2 * k, 200 + 90 * k, 280, 2.6, op=0.8 * o, kind='dust'))
                    fig.fx_back.append(curl(fig, (cx - 30 - 8 * k, GR - 26 - 10 * k), 3.6 + 2 * k, 340 - 90 * k, -280, 2.4, op=0.7 * o, kind='dust'))
        # les deux bonds lourds et la retombée : la poussière sous les sabots
        for t0, xo in ((1560, 42.0), (1720, 0.0)):
            k = (t - t0) / 500.0
            if 0 < k < 1:
                o = env(k, 0, 0.12, 0.45, 1)
                for x_ in (40 + xo, 90 + xo):
                    fig.fx_back.append(puff(fig, x_ - 12 - 6 * k, GR - 3 - 1.5 * k, 3 + 2.5 * k, op=0.85 * o))
                    fig.fx_front.append(puff(fig, x_ + 12 + 6 * k, GR - 2.5 - 1.2 * k, 2.6 + 2 * k, op=0.8 * o))
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
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.12))
    im.alpha_composite(glow)
    return im


def shadow_layer(w, h, view, shift, lift, floor_y=GR):
    """L'ombre douce au sol sous le héros (elle suit ses pas et pâlit quand il bondit)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (68 + shift - x0) * k
    s = max(0.45, 1 - lift / 40)
    sd.ellipse([cx - 40 * k * s, fy - 2.8 * k * s, cx + 40 * k * s, fy + 2.8 * k * s], fill=(10, 4, 24, int(150 * s)))
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
            HIT_AT['c'] = K.build(pose=Ph).ctx['edge_lo']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'x' not in IMP_AT:
            Ph, _ = pose_at(t0 + SP_HIT / 1000.0, act, t0)
            cx_ = K.build(pose=Ph).ctx
            IMP_AT['x'] = max(cx_['horns'][1][0], cx_['muzzle'][0]) + 8
        fx = [fx_special(tl)]
    else:
        # au repos : à l'expiration, la vapeur sort des naseaux ; un cycle sur deux, il gratte le sol du sabot
        k = ((T % 2.4) - 1.25) / 0.95
        tau = (T % 4.8) - 3.3
        fx = [lambda fig, ctx: steam(fig, ctx, k, big=1.1), lambda fig, ctx: scrape_fx(fig, ctx, tau, seed=3)]
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
        extra = []
        for x in sys.argv[sys.argv.index('--planche') + 1:]:
            try:
                extra.append(float(x))
            except ValueError:
                break
        moments = extra or [1.5, 3.7, a_s + 0.12, a_s + 0.3, a_s + 0.56, a_s + 0.6, a_s + 0.64, a_s + 0.7, a_s + 0.9, a_s + 1.05,
                            s_s + 0.25, s_s + 0.45, s_s + 0.8, s_s + 1.03, s_s + 1.12, s_s + 1.25, s_s + 1.42, s_s + 1.5,
                            s_s + 1.64, s_s + 1.75]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P['shift'], P['lift']))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = sys.argv[sys.argv.index('--sortie') + 1] if '--sortie' in sys.argv else os.path.join(TMP, 'planche.png')
        sheet.save(dst)
        print('planche :', dst)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P['shift'], P['lift']))
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
