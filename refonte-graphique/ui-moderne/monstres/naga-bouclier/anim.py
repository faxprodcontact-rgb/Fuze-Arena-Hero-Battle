# Le naga au bouclier vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# naga-bouclier/build.py) — respiration lourde, attaque de base « Coup de bouclier », attaque spéciale « Séisme du
# trident » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/naga-bouclier/anim.py            # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/naga-bouclier/anim.py --planche [t…]   # planche d'instants (contrôle)
#
# Méthode (comme Kael et Sarvik, ../../heros/kael/anim.py, ../../heros/sarvik/anim.py) : le dessin (naga-bouclier.py)
# est fait de morceaux ; chaque image le redessine dans une POSE. Un serpent ne marche pas : tout part des anneaux. Le
# buste se dresse (rise : le tronc s'étire) ou se tasse, il se penche (lean : il tourne autour de la taille) ; le
# bouclier suit le buste et part en avant (sh) ; le trident reste planté (le poing le tient : le bras se plie par
# cinématique inverse, coude toujours bas) ou se soulève (ty) ; la tête tourne d'un seul bloc ; le crochet de la queue
# se balance, une bosse de muscle court le long de la boucle de derrière. Poses clés reprises du pixel art (mêmes
# gestes, même rythme), reliées par des courbes douces sans dépassement. Effets (roche, poussière, venin vert) :
# dégradés, un seul contour, courbes ; aucun flou SVG, aucun rayon droit répété.
import importlib.util
import json
import math
import os
import random
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
_spec = importlib.util.spec_from_file_location('naga', os.path.join(HERE, 'naga-bouclier.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'naga-bouclier')
TMP = os.environ.get('NAGA_TMP') and os.path.join(os.environ['NAGA_TMP'], '_images') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-20, -28, 288, 162)          # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
GR = K.GRD
VEN = K.VEN
GINK = '#0c2c2a'                     # le contour du venin
ROCK = ['#f2e0b6', '#c8a070', '#8e664a', '#5e4046']     # roche : lumière, ocre, ombre, creux (palette du pixel art)
RINK = '#3e2a36'                     # le contour de la roche et de la poussière (jamais du noir)
DUST = ['#f8ecd8', '#dcc6a6', '#ac927a', '#705a5e']
GOLDS = ['#fffbe0', '#ffe080', '#fcc844', '#e09030']
ENEMY_X = 208.0                      # l'ennemi en face (comme le pixel art)

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


NUM = ['rise', 'lean', 'headx', 'heady', 'tilt', 'jaw', 'tg', 'flare', 'shx', 'shy', 'shr', 'ty', 'trot', 'slide',
       'hook', 'crest']
BASE = dict(jaw=0.55, tg=1.0)


def flat(k):
    d = {n: BASE.get(n, 0.0) for n in NUM}
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'sh':
            d['shx'], d['shy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Coup de bouclier » (pixel : ATTAQUE, 1230 ms). Le mur qui frappe : il se dresse et se ramasse en arrière sur ses
# anneaux, le bouclier ramené contre la poitrine, la tête rentrée derrière son bord, la queue qui se relève (longue
# attente) ; puis tout le corps se détend comme un ressort (il prend appui sur le trident planté), le buste plonge et
# le bouclier part d'un coup (croissant de poussière derrière lui) ; impact : arrêt sur l'image, éclat doré, éclats de
# pierre, le sol tremble ; il encaisse le recul, ramène le bouclier et revient en garde.
ATTACK = [
    (0, {}),
    (100, dict(rise=1, lean=-1, sh=(-1, 0), head=(0, 0.8), hook=1, jaw=0.4)),
    (210, dict(rise=3, lean=-3, sh=(-2.5, -1), shr=-3, head=(-1.4, 1.4), hook=2, tg=0, jaw=0.3, tilt=-2)),
    (470, dict(rise=4, lean=-4, sh=(-3, -1.2), shr=-4, head=(-2, 1.8), hook=2.4, tg=0, jaw=0.25, tilt=-3)),
    # la détente : le buste plonge, le bouclier part
    (525, dict(rise=0, lean=3.4, sh=(5, 0), shr=2, head=(1.4, 0), hook=-0.5, tg=2.2, jaw=0.9, tilt=2, slide=-0.6)),
    # l'impact : arrêt sur l'image
    (590, dict(rise=-1, lean=4.4, sh=(8.5, 1), shr=4, head=(1.6, 0.4), hook=-1.2, tg=2.4, jaw=1.0, tilt=3, slide=-0.8)),
    (760, dict(rise=-1, lean=4.2, sh=(8.0, 1), shr=3.6, head=(1.5, 0.4), hook=-1.0, tg=2.3, jaw=0.95, tilt=2.8, slide=-0.8)),
    # le recul : il ramène le bouclier
    (860, dict(rise=0, lean=3, sh=(4.4, 0.5), shr=2, head=(0.6, 0.2), tg=1.4, jaw=0.7, tilt=1.4, slide=-0.4)),
    (970, dict(lean=1, sh=(1.5, 0), shr=0.6, head=(0, -0.4), tg=1.1, jaw=0.6, hook=0.4)),
    (1100, dict(lean=0.2, sh=(0.3, 0), hook=0.2)),
    (1240, {}),
]
AT_BRACE = 210
AT_LUNGE = (480, 600)          # le bouclier part : croissant de poussière derrière lui
AT_HIT = 590                   # l'impact

# 3) « Séisme du trident » (pixel : SPECIALE, 2400 ms). Il se dresse de toute sa hauteur et arrache le trident du sol
# (le poing le monte haut), le bouclier levé, le crochet de la queue dressé, la crête déployée ; la gueule siffle, ses
# yeux s'allument de venin vert, une lueur verte s'enroule autour des pointes du trident, des cailloux se soulèvent
# (longue attente). Puis il s'abat de tout son poids : le talon du trident s'enfonce, le bouclier frappe la terre, la
# queue fouette le sol — arrêt sur l'image, éclat. La terre se fend d'une fissure de venin vert qui court vers la
# droite, des éclats de roche jaillissent l'un après l'autre jusqu'à l'ennemi et au-delà (le plus gros sous l'ennemi),
# s'effritent en blocs qui retombent ; il arrache le trident, le replante et revient en garde.
_F = dict(flare=1.0)
SPECIAL = [
    (0, {}),
    (110, dict(rise=1, lean=-1, ty=-3, sh=(0, -1), head=(0, 0.8), hook=0.6, flare=0.2, slide=0.4)),
    (230, dict(rise=3, lean=-2, ty=-8, sh=(-1, -2), shr=-2, head=(0, 0), hook=1.4, flare=0.6, crest=0.5, tg=2.2, jaw=0.8)),
    (350, dict(rise=5, lean=-2, ty=-13, sh=(-1, -3), shr=-3, head=(-0.6, -1), hook=2, crest=1, tg=2.6, jaw=0.9, tilt=-2, **_F)),
    (660, dict(rise=5.4, lean=-3, ty=-14, sh=(-1.2, -3.2), shr=-3.5, head=(-1, -1.2), hook=2.2, crest=1, tg=2.4, jaw=0.95, tilt=-3, **_F)),
    # il s'abat
    (715, dict(rise=1, lean=1.6, ty=-5, sh=(1, 1), shr=0, head=(0.6, 0.4), hook=0.4, crest=0.8, tg=2, jaw=1, tilt=1, **_F)),
    (780, dict(rise=-2, lean=2.6, ty=2.6, sh=(2, 5.5), shr=3, head=(1, 1.6), hook=-1.8, crest=0.7, tg=2.4, jaw=1, tilt=3, **_F)),
    (930, dict(rise=-2, lean=2.5, ty=2.6, sh=(2, 5.2), shr=2.8, head=(1, 1.5), hook=-1.4, crest=0.6, tg=2.2, jaw=0.95, tilt=2.8, **_F)),
    # la terre se fend, les éclats jaillissent
    (1080, dict(rise=-1, lean=2, ty=2.6, sh=(2, 2.5), shr=1.6, head=(1, 0.6), hook=-0.6, crest=0.4, tg=1.8, jaw=0.85, tilt=2, **_F)),
    (1500, dict(rise=-0.8, lean=1.8, ty=2.6, sh=(1.6, 2), shr=1.2, head=(0.8, 0.4), crest=0.3, tg=1.4, jaw=0.75, tilt=1.6, flare=0.6)),
    # il arrache le trident et le replante, retour en garde
    (1760, dict(rise=0.4, lean=0.6, ty=-2.6, sh=(0.6, 0.6), shr=0.4, head=(0, -0.6), tg=1.1, jaw=0.6, flare=0.2)),
    (1920, dict(rise=0, lean=0.2, ty=0.4, sh=(0.2, 0), tg=1.0, flare=0.0)),
    (2100, dict(ty=0, hook=0.4)),
    (2400, {}),
]
SP_SLAM = 780
SPIKES = [  # (x, hauteur, largeur, penché, naissance en ms) : le long du sol, le plus gros sous l'ennemi
    (125.0, 14, 12, 1.5, 830), (142.0, 20, 14, 2.0, 880), (161.0, 26, 16, 1.0, 920), (182.0, 31, 18, 2.0, 980),
    (ENEMY_X - 1, 46, 27, 1.5, 1080), (231.0, 29, 17, -1.0, 1100), (246.0, 19, 12, -1.5, 1160)]
CRACK_SPEED = 0.19             # px du dessin par ms : la fissure court vers la droite

# ======================================================================== la respiration (en boucle, 2 s : lourde)
LOOP = 2.0


def idle_offsets(T):
    u = 2 * math.pi * T / LOOP
    return dict(breath=0.5 - 0.5 * math.cos(u), rise=0.35 * math.sin(u - 0.3), heady=-0.4 * math.sin(u - 1.0),
                headx=0.25 * math.sin(u - 0.7), tilt=0.7 * math.sin(u - 0.9), lean=0.25 * math.sin(u - 1.2),
                hook=1.0 * math.sin(u + 1.0), slide=0.35 * math.sin(u - 1.1), shy=0.35 * math.sin(u - 0.8),
                shr=0.4 * math.sin(u - 1.0), tg=0.95 * math.sin(2 * u + 0.6), jaw=0.06 * math.sin(u - 0.4),
                crest=0.15 * math.sin(u - 1.3))


def pose_at(T, action=None, t0=0.0):
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
    Q = {}
    for n in NUM:
        Q[n] = src[n] + w * idl.get(n, 0.0)
    Q['tg'] = max(0.0, Q['tg'])
    P = {n: Q[n] for n in NUM if n not in ('headx', 'heady', 'shx', 'shy')}
    P['breath'] = w * idl['breath']
    P['head'] = (Q['headx'], Q['heady'])
    P['sh'] = (Q['shx'], Q['shy'])
    P['hump'] = ((T % LOOP) / LOOP * 1.4 - 0.2, 0.9 * w)
    P['blink'] = 1.0 if (w > 0.95 and 2.6 <= (T % 3.7) < 2.72) else 0.0
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def outlined(shapes_fills, ink=GINK, w=1.0, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                     '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


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


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def radial(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, ry or r, stops)


def glow(fig, c, r, color, op, ry=None):
    if op <= 0.01 or r <= 0.1:
        return ''
    ry = ry or r
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(ry),
                                                                    radial(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)], ry))


def taper_arc(c, r, a0, a1, w, n=24, wy=1.0):
    """Un croissant effilé : un arc (centre c, rayon r) de l'angle a0 à a1 (degrés), épais au milieu, pointu aux bouts."""
    pts, ws = [], []
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0 + (a1 - a0) * u)
        pts.append((c[0] + r * math.cos(a), c[1] + r * wy * math.sin(a)))
        ws.append(max(0.08, w * math.sin(math.pi * u) ** 0.8))
    return ribbon(pts, ws)


def dust(fig, cx, cy, r, op=1.0, seed=0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    balls = [(cx, cy, r)]
    for i in range(3):
        a = rnd.uniform(0, 2 * math.pi)
        balls.append((cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.45 + 0.2 * r, r * rnd.uniform(0.55, 0.75)))
    gr = lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), RINK, RINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.7"/>' % (fm(cx + r * 0.3), fm(cy - r * 0.35), fm(r * 0.38), DUST[0])
    return '<g opacity="%g">%s%s%s</g>' % (max(0.0, min(1.0, op)), sil, col, hi)


def pebble(fig, c, r, ang=0.0, seed=0, op=1.0):
    """Un éclat de pierre à facettes : un contour, la facette du haut à droite éclairée."""
    if r < 0.2 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    n = 6
    pts = []
    for i in range(n):
        a = math.radians(ang) + 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25)
        rr = r * rnd.uniform(0.75, 1.1)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a) * 0.85))
    sh = sm(pts, sharp=tuple(range(n)), t=0.3)
    lit = sm([c, pts[4], pts[5], pts[0]], sharp=(0, 1, 2, 3), t=0.3)
    return outlined([(sh, ROCK[1], 1), (lit, ROCK[0], 0.85), (sm([c, pts[1], pts[2], pts[3]], sharp=(0, 1, 2, 3), t=0.3), ROCK[2], 0.7)],
                    ink=RINK, w=0.7, op=op)


def pop(fig, c, r, op=1.0, seed=0):
    """L'éclat de l'impact : une fleur dorée à lobes ronds inégaux (pas de rayons), un coeur blanc, un contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    n = 10
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.12, 0.12)
        rr = r * (rnd.uniform(0.95, 1.12) if i % 2 == 0 else rnd.uniform(0.74, 0.84))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = sm(pts, t=1.0)
    gr = radial(fig, c, r * 1.1, [(0, GOLDS[0]), (0.45, GOLDS[1]), (0.8, GOLDS[2]), (1, GOLDS[3])])
    return outlined([(sh, gr, 1), (ellipse(c[0] + r * 0.08, c[1] - r * 0.06, r * 0.42, r * 0.38), '#ffffff', 0.95)], ink='#6a3a1e', w=1.0, op=op)


def spike(fig, x, h, w, lean, seed=0, op=1.0):
    """Un éclat de roche qui jaillit du sol : une lame à facettes (deux pans : l'un éclairé à droite, l'autre dans
    l'ombre), une veine de venin vert au pied, un contour. h = hauteur actuelle."""
    if h < 0.4 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    g = GR + 0.6
    tip = (x + lean * h / 10, g - h)
    sl = (x - w * 0.5, g)
    sr = (x + w * 0.5, g)
    ml = (x - w * 0.34 + lean * h / 30, g - h * rnd.uniform(0.42, 0.55))
    mr = (x + w * 0.3 + lean * h / 25, g - h * rnd.uniform(0.5, 0.62))
    ridge = (x + w * 0.06 + lean * h / 18, g - h * 0.35)
    body = sm([sl, ml, tip, mr, sr], sharp=(0, 1, 2, 3, 4), t=0.3)
    lit = sm([tip, mr, sr, (x + w * 0.08, g), ridge], sharp=(0, 1, 2, 3, 4), t=0.3)
    shade = sm([sl, ml, tip, ridge, (x - w * 0.05, g)], sharp=(0, 1, 2, 3, 4), t=0.3)
    vein = ribbon([(x - w * 0.3, g - 0.2), (x - w * 0.05, g - h * 0.18), (x + w * 0.02, g - h * 0.3)], [0.1, max(0.4, w * 0.07), 0.1])
    parts = [(body, ROCK[1], 1), (lit, lin(fig, tip, sr, [(0, ROCK[0]), (1, ROCK[1])]), 1), (shade, ROCK[2], 0.9),
             (ribbon([lerp(tip, mr, 0.15), lerp(tip, mr, 0.55), mr], [0.05, 0.45, 0.1]), '#fff6e0', 0.7),
             (vein, VEN[1], 0.9)]
    return outlined(parts, ink=RINK, w=1.0, op=op)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def curl(fig, c, r, a0, turn, w, op=1.0, cw=False):
    """Une volute de venin : une spirale effilée (épaisse au départ, fine au bout), un contour."""
    if op <= 0.02:
        return ''
    n = 26
    pts, ws = [], []
    sg = -1 if cw else 1
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0 + sg * turn * u)
        rr = r * (1 - 0.6 * u)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        ws.append(max(0.1, w * (1 - u) ** 0.8))
    sh = ribbon(pts, ws)
    gr = lin(fig, pts[0], pts[-1], [(0, VEN[2]), (0.5, VEN[1]), (1, VEN[0])])
    return outlined([(sh, gr, 1)], w=0.8, op=op)


def crack(fig, x0, x1, op=1.0, seed=3):
    """La fissure de venin qui court sur le sol : une fente sombre en lentille aplatie (vue de 3/4), un coeur vert
    brûlant, une lueur verte douce au-dessus (dégradé, pas de flou)."""
    if x1 - x0 < 1 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    n = max(4, int((x1 - x0) / 7))
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, GR + 0.9 + (0.5 * math.sin(i * 1.7 + seed) if 0 < i < n else 0)))
    ws = [0.1] + [rnd.uniform(1.0, 1.6) for _ in range(n - 1)] + [0.1]
    out = glow(fig, ((x0 + x1) / 2, GR), (x1 - x0) / 2 + 4, VEN[1], 0.35 * op, ry=5)
    core = ribbon(pts, [w_ * 0.4 for w_ in ws])
    return out + outlined([(ribbon(pts, ws), '#3e2a36', 1), (core, VEN[1], 1)], ink=RINK, w=0.6, op=op)


# ---- l'attaque

def fx_attack(tl):
    def f(fig, ctx):
        back, front = [], []
        sh = ctx['shield']
        fr = sh['front']
        # il prend appui : un peu de poussière glisse sous la grande boucle
        a = env(tl, AT_BRACE - 60, AT_BRACE, AT_BRACE + 60, AT_BRACE + 300)
        if a:
            k = ease((tl - AT_BRACE + 60) / 360)
            front.append(dust(fig, 8 - 3 * k, GR - 1.6, 2.2 + 1.2 * k, a * 0.9, seed=1))
            front.append(dust(fig, 16 - 2 * k, GR - 1.2, 1.6 + 0.8 * k, a * 0.8, seed=2))
        # le bouclier part : un croissant de poussière derrière lui
        a = env(tl, AT_LUNGE[0], AT_LUNGE[0] + 30, AT_LUNGE[1] - 40, AT_LUNGE[1] + 60)
        if a:
            c = (fr[0] - 22, fr[1] + 2)
            gr = lin(fig, (c[0] - 4, c[1]), (c[0] + 20, c[1]), [(0, DUST[1], 0.0), (0.6, DUST[0], 0.55), (1, '#ffffff', 0.85)])
            back.append('<g opacity="%g"><path d="%s" fill="%s"/></g>' % (a, taper_arc(c, 20, -42, 42, 4.2, wy=1.4).d(), gr))
        # l'impact : l'éclat doré, la poussière en chou-fleur, les éclats de pierre, le sol qui tremble
        t = tl - AT_HIT
        if -10 <= t <= 520:
            u = max(0.0, t) / 520
            hit = (fr[0] + 2.0, fr[1])
            front.append(glow(fig, hit, 16 * (0.6 + 0.6 * ease(u * 3)), '#fff0b0', 0.55 * (1 - ease(u * 1.4))))
            front.append(pop(fig, hit, 7.5 * ease(t / 60 + 0.2) * (1 - 0.6 * ease((t - 120) / 200)), op=1 - ease((t - 150) / 140), seed=5))
            for i, (dx, dy, r) in enumerate(((4, -5, 3.2), (6, 3, 3.6), (2, 9, 2.6), (8, -12, 2.2))):
                k = ease(t / 300)
                front.append(dust(fig, hit[0] + dx * (0.6 + k), hit[1] + dy * (0.6 + 0.7 * k) - 2 * k, r * (0.6 + 0.6 * k),
                                  op=1 - ease((t - 200) / 300), seed=10 + i))
            for i, (vx, vy, r) in enumerate(((0.05, -0.06, 1.3), (0.07, -0.02, 1.0), (0.045, 0.01, 1.1), (0.06, -0.09, 0.8), (0.03, -0.1, 0.9))):
                tt = max(0.0, t)
                px_ = hit[0] + vx * tt
                py_ = hit[1] + vy * tt + 0.00012 * tt * tt
                front.append(pebble(fig, (px_, py_), r, ang=tt * 0.6 * (1 + i), seed=20 + i, op=1 - ease((t - 300) / 200)))
            # au pied des anneaux, des bouffées de poussière
            for i, x in enumerate((6, 30, 60, 104)):
                q = env(t, 0, 80, 200, 480)
                front.append(dust(fig, x + 2 * ease(t / 400), GR - 1.0 - 1.5 * ease(t / 400), 1.8 + 1.0 * ease(t / 300), q * 0.85, seed=40 + i))
        fig.fx_back += back
        fig.fx_front += front
    return f


# ---- la spéciale

def fx_special(tl):
    def f(fig, ctx):
        back, front = [], []
        tri = ctx['tri']
        # la lueur de venin s'enroule autour des pointes du trident ; des cailloux se soulèvent
        a = env(tl, 120, 360, 700, 800)
        if a:
            for i, tip in enumerate(tri['tips']):
                back.append(glow(fig, (tip[0], tip[1] + 2), 7 + 1.5 * math.sin(tl / 90 + i), VEN[1], 0.55 * a))
            h = tri['tips'][0]
            ang = tl * 0.9
            front.append(curl(fig, (h[0], h[1] + 9), 7.5, ang, 230, 1.5, op=a))
            front.append(curl(fig, (h[0], h[1] + 9), 6.0, ang + 180, 210, 1.2, op=a * 0.9, cw=False))
            for i, (x, sp, r) in enumerate(((4, 0.022, 1.3), (14, 0.03, 1.0), (40, 0.026, 1.2), (52, 0.018, 0.9), (90, 0.024, 1.1), (112, 0.02, 0.9))):
                tt = max(0.0, tl - 150 - 40 * i)
                y = GR - 1 - min(tt * sp, 9 + 3 * (i % 2)) + 0.6 * math.sin(tl / 120 + i)
                front.append(pebble(fig, (x, y), r, ang=tl * 0.3 + 40 * i, seed=60 + i, op=a))
        # il s'abat : la traînée dorée derrière la tête du trident
        a = env(tl, 660, 700, 760, 820)
        if a:
            h = tri['tips'][0]
            gr = lin(fig, (h[0], h[1] - 14), (h[0], h[1] + 6), [(0, GOLDS[1], 0), (1, '#ffffff', 0.7)])
            back.append('<g opacity="%g"><path d="%s" fill="%s"/></g>' % (a, ribbon([(h[0], h[1] - 14), (h[0] - 0.4, h[1] - 4), (h[0], h[1] + 4)], [0.1, 9, 0.1]).d(), gr))
        # l'impact : éclat au talon du trident et sous le bouclier, poussière ; la fissure court, les éclats jaillissent
        t = tl - SP_SLAM
        if t >= -10:
            base = (tri['base'][0], GR - 0.5)
            sb = ctx['shield']['bottom']
            if t < 420:
                front.append(glow(fig, base, 14, '#fff0b0', 0.5 * (1 - ease(t / 300))))
                front.append(pop(fig, (base[0], GR - 2), 6.0 * ease(t / 60 + 0.3) * (1 - 0.5 * ease((t - 100) / 200)), op=1 - ease((t - 140) / 160), seed=7))
                front.append(pop(fig, (sb[0], GR - 1.5), 4.6 * ease(t / 60 + 0.3), op=1 - ease((t - 120) / 160), seed=8))
                for i, (x, r) in enumerate(((base[0] - 8, 2.6), (base[0] + 9, 3.0), (sb[0] - 7, 2.4), (sb[0] + 8, 2.8), (40, 2.2), (70, 2.4))):
                    k = ease(t / 380)
                    front.append(dust(fig, x + (x - 60) * 0.06 * k, GR - 1.5 - 3 * k, r * (0.6 + 0.7 * k), op=1 - ease((t - 180) / 240), seed=70 + i))
            # la fissure de venin : elle part du trident et court vers la droite jusqu'au bout de la ligne
            x0 = base[0] + 4
            x1 = min(262.0, x0 + CRACK_SPEED * max(0.0, t) * 1.3)
            fade = 1 - ease((t - 1000) / 400)
            back.append(crack(fig, x0, x1, op=fade))
            # les éclats de roche
            for i, (x, hh, w, ln, born) in enumerate(SPIKES):
                ts = tl - born
                if ts < 0:
                    continue
                grow = ease(ts / 110) * (1 + 0.08 * math.sin(min(1.0, ts / 220) * math.pi))
                life = 520 + 40 * i
                sink = ease((ts - life) / 220)
                if sink < 1:
                    hcur = hh * grow * (1 - sink)
                    front.append(spike(fig, x, hcur, w * (0.7 + 0.3 * grow), ln, seed=90 + i))
                    if ts < 260:
                        front.append(glow(fig, (x, GR - 2), w * 0.8, VEN[1], 0.4 * (1 - ts / 260), ry=w * 0.4))
                # il s'effrite : des blocs qui retombent, la poussière roule en volutes
                tb = ts - life
                if 0 <= tb <= 600:
                    for j in range(3):
                        sx = (j - 1) * 0.022
                        bx = x + (j - 1) * w * 0.25 + sx * tb
                        by = GR - hh * (0.3 + 0.25 * j) - 0.03 * tb + 0.00018 * tb * tb
                        by = min(by, GR - 1.0)
                        front.append(pebble(fig, (bx, by), w * 0.12 * (1.2 - 0.2 * j), ang=tb * 0.4 * (j + 1), seed=110 + 7 * i + j,
                                            op=1 - ease((tb - 380) / 220)))
                    for j in range(2):
                        k = ease(tb / 600)
                        front.append(dust(fig, x + (j - 0.5) * w * 0.7 * (1 + k), GR - 1.5 - 4 * k, w * 0.16 * (1 + k), op=0.9 * (1 - ease((tb - 250) / 350)), seed=130 + 3 * i + j))
        fig.fx_back += back
        fig.fx_front += front
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael)."""
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
    glow_ = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow_).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow_.filter(ImageFilter.GaussianBlur(h * 0.12)))
    # l'ombre douce sous les anneaux (le naga ne se déplace pas)
    sh = Image.new('RGBA', (w, h))
    cx = (64 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 62 * k, fy - 3.2 * k, cx + 62 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite de la vidéo (repos ×2, attaque ×2, spéciale ×1) : (action, début, fin) en secondes."""
    seq = [('idle', 4.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
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


def shake_at(act, tl):
    """Le sol tremble à l'impact : toute la scène (sauf le fond) bouge d'un demi-pixel du dessin, deux fois."""
    t0 = AT_HIT if act == 'attack' else SP_SLAM if act == 'special' else None
    if t0 is None:
        return 0.0
    t = tl - t0
    if 0 <= t < 200:
        return 0.7 * math.sin(t / 200 * 4 * math.pi) * (1 - t / 200)
    if act == 'special' and 300 <= t < 460:
        return 0.4 * math.sin((t - 300) / 160 * 2 * math.pi)
    return 0.0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    s = shake_at(act, tl)
    v = (view[0] - s, view[1] + 0.4 * abs(s), view[2], view[3])
    return K.build(ow=ow, pose=P, fx=fx, frame=v).svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        moments = extra or [0.5, 1.5, a_s + 0.21, a_s + 0.47, a_s + 0.53, a_s + 0.6, a_s + 0.75, a_s + 0.95,
                            s_s + 0.35, s_s + 0.6, s_s + 0.72, s_s + 0.8, s_s + 0.95, s_s + 1.1, s_s + 1.3,
                            s_s + 1.6, s_s + 1.8, s_s + 2.0]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 3
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(out)
        print('planche :', os.path.abspath(out))
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
