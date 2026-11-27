# La prêtresse serpent vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# pretresse-serpent/build.py) — respiration de statue vivante, attaque de base « Éclat envoûté », attaque spéciale
# « Étreinte de la Gorgone » — dans le style lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/pretresse-serpent/anim.py            # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/pretresse-serpent/anim.py --planche [t…]   # une planche d'instants
#
# Méthode (comme Sarvik et Ophira, ../../heros/sarvik/anim.py) : le dessin (pretresse-serpent.py) est fait de morceaux ;
# chaque image le redessine dans une POSE. Le corps de serpent caché sous la robe la bombe d'un côté puis de l'autre
# (wave), le buste se balance (lean, la robe se cisaille : l'ourlet ne bouge pas), elle se dresse (rise) ; le crochet
# de la queue se balance, une bosse court le long du corps posé au sol. Les deux bras par cinématique inverse (les
# coudes tournent autour de leur vraie jointure ; les manches pendent toujours vers le bas) ; le sceptre tourne autour
# du poing. La tête tourne d'un seul bloc (tous les traits ensemble) ; les trois petits serpents de la coiffe ont chacun
# leur rythme et sortent la langue à leur tour. Effets du venin, de la pierre et de la poussière : dégradés, un seul
# contour, courbes ; aucun flou SVG, aucun rayon droit répété.
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
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('pretresse_serpent', os.path.join(HERE, 'pretresse-serpent.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'pretresse-serpent')
# les images de travail : dans le brouillon de la session si on le donne (PRETRESSE_TMP), sinon à côté du script
TMP = os.environ.get('PRETRESSE_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-14, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9), même échelle que les héros
VW, VH = 1280, 720
GR = K.GRD
FOE_X = 200.0                        # l'ennemi (comme le pixel art : 140 px devant elle)
FOE = (FOE_X, GR - 42.0)             # sa poitrine, là où frappe l'éclat

VEN = K.VEN                          # venin : coeur, vert vif, vert, vert sombre, bord
GINK = '#0c2c2a'                     # le contour du venin
ROCK = ['#f2e0b6', '#c8a070', '#8e664a', '#5e4046', '#3e2a36']   # roche : lumière, base, ombre, creux, fond des fentes
RINK = '#3a2434'                     # le contour de la roche
DUST = ['#f8ecd8', '#dcc6a6', '#ac927a', '#705a5e']
DINK = '#4a3644'                     # le contour doux de la poussière

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


SNK = ('SA', 'SB', 'SC')
NUM = ['lean', 'wave', 'rise', 'hook', 'headx', 'heady', 'tilt', 'flare', 'armx', 'army', 'stilt', 'gem', 'nhx', 'nhy',
       'curl', 'smile'] + ['%sx' % k for k in SNK] + ['%sy' % k for k in SNK] + ['tg%s' % k for k in SNK] + ['gp%s' % k for k in SNK]
BASE = dict(tgSA=1.0, tgSB=0.7, tgSC=0.0, gpSA=0.5, gpSB=0.5, gpSC=0.5)


def flat(k):
    d = {n: BASE.get(n, 0.0) for n in NUM}
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'arm':
            d['armx'], d['army'] = v
        elif key == 'nhand':
            d['nhx'], d['nhy'] = v
        elif key == 'sn':
            for s_, (x, y) in v.items():
                d[s_ + 'x'], d[s_ + 'y'] = x, y
        elif key == 'tg':
            for s_, x in v.items():
                d['tg' + s_] = x
        elif key == 'gape':
            for s_, x in v.items():
                d['gp' + s_] = x
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# Les serpents de la coiffe : en arrière (anticipation), en retard sur le geste, puis ils le dépassent ; dressés.
REAR = dict(SA=(1.2, -1.0), SB=(-1.0, -1.2), SC=(-1.2, -1.0))
LAG = dict(SA=(1.2, 1.0), SB=(-1.0, 1.0), SC=(-1.2, 0.8))
OVER = dict(SA=(-1.0, 0.0), SB=(1.0, 0.0), SC=(1.2, -0.8))
ZERO = dict(SA=(0, 0), SB=(0, 0), SC=(0, 0))
RISE = dict(SA=(1.0, -2.2), SB=(0.0, -2.4), SC=(0.4, -2.0))
STRIKE = dict(SA=(1.2, 0.0), SB=(1.2, -1.0), SC=(2.2, 0.0))
TG_IN = dict(SA=0.0, SB=0.0, SC=0.0)
HISS = dict(SA=2.0, SB=2.0, SC=2.0)
OPEN = dict(SA=1.0, SB=1.0, SC=1.0)

# 2) « Éclat envoûté » (pixel : ATTAQUE, 910 ms). Elle lève le sceptre en le ramenant vers elle ; la pierre verte
# s'allume, une volute de venin s'enroule autour et trois gravillons y montent se souder en un éclat de pierre
# (anticipation tenue : les serpents de la coiffe se dressent, langues rentrées, ses yeux s'allument). Puis elle pique
# le sceptre vers l'ennemi : l'éclat part dans un halo vert, en arc, avec une traînée de venin qui serpente ; il frappe
# (éclat vert, gravillons, poussière). Les serpents de la coiffe traînent derrière le geste puis le dépassent ; elle
# revient en garde.
ATTACK = [
    (0, {}),
    (90, dict(lean=-1, wave=-0.6, arm=(-0.8, -2.8), stilt=-3, gem=0.4, sn={k: (v[0], 0) for k, v in REAR.items()}, hook=0.6, curl=0.2)),
    (200, dict(lean=-2, wave=-1.2, arm=(-1.0, -6.0), stilt=-5, head=(0, 0.8), sn=REAR, tg=TG_IN, gem=0.8, hook=1.0, curl=0.4, flare=0.5)),
    (420, dict(lean=-2.3, wave=-1.4, arm=(-1.1, -6.4), stilt=-6, head=(0, 0.6), sn=REAR, tg=TG_IN, gem=1.0, hook=1.2, flare=1.0, curl=0.5, smile=0.4)),
    # elle pique le sceptre vers l'ennemi : l'éclat part en arc
    (470, dict(lean=2.2, wave=1.4, arm=(3.6, 1.0), stilt=15, head=(-0.8, 0), sn=LAG, tg=HISS, gape=OPEN, flare=1, gem=1, hook=-0.6, curl=-0.3, smile=0.4)),
    (530, dict(lean=2.5, wave=1.3, arm=(4.0, 1.2), stilt=17, head=(0.2, 0), sn=LAG, tg=HISS, gape=OPEN, flare=1, gem=0.9, hook=-1.0, curl=-0.4, smile=0.4)),
    # il frappe
    (600, dict(lean=2.2, wave=1.0, arm=(3.0, 1.0), stilt=13, sn=ZERO, tg=HISS, flare=0.8, gem=0.6, hook=-0.6, smile=0.5)),
    # retour en garde
    (690, dict(lean=1, wave=0.6, arm=(1.2, 0.2), stilt=6, sn=OVER, flare=0.3, gem=0.4, hook=0.4, smile=0.3)),
    (800, dict(lean=0.8, wave=0.0, arm=(0.3, 0), stilt=2, head=(0, -0.6), sn=OVER, gem=0.2, hook=0.6)),
    (1000, {}),
]
AT_CHARGE = (60, 470)        # la pierre s'allume, la volute s'enroule, l'éclat se forme
AT_SHOT = (470, 600)         # l'éclat vole
AT_HIT = 600                 # il frappe

# 3) « Étreinte de la Gorgone » (pixel : SPECIALE, 1650 ms). Elle se dresse (le corps de serpent se déroule sous la
# robe), lève le sceptre ; la poussière s'arrache sous ses anneaux, la pierre brûle, des volutes de venin montent et un
# serpent de lueur verte s'enroule autour de la pierre (anticipation tenue, ses yeux s'allument, les serpents de la
# coiffe sifflent). Elle pique le sceptre : le serpent de lueur file en ondulant jusqu'à l'ennemi et s'enroule autour de
# lui en spirale, des éclats de roche jaillissent du sol, la pierre monte dans ses anneaux et l'enferme : un cocon de
# pierre que le serpent enlace, devenu pierre lui aussi (arrêt sur l'image). Des veines vertes courent dans la pierre,
# puis le cocon s'effondre en blocs qui roulent et en poussière qui se défait en volutes. Elle se repose.
SPECIAL = [
    (0, {}),
    (110, dict(rise=1.6, lean=-1, wave=-0.6, arm=(0, -3.0), stilt=-2, head=(0, 0.8), sn={k: (v[0], v[1] / 2) for k, v in RISE.items()}, tg=HISS, gem=0.4, hook=0.6)),
    (230, dict(rise=3.6, lean=-1, wave=-1.0, arm=(-0.6, -7.2), stilt=-4, head=(0, 0.6), sn=RISE, tg=HISS, gape=OPEN, gem=0.8, flare=0.6, hook=1.2, curl=0.4)),
    (470, dict(rise=4.6, lean=-1.3, wave=-1.3, arm=(-0.8, -8.4), stilt=-5, sn=RISE, tg=HISS, gape=OPEN, gem=1, flare=1, hook=1.4, curl=0.6, smile=0.5)),
    # elle pique le sceptre : le serpent de lueur file vers l'ennemi
    (530, dict(rise=3.6, lean=2.2, wave=1.2, arm=(3.6, 0), stilt=16, head=(1, 0), sn=STRIKE, tg=HISS, gape=OPEN, flare=1, gem=1, hook=-0.8, curl=-0.4, smile=0.6)),
    # il s'enroule, la pierre monte ; arrêt sur l'image quand le cocon est fermé
    (650, dict(rise=3.4, lean=2.0, wave=1.0, arm=(3.0, 0), stilt=13, head=(0.6, 0), sn=STRIKE, tg=HISS, flare=1, gem=0.8, hook=-0.6, curl=0.6, smile=0.7)),
    (900, dict(rise=3.2, lean=2.0, wave=1.0, arm=(2.8, 0), stilt=12, head=(0.6, 0), sn=STRIKE, tg=HISS, flare=1, gem=0.7, hook=-0.4, curl=0.8, smile=0.8)),
    (1140, dict(rise=3.0, lean=1.6, wave=0.8, arm=(2.2, 0), stilt=10, head=(0.4, -0.2), sn={k: (v[0], v[1] / 2) for k, v in RISE.items()}, tg=HISS, flare=0.6, gem=0.5, curl=1.0, smile=0.8)),
    # le cocon s'effondre ; elle se repose
    (1260, dict(rise=2.0, lean=1, wave=0.4, arm=(1.2, 0), stilt=5, head=(0, -0.6), sn=OVER, gem=0.3, smile=0.5)),
    (1400, dict(rise=0.6, lean=0, wave=-0.4, arm=(0.3, 0), stilt=1, head=(0, 0.6), sn=OVER, hook=-0.6, smile=0.3)),
    (1560, dict(wave=-0.3, hook=0.4)),
    (1800, {}),
]
SP_DUST = (60, 520)          # la poussière s'arrache sous les anneaux
SP_GATHER = (180, 540)       # le serpent de lueur s'enroule autour de la pierre
SP_FLY = (520, 660)          # il file vers l'ennemi
SP_COIL = (640, 780)         # il s'enroule autour de l'ennemi
SP_STONE = (700, 900)        # la pierre monte et l'enferme
SP_VEINS = (980, 1140)       # des veines vertes courent dans la pierre
SP_FALL = (1140, 1500)       # le cocon s'effondre
SP_END = 1760

# ======================================================================== la respiration (en boucle, 1,4 s : lente)
# Immobile comme une statue mais vivante : le souffle soulève le buste, la tête suit avec retard ; le corps caché bombe
# la robe d'un côté puis de l'autre (wave) et le buste se balance avec retard ; le crochet de la queue se balance plus
# tard encore ; une bosse court le long du corps posé au sol. Les trois serpents de la coiffe ont chacun leur rythme
# (celui de droite deux fois plus vite) et sortent la langue à leur tour. La pierre du sceptre palpite. Un clignement.
LOOP = 1.4


def pulse(x, c, w):
    """Une bosse douce (0..1) autour de c (largeur w), sur une boucle 0..1."""
    d = min(abs(x - c), 1 - abs(x - c))
    return max(0.0, 1 - (d / w) ** 2) ** 2


def idle_offsets(T):
    u = 2 * math.pi * T / LOOP
    x = (T % LOOP) / LOOP
    d = dict(breath=0.5 - 0.5 * math.cos(u), wave=1.2 * math.sin(u), lean=0.7 * math.sin(u - 1.3),
             heady=-0.45 * (0.5 - 0.5 * math.cos(u - 0.8)), headx=0.15 * math.sin(u - 1.0), tilt=0.8 * math.sin(u - 1.1),
             hook=1.6 * math.sin(u - 2.0), stilt=0.9 * math.sin(u - 1.2), army=-0.3 * (0.5 - 0.5 * math.cos(u - 0.4)),
             curl=0.25 * math.sin(u - 1.6), nhy=-0.25 * (0.5 - 0.5 * math.cos(u - 0.5)), gem=0.15 + 0.15 * math.sin(u + 0.5))
    for k_, (ax, ay, turns, ph) in dict(SA=(1.0, 0.9, 1, 0.0), SB=(0.6, 1.0, 1, 2.1), SC=(0.8, 0.8, 2, 0.6)).items():
        d[k_ + 'x'] = ax * math.cos(turns * u + ph)
        d[k_ + 'y'] = ay * math.sin(turns * u + ph)
    d['tgSA'] = 0.3 + 1.6 * pulse(x, 0.15, 0.13)
    d['tgSB'] = 0.2 + 1.7 * pulse(x, 0.45, 0.12)
    d['tgSC'] = 1.8 * pulse(x, 0.78, 0.12)
    return d


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
        if n.startswith('tg'):
            Q[n] = (1 - w) * src[n] + w * idl[n]
        else:
            Q[n] = src[n] + w * idl.get(n, 0.0)
    P = dict(lean=Q['lean'], wave=Q['wave'], rise=Q['rise'], hook=Q['hook'], tilt=Q['tilt'], flare=max(0.0, Q['flare']),
             stilt=Q['stilt'], gem=max(0.0, min(1.0, Q['gem'])), curl=Q['curl'], smile=Q['smile'])
    P['breath'] = w * idl['breath']
    P['head'] = (Q['headx'], Q['heady'])
    P['arm'] = (Q['armx'], Q['army'])
    P['nhand'] = (Q['nhx'], Q['nhy'])
    P['sn'] = {k_: (Q[k_ + 'x'], Q[k_ + 'y']) for k_ in SNK}
    P['tg'] = {k_: max(0.0, Q['tg' + k_]) for k_ in SNK}
    P['gape'] = {k_: max(0.0, Q['gp' + k_]) for k_ in SNK}
    P['hump'] = ((T % LOOP) / LOOP * 1.3 - 0.15, 0.6 * w)
    P['blink'] = 1.0 if (w > 0.95 and 2.3 <= (T % 3.9) < 2.4) else 0.0
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


def prog(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))


def lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def radial(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def glow(fig, c, r, color, op):
    if op <= 0.01 or r <= 0.1:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), radial(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)]))


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def normal_at(pts, i):
    a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    return (-dy / L, dx / L)


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
        rr = r * (1 - 0.55 * u)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        ws.append(max(0.1, w * (1 - u) ** 0.8))
    sh = ribbon(pts, ws)
    gr = lin(fig, pts[0], pts[-1], [(0, VEN[2]), (0.5, VEN[1]), (1, VEN[0])])
    return outlined([(sh, gr, 1)], w=0.8, op=op)


def dust(fig, cx, cy, r, op=1.0, seed=0, hollow=0.0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    balls = [(cx, cy, r)]
    for i in range(3):
        a = rnd.uniform(0, 2 * math.pi)
        balls.append((cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.45 + 0.2 * r, r * rnd.uniform(0.55, 0.75)))
    if hollow > 0:
        balls = [(x + (x - cx) * hollow * 0.6, y + (y - cy) * hollow * 0.4, rr * (1 - 0.45 * hollow)) for x, y, rr in balls[1:]]
    gr = lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.7"/>' % (fm(balls[0][0] + r * 0.3), fm(balls[0][1] - r * 0.35), fm(r * 0.36), DUST[0])
    return '<g opacity="%g">%s%s%s</g>' % (max(0.0, min(1.0, op)), sil, col, hi)


def rock_shape(c, r, seed=0, ang=0.0, squash=1.0):
    """Un caillou (ou un bloc) à facettes : un polygone irrégulier aux coins à peine arrondis."""
    rnd = random.Random(seed)
    n = 6 + seed % 2
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25) + math.radians(ang)
        rr = r * rnd.uniform(0.78, 1.08)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a) * squash))
    return sm(pts, sharp=tuple(range(n)), t=0.35), pts


def rock(fig, c, r, op=1.0, seed=0, ang=0.0, squash=1.0, glow_=0.0):
    """Un caillou de pierre : la face éclairée en haut à droite, l'ombre en bas à gauche, un contour."""
    if r < 0.2 or op <= 0.02:
        return ''
    sh, pts = rock_shape(c, r, seed, ang, squash)
    gr = lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, ROCK[0]), (0.45, ROCK[1]), (1, ROCK[2])])
    facet = sm([c] + [p for p in pts if (p[0] - c[0]) + (c[1] - p[1]) > 0.2 * r][:3], t=0.3)
    parts = [(sh, gr, 1), (facet, ROCK[0], 0.45),
             (sm([(c[0] - r * 0.9, c[1] + r * 0.1), (c[0] - r * 0.2, c[1] + r * 0.75), (c[0] - r * 0.5, c[1] + r * 0.2)], t=0.5), ROCK[3], 0.45)]
    if glow_ > 0:
        parts.append((sh, VEN[1], 0.35 * glow_))
    return outlined(parts, ink=RINK, w=0.8, op=op)


def pop(fig, c, r, op=1.0, seed=0):
    """L'éclat vert de l'impact : une étoile molle à lobes inégaux (jamais des rayons réguliers), un coeur blanc."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    n = 7
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n + rnd.uniform(-0.12, 0.12)
        rr = r * (rnd.uniform(0.95, 1.25) if i % 2 == 0 else rnd.uniform(0.45, 0.6))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = sm(pts, t=0.8)
    gr = radial(fig, c, r * 1.2, [(0, VEN[0]), (0.45, VEN[1]), (1, VEN[2])])
    return outlined([(sh, gr, 1), (ellipse(c[0] + r * 0.05, c[1] - r * 0.05, r * 0.42, r * 0.4), '#ffffff', 0.9)], w=1.0, op=op)


def trail(fig, pts, w0, w1, amp, phase, op=1.0):
    """Une traînée de venin qui SERPENTE le long de pts (mince au début, épaisse au bout) : une onde, un contour."""
    if len(pts) < 3 or op <= 0.02:
        return ''
    n = len(pts)
    out, ws = [], []
    for i in range(n):
        s = i / (n - 1)
        nx, ny = normal_at(pts, i)
        off = amp * math.sin(s * 9.0 + phase) * min(1.0, (1 - s) * 3) * min(1.0, s * 4)
        out.append((pts[i][0] + nx * off, pts[i][1] + ny * off))
        ws.append(max(0.08, w0 + (w1 - w0) * s ** 1.3))
    sh = ribbon(out, ws)
    gr = lin(fig, out[0], out[-1], [(0, VEN[3]), (0.6, VEN[2]), (1, VEN[1])])
    return outlined([(sh, gr, 1)], w=0.8, op=op)


def serpent(fig, pts, w_head=4.4, op=1.0, stone=0.0, head=True):
    """Le serpent de lueur verte (ou de pierre : stone = 1) : un corps effilé le long de pts (la tête au dernier
    point), une tête en goutte, un oeil blanc ; un contour."""
    if len(pts) < 3 or op <= 0.02:
        return ''
    n = len(pts)
    ws = [max(0.2, w_head * (0.25 + 0.75 * (i / (n - 1)) ** 0.7)) for i in range(n)]
    body = ribbon(pts, ws[:-1] + [ws[-1] * 0.6])
    a = pts[-1]
    b = pts[-3]
    ang = math.degrees(math.atan2(a[1] - b[1], a[0] - b[0]))
    L = w_head * 1.6

    def H(x, y):
        r_ = math.radians(ang)
        return (a[0] + x * math.cos(r_) - y * math.sin(r_), a[1] + x * math.sin(r_) + y * math.cos(r_))
    hd = sm([H(-0.6, -w_head * 0.42), H(L * 0.5, -w_head * 0.6), H(L, -w_head * 0.25), H(L * 1.08, 0.05),
             H(L, w_head * 0.3), H(L * 0.45, w_head * 0.58), H(-0.6, w_head * 0.42)], t=0.9)
    eye = ellipse(*H(L * 0.55, -w_head * 0.22), w_head * 0.16, w_head * 0.13)
    if stone >= 0.5:
        gr = lin(fig, (max(p[0] for p in pts), min(p[1] for p in pts)), (min(p[0] for p in pts), max(p[1] for p in pts)),
                 [(0, ROCK[0]), (0.5, ROCK[1]), (1, ROCK[2])])
        parts = [(body, gr, 1), (hd, gr, 1), (eye, ROCK[3], 0.9)]
        return outlined(parts, ink=RINK, w=0.9, op=op)
    gr = lin(fig, pts[0], pts[-1], [(0, VEN[3]), (0.5, VEN[2]), (1, VEN[1])])
    core = ribbon(pts[n // 4:], [max(0.1, w * 0.35) for w in ws[n // 4:-1]] + [0.1])
    parts = [(body, gr, 1), (core, VEN[0], 0.55), (hd, VEN[1], 1), (eye, '#ffffff', 0.95)]
    if stone > 0:
        parts += [(body, ROCK[1], stone * 1.6), (hd, ROCK[1], stone * 1.6)]
    return outlined(parts, w=0.9, op=op)


# ---- l'attaque : « Éclat envoûté »

SHARD_SEED = 47


def shard_at(ctx, tl):
    """Où est l'éclat (et s'il existe) : formé au-dessus de la pierre, puis en vol jusqu'à l'ennemi."""
    g = ctx['gem']
    if tl < 330:
        return None
    if tl < AT_SHOT[0]:
        return (g[0] + 0.8, g[1] - 7.0)
    return None


_PATH = {}


def shot_path():
    """La trajectoire de l'éclat : de la pierre (au moment où le sceptre pique) jusqu'à l'ennemi, en arc."""
    if 'a' not in _PATH:
        P, _ = pose_at(0.0, 'attack', -AT_SHOT[0] / 1000)
        fig = K.build(pose=P)
        g = fig.ctx['gem']
        p0 = (g[0] + 2.0, g[1] - 5.0)
        _PATH['a'] = bezier(p0, (p0[0] + 40, p0[1] - 12), (FOE[0] - 46, FOE[1] - 16), FOE, 90)
    return _PATH['a']


def fx_attack(tl):
    def f(fig, ctx):
        back, front = [], []
        g = ctx['gem']
        # 1) la pierre s'allume : un halo vert qui grandit ; une volute de venin s'enroule autour ; trois gravillons
        # montent du sol et se soudent en un éclat au-dessus de la pierre
        e = env(tl, AT_CHARGE[0], 200, 470, 560)
        back.append(glow(fig, g, 6 + 6 * e, VEN[1], 0.55 * e))
        if AT_CHARGE[0] < tl < 520:
            k = prog(tl, 120, 430)
            back.append(curl(fig, (g[0] + 0.5, g[1] + 0.5), 9.0 - 2 * k, 200 + 260 * k, 300, 2.2, op=env(tl, 100, 180, 430, 520)))
            for i, (dx, dy) in enumerate(((-12, 16), (10, 18), (13, -2))):
                q = ease(prog(tl, 150 + 40 * i, 360 + 20 * i))
                if q < 1:
                    p = (g[0] + 0.8 + dx * (1 - q), g[1] - 7 + (dy + 7) * (1 - q))
                    front.append(rock(fig, p, 1.1 + 0.2 * i, seed=21 + i, glow_=q))
        sp = shard_at(ctx, tl)
        if sp:
            k = ease(prog(tl, 330, 420))
            back.append(glow(fig, sp, 6.5 * k, VEN[1], 0.7))
            front.append(rock(fig, sp, 2.2 + 1.2 * k, seed=SHARD_SEED, ang=10 * k, glow_=0.6))
        # 2) le coup de sceptre : un croissant de venin derrière la pierre ; l'éclat file en arc, sa traînée serpente
        if AT_SHOT[0] <= tl < AT_SHOT[1] + 120:
            path = shot_path()
            n = len(path) - 1
            q = prog(tl, AT_SHOT[0], AT_SHOT[1])
            q = q ** 0.85
            i1 = int(round(q * n))
            i0 = max(0, i1 - 50, int(round(prog(tl, 540, 700) * n)))
            if i1 - i0 >= 4:
                back.append(trail(fig, path[i0:i1 - 1], 0.6, 3.2, 1.8, q * 7, op=1.0 - prog(tl, 620, 720)))
            if tl < AT_HIT:
                c = path[i1]
                back.append(glow(fig, c, 7.5, VEN[1], 0.75))
                front.append(rock(fig, c, 3.4, seed=SHARD_SEED, ang=10 + 400 * q, glow_=0.6))
        e2 = env(tl, AT_SHOT[0], 480, 520, 600)
        if e2 > 0:
            ang0 = math.radians(-40)
            pts = [(g[0] - 4 + 11 * math.cos(ang0 + 1.6 * s), g[1] + 6 + 9 * math.sin(ang0 + 1.6 * s)) for s in [i / 16 for i in range(17)]]
            back.append(outlined([(ribbon(pts, [max(0.1, 3.4 * math.sin(math.pi * i / 16)) for i in range(17)]), VEN[1], 1)], w=0.8, op=e2))
        # 3) l'impact : un éclat vert et blanc, des gravillons qui volent, la poussière qui enfle puis se défait
        if tl >= AT_HIT:
            k = prog(tl, AT_HIT, AT_HIT + 120)
            front.append(pop(fig, FOE, 5.5 + 3.5 * k, op=1 - prog(tl, AT_HIT + 60, AT_HIT + 200), seed=5))
            d = prog(tl, AT_HIT, 1000)
            back.append(dust(fig, FOE[0] + 2, FOE[1] + 4, 3 + 3.5 * d, op=1 - d ** 1.6, seed=36, hollow=d))
            for i, (dx, dy) in enumerate(((-1.0, -0.7), (-0.8, 0.9), (0.7, -1.0), (0.9, 0.6))):
                q = prog(tl, AT_HIT, AT_HIT + 300)
                p = (FOE[0] + dx * (4 + 16 * q), FOE[1] + dy * (4 + 14 * q) + 18 * q * q)
                front.append(rock(fig, p, 1.0, op=1 - prog(tl, AT_HIT + 200, AT_HIT + 320), seed=31 + i, ang=300 * q))
            front.append(curl(fig, (FOE[0] - 4, FOE[1] - 5), 4.0, 90, 260, 1.6, op=env(tl, AT_HIT + 60, AT_HIT + 120, AT_HIT + 200, AT_HIT + 320)))
        fig.fx_back.extend([b for b in back if b])
        fig.fx_front.extend([x for x in front if x])
    return f


# ---- l'attaque spéciale : « Étreinte de la Gorgone »

COC_H = 54.0                 # la hauteur du cocon de pierre
COC_W = 11.5                 # sa demi-largeur la plus grande


def coc_w(h):
    """La demi-largeur du cocon à la hauteur h au-dessus du sol (un grand œuf de pierre, plus large en bas)."""
    if h < 0 or h > COC_H:
        return 0.0
    q = (h - 20) / (34 if h > 20 else 26)
    return COC_W * max(0.0, 1 - q * q) ** 0.55


def cocoon_shape(dx=0.0):
    pts = []
    for i in range(0, 25):
        h = COC_H * i / 24
        pts.append((FOE_X + dx + coc_w(h) + (0.8 if i == 0 else 0), GR - h))
    for i in range(24, -1, -1):
        h = COC_H * i / 24
        pts.append((FOE_X + dx - coc_w(h) - (0.8 if i == 0 else 0), GR - h))
    return sm(pts, sharp=(0, 49), t=0.9)


def helix(h0, h1, turns, a0, rx=13.0, ry=4.2, n=90, upto=1.0):
    """La spirale autour de l'ennemi : (points, devant ?) ; upto = la part déjà tracée (depuis le bas)."""
    out = []
    m = max(2, int(n * upto))
    for i in range(m + 1):
        s = i / n
        a = math.radians(a0 + 360 * turns * s)
        h = h0 + (h1 - h0) * s
        r = rx * (0.75 + 0.25 * coc_w(h) / COC_W) if h < COC_H else rx * 0.6
        out.append(((FOE_X + r * math.cos(a), GR - h + ry * math.sin(a)), math.sin(a) > 0))
    return out


def split_runs(hp):
    """Les morceaux de la spirale qui passent devant / derrière."""
    runs = []
    cur = [hp[0][0]]
    side = hp[0][1]
    for p, s in hp[1:]:
        cur.append(p)
        if s != side:
            runs.append((side, cur))
            cur = [p]
            side = s
    runs.append((side, cur))
    return runs


def coil(fig, upto, stone, op=1.0, w=3.0):
    """Le serpent enroulé autour de l'ennemi (de lueur, puis de pierre) : rend (derrière, devant)."""
    hp = helix(4.0, 46.0, 2.25, 200.0, upto=upto)
    back, front = [], []
    pts_all = [p for p, _ in hp]
    n = len(pts_all)
    ws = [max(0.4, w * (0.35 + 0.65 * (i / max(1, n - 1)) ** 0.6)) for i in range(n)]
    i = 0
    for side, run in split_runs(hp):
        k = len(run)
        seg_w = ws[i:i + k]
        i += k - 1
        if k < 2:
            continue
        sh = ribbon(run, [max(0.2, x) for x in seg_w[:k]]) if k >= 3 else None
        if sh is None:
            continue
        if stone >= 0.5:
            gr = lin(fig, (FOE_X + 12, GR - 50), (FOE_X - 12, GR), [(0, ROCK[0]), (0.5, ROCK[1]), (1, ROCK[2])])
            el = outlined([(sh, gr if side else ROCK[3], 1)], ink=RINK, w=0.9, op=op)
        else:
            col = VEN[1] if side else VEN[3]
            parts = [(sh, col, 1)]
            if side:
                parts.append((ribbon(run, [max(0.1, x * 0.35) for x in seg_w[:k]]), VEN[0], 0.6))
            if stone > 0:
                parts.append((sh, ROCK[1], stone * 1.6))
            el = outlined(parts, w=0.9, op=op)
        (front if side else back).append(el)
    # la tête, au bout (en haut), tournée vers la prêtresse
    if upto > 0.85:
        p = pts_all[-1]
        q = (p[0] - 4, p[1] - 2.5)
        front.append(serpent(fig, [pts_all[-4], pts_all[-2], q], w_head=w * 1.3, stone=stone, op=op))
    return back, front


def cocoon(fig, level, veins=0.0, cracks=0.0, op=1.0):
    """Le cocon de pierre qui monte du sol (level 0..1 de sa hauteur), ses grandes plaques, ses veines vertes."""
    if level <= 0.01 or op <= 0.02:
        return ''
    sh = cocoon_shape()
    top = GR - COC_H * level - 0.5
    cid = fig.uid('cc')
    fig.defs.append('<clipPath id="%s"><rect x="%s" y="%s" width="60" height="%s"/></clipPath>' % (
        cid, fm(FOE_X - 30), fm(top - 1.2), fm(GR - top + 3)))
    gr = lin(fig, (FOE_X + 12, GR - 50), (FOE_X - 12, GR), [(0, ROCK[0]), (0.45, ROCK[1]), (1, ROCK[2])])
    parts = [(sh, gr, 1)]
    # les plaques : quelques grandes facettes (claires côté lumière, sombres côté ombre), jamais des rayures
    rnd = random.Random(9)
    for j in range(7):
        h = 6 + j * 7.0 + rnd.uniform(-1.5, 1.5)
        w_ = coc_w(h)
        if w_ <= 1:
            continue
        x0 = FOE_X + rnd.uniform(-0.5, 0.5) * w_
        a = (x0 - 3.6, GR - h + 3.0)
        b = (x0 + 2.8, GR - h + 3.8)
        c = (x0 + 4.0, GR - h - 2.4)
        d = (x0 - 2.4, GR - h - 3.4)
        side_light = x0 > FOE_X
        parts.append((sm([a, b, c, d], sharp=(0, 1, 2, 3), t=0.3), ROCK[0] if side_light else ROCK[2], 0.45))
    parts.append((sm([(FOE_X - 9, GR - 4), (FOE_X - 11, GR - 20), (FOE_X - 8, GR - 38), (FOE_X - 5, GR - 50),
                      (FOE_X - 7.5, GR - 36), (FOE_X - 8.5, GR - 20), (FOE_X - 6.5, GR - 4)], t=0.9), ROCK[3], 0.45))
    parts.append((sm([(FOE_X + 6, GR - 46), (FOE_X + 9.5, GR - 30), (FOE_X + 10, GR - 16), (FOE_X + 7.6, GR - 24), (FOE_X + 6.6, GR - 38)], t=0.9), ROCK[0], 0.5))
    # les veines vertes : des fentes qui courent dans la pierre (elles se ramifient), lumineuses
    if veins > 0:
        lines = [[(FOE_X - 2, GR - 2), (FOE_X - 4, GR - 12), (FOE_X - 1, GR - 22), (FOE_X - 3.5, GR - 32), (FOE_X + 0.5, GR - 44)],
                 [(FOE_X - 1, GR - 22), (FOE_X + 4, GR - 27), (FOE_X + 6.5, GR - 36)],
                 [(FOE_X - 4, GR - 12), (FOE_X - 8.5, GR - 16)],
                 [(FOE_X - 3.5, GR - 32), (FOE_X - 7, GR - 40)]]
        for li, L in enumerate(lines):
            k = max(0.0, min(1.0, veins * 1.6 - li * 0.25))
            if k <= 0:
                continue
            m = max(2, int(round(1 + (len(L) - 1) * k)))
            seg = L[:m]
            if len(seg) < 2:
                continue
            ws = [0.15] + [1.3 - 0.2 * li] * (len(seg) - 2) + [0.15]
            if len(seg) == 2:
                seg = [seg[0], ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2), seg[1]]
                ws = [0.15, 1.1, 0.15]
            parts.append((ribbon(seg, [w_ + 0.9 for w_ in ws]), VEN[2], 0.9))
            parts.append((ribbon(seg, ws), VEN[0], 0.95))
    el = outlined(parts, ink=RINK, w=1.0, op=op)
    return '<g clip-path="url(#%s)">%s</g>' % (cid, el)


def fly_path():
    """La route du serpent de lueur : de la pierre (au moment où elle pique) jusqu'au bas de l'ennemi, en ondulant."""
    if 'f' not in _PATH:
        P, _ = pose_at(0.0, 'special', -SP_FLY[0] / 1000)
        fig = K.build(pose=P)
        g = fig.ctx['gem']
        p0 = (g[0] + 2, g[1] - 2)
        end = (FOE_X - 10, GR - 8)
        base = bezier(p0, (p0[0] + 40, p0[1] - 18), (end[0] - 50, end[1] - 40), end, 120)
        out = []
        for i, p in enumerate(base):
            s = i / 120
            nx, ny = normal_at(base, i)
            off = 5.0 * math.sin(s * 14) * min(1.0, s * 5) * min(1.0, (1 - s) * 4)
            out.append((p[0] + nx * off, p[1] + ny * off))
        _PATH['f'] = out
    return _PATH['f']


BLOCKS = [((-6, 8), 4.2, (-1.0, 0.0)), ((5, 10), 4.6, (1.0, 0.0)), ((-3, 22), 4.0, (-0.8, -0.2)), ((6, 24), 3.8, (0.9, -0.3)),
          ((-6, 34), 3.6, (-1.2, -0.4)), ((3, 38), 3.4, (0.8, -0.6)), ((0, 48), 3.0, (0.2, -0.8)), ((-1, 14), 4.4, (-0.2, 0.0))]


def fx_special(tl):
    def f(fig, ctx):
        back, front = [], []
        g = ctx['gem']
        # 1) elle se dresse : la poussière s'arrache sous ses anneaux
        for i, (x, sd) in enumerate(((28.0, 1), (46.0, 2), (66.0, 3), (76.0, 4))):
            q = prog(tl, SP_DUST[0] + 50 * i, SP_DUST[0] + 380 + 50 * i)
            if 0 < q < 1:
                back.append(dust(fig, x + 5 * q * (1 if i > 1 else -1), GR - 2.5 - 3.5 * q, 3.0 + 3.4 * q, op=1 - q ** 1.5, seed=60 + sd, hollow=q))
        # 2) la pierre brûle, des volutes montent, le serpent de lueur s'enroule autour de la pierre
        e = env(tl, 80, 250, 520, 620)
        back.append(glow(fig, g, 7 + 8 * e, VEN[1], 0.6 * e))
        if SP_GATHER[0] < tl < SP_GATHER[1]:
            k = prog(tl, SP_GATHER[0], SP_GATHER[1])
            for j, (dx, a0) in enumerate(((-7, 120), (6, 300))):
                q = prog(tl, SP_GATHER[0] + 60 * j, SP_GATHER[1] - 40 + 60 * j)
                if 0 < q < 1:
                    back.append(curl(fig, (g[0] + dx, g[1] + 12 - 16 * q), 3.0 + 2 * q, a0 + 200 * q, 260, 1.6, op=math.sin(math.pi * q)))
            pts = []
            turns = 1.3
            for i in range(40):
                s = i / 39
                a = math.radians(-90 + 360 * turns * s + 220 * k)
                r = 6.5 - 1.5 * s
                pts.append((g[0] + r * math.cos(a), g[1] + r * 0.75 * math.sin(a) + 2 - 4 * s))
            front.append(serpent(fig, pts[:max(4, int(40 * min(1.0, k * 1.6)))], w_head=3.0, op=min(1.0, k * 4)))
        # 3) il file vers l'ennemi en ondulant
        if SP_FLY[0] <= tl < SP_COIL[0] + 60:
            path = fly_path()
            n = len(path) - 1
            q = ease(prog(tl, SP_FLY[0], SP_FLY[1]))
            i1 = max(5, int(round(q * n)))
            i0 = max(0, i1 - 45)
            front.append(serpent(fig, path[i0:i1 + 1], w_head=4.0, op=1 - prog(tl, SP_COIL[0], SP_COIL[0] + 60)))
        # 4) il s'enroule autour de l'ennemi en spirale ; des éclats de roche jaillissent du sol ; la pierre monte dans
        # ses anneaux et l'enferme ; le serpent devient pierre lui aussi
        if SP_COIL[0] <= tl < SP_FALL[0] + 40:
            up = ease(prog(tl, SP_COIL[0], SP_COIL[1]))
            st = prog(tl, SP_STONE[0] + 60, SP_STONE[1])
            cb, cfr = coil(fig, up, st)
            back.extend(cb)
            lvl = ease(prog(tl, SP_STONE[0], SP_STONE[1]))
            vn = prog(tl, SP_VEINS[0], SP_VEINS[1])
            front.append(cocoon(fig, lvl, veins=vn))
            front.extend(cfr)
            for i, (dx, hh, lean) in enumerate(((-17, 12, -0.5), (16, 10, 0.5), (-12, 7, -0.3))):
                q = ease(prog(tl, SP_COIL[0] + 40 * i, SP_COIL[0] + 140 + 40 * i))
                if q > 0:
                    x = FOE_X + dx
                    h = hh * q
                    sp = sm([(x - 2.4, GR + 0.5), (x + lean * h - 0.3, GR - h), (x + lean * h + 0.4, GR - h + 0.6), (x + 2.6, GR + 0.5)], sharp=(0, 1, 2, 3), t=0.4)
                    gr = lin(fig, (x + 3, GR - h), (x - 3, GR), [(0, ROCK[0]), (0.5, ROCK[1]), (1, ROCK[2])])
                    front.append(outlined([(sp, gr, 1)], ink=RINK, w=0.8, op=1 - prog(tl, SP_FALL[0] - 100, SP_FALL[0] + 40)))
            # l'arrêt sur l'image : un liseré vert autour du cocon quand il se ferme
            ring_ = env(tl, SP_STONE[1] - 40, SP_STONE[1], SP_STONE[1] + 40, SP_STONE[1] + 200)
            if ring_ > 0:
                back.append(glow(fig, (FOE_X, GR - 26), 30, VEN[1], 0.5 * ring_))
        # 5) le cocon s'effondre en blocs qui roulent, et en poussière qui se défait en volutes
        if tl >= SP_FALL[0]:
            q = prog(tl, SP_FALL[0], SP_FALL[1])
            for i, ((dx, h), r, (vx, vy)) in enumerate(BLOCKS):
                t_ = q * 1.25
                x = FOE_X + dx + vx * 18 * t_
                y = GR - h + (vy * 10 * t_) + 60 * t_ * t_
                y = min(y, GR - r * 0.8)
                front.append(rock(fig, (x, y), r * (1 - 0.15 * q), seed=70 + i, ang=vx * 220 * t_,
                                  op=1 - prog(tl, SP_FALL[1] - 100, SP_FALL[1] + 120)))
            for i, (dx, dy, r) in enumerate(((-8, -4, 5.0), (7, -6, 5.6), (0, -16, 4.6), (-12, -2, 3.6), (13, -2, 3.8))):
                d = prog(tl, SP_FALL[0] + 30 * i, SP_END)
                back.append(dust(fig, FOE_X + dx * (1 + 0.6 * d), GR + dy - 4 * d, r * (0.7 + 0.8 * d), op=1 - d ** 1.4, seed=80 + i, hollow=d))
            front.append(curl(fig, (FOE_X - 6, GR - 20), 5.0, 120, 280, 1.6, op=env(tl, SP_FALL[0] + 40, SP_FALL[0] + 120, SP_FALL[0] + 220, SP_FALL[0] + 360)))
        fig.fx_back.extend([b for b in back if b])
        fig.fx_front.extend([x for x in front if x])
    return f


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
    glow_ = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow_).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow_.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def ground_shadow(w, h, view, floor_y=GR):
    """L'ombre douce sous le corps de serpent."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = int((floor_y - y0) * k)
    sh = Image.new('RGBA', (w, h))
    cx = (48 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 32 * k, fy - 2.6 * k, cx + 32 * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k)), k


def timeline():
    """La suite de la vidéo (repos ×2, attaque ×2, spéciale ×1) : (action, début, fin) en secondes."""
    seq = [('idle', 2.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
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


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(K.HEROS, 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def compose(png, P, bg, shadow, k):
    im = bg.copy()
    im.alpha_composite(shadow)
    im.alpha_composite(Image.open(png))
    return im


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
        moments = extra or [0.35, 1.05, a_s + 0.2, a_s + 0.4, a_s + 0.5, a_s + 0.56, a_s + 0.62, a_s + 0.75,
                            s_s + 0.23, s_s + 0.45, s_s + 0.56, s_s + 0.62, s_s + 0.72, s_s + 0.85, s_s + 1.05,
                            s_s + 1.2, s_s + 1.3, s_s + 1.45, s_s + 1.6, s_s + 1.75]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        shadow, k = ground_shadow(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = compose(p, fr[i][1], bg, shadow, k)
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, '..', 'planche.png')
        sheet.save(out)
        print('planche :', os.path.abspath(out))
        shutil.rmtree(TMP)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    shadow, k = ground_shadow(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        compose(p, fr[i][1], bg, shadow, k).convert('RGB').save(os.path.join(TMP, 'v%04d.png' % i))
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
