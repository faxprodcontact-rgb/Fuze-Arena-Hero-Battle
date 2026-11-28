# Nérith vectorielle ANIMÉE (refonte de tous les héros, 26/11/2026, sur le modèle de Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/nerith/build.py) — la pose souveraine (respiration, la
# tête suit avec retard, la lanterne se balance au bout de la crosse et son pompon avec retard, les pampilles de la
# couronne, le bas de la manche, la flamme de jade qui palpite, l'étincelle de soin, les bijoux qui scintillent chacun
# son tour, le regard qui se pose, méprisant, puis un clignement), l'attaque de base « Perle de jade » (elle ramène le
# bâton en arrière, l'eau de l'air se rassemble en perle contre la lanterne, elle TIENT, puis d'un coup de poignet la
# lanterne file et lance la perle en cloche ; elle éclate sur l'ennemi en fleur de lotus d'eau) et l'attaque spéciale
# « Grâce des eaux » (un trône d'eau monte sous sa robe et l'élève, elle lève la main paume au ciel, une perle de jade se
# forme, la lanterne s'embrase ; la vasque déborde : l'anneau d'eau part d'elle tout autour au sol, sa silhouette
# s'éclaire, une pluie de jade monte et retombe en cercle autour d'elle) — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/nerith/anim.py              # → anim.gif + anim.mp4 dans pixel/sortie/ui/vecto/nerith/
#   python3 refonte-graphique/ui-moderne/heros/nerith/anim.py --planche    # seulement une planche d'images clés (contrôle)
#   python3 refonte-graphique/ui-moderne/heros/nerith/anim.py --planche 1.0 5.4 …   # … à ces instants (s) de la vidéo
#
# Méthode (celle de Kael) : le dessin (nerith.py) est fait de morceaux ; chaque image le redessine dans une POSE
# (buste qui respire, tête, bâton qui tourne autour de la main, lanterne et pompon qui pendent par la pesanteur, manche
# proche qui suit le bras placé par cinématique inverse depuis le poignet, avant-bras qui sort de la manche quand elle
# lève la main). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps), reliées par des courbes douces
# sans dépassement, 24 images par seconde. Les effets d'eau et de jade sont dessinés dans le même style : dégradés, un
# seul contour, aucun flou SVG, jamais de rayons droits répétés. Images intermédiaires : dossier NERITH_TMP (par défaut
# un dossier temporaire du système, jamais dans le dépôt).
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import nerith as N  # noqa: E402
from atelier import sm, ellipse, lock, f as fm  # noqa: E402
from lib import sparkle_shape  # noqa: E402
from nerith import ribbon, crpath  # noqa: E402

ROOT = N.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'nerith')
TMP = os.environ.get('NERITH_TMP', os.path.join(tempfile.gettempdir(), 'nerith-vecto'))
FPS = 24
VIEW = (-22, -40, 290, 163.125)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = N.GRD
WINK = '#0c1846'                      # le contour de l'eau (bleu nuit presque noir)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']
JINK = '#0c3a44'                      # le contour du jade
JADE = ['#ffffff', '#e8fff8', '#a8f4de', '#52d6b8', '#1a8c86', '#0e4a56']
FOE = (226.0, 82.0)                   # l'ennemi (milieu du corps) : visé par l'attaque de base seulement
THRONE_X = 67.0                       # le milieu de l'ourlet : le trône d'eau
RING_FLAT = 0.2                       # l'anneau au sol est un cercle vu en biais : hauteur = 0,2 × largeur


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


NUM = ['breath', 'lean', 'lift', 'hx', 'hy', 'tilt', 'st', 'la', 'pa', 'glow', 'tl', 'tc', 'mp', 'mf', 'ax', 'ay', 'hr', 'sp',
       'mep', 'ec']


def flat(k):
    d = dict(breath=0, lean=0, lift=0, hx=0, hy=0, tilt=0, st=0, la=0, pa=0, glow=0, tl=0, tc=0, mp=0, mf=0, ax=0, ay=0, hr=0,
             sp=1, mep=0, ec=0)
    for key, v in k.items():
        if key == 'head':
            d['hx'], d['hy'] = v
        elif key == 'arm':
            d['ax'], d['ay'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, celles du pixel art)
# 2) L'attaque de base « Perle de jade » : un geste de sceptre, hautain (le menton monte, les paupières tombent). Elle
# ramène le bâton en arrière (la lanterne, en retard, part de l'autre côté), l'eau se rassemble en perle contre la
# lanterne, elle TIENT ; puis d'un coup de poignet elle rabat la crosse vers l'ennemi : la lanterne file au bout de son
# cordon et lance la perle en cloche. La lanterne se balance encore deux fois pendant que le bâton revient droit.
ATTACK = [
    (0, {}),
    (110, dict(st=-4, la=-7, pa=-4, lean=-0.8, head=(0, -1), mep=1, tl=1, tc=1, glow=1)),
    (230, dict(st=-6.6, la=-3.5, pa=-5, lean=-1, head=(-0.8, -1), mep=1, tl=1, tc=0.8, mp=1, glow=2, sp=1.6)),
    (350, dict(st=-7, la=-3, pa=-5, lean=-1, head=(-1, -1), mep=1, tl=0.8, tc=0.6, mp=1, glow=2, sp=1.6)),
    (400, dict(st=8, la=18, pa=8, lean=1, head=(0, -1), mep=1, tl=-1, tc=-1, mp=-1, glow=2, sp=1)),
    (460, dict(st=13, la=-22, pa=6, lean=1.2, head=(1, -1), mep=1, tl=-1, tc=-1, mp=-1, glow=1.2, sp=1.2)),
    (520, dict(st=11, la=-28, pa=-12, lean=1.1, head=(1, -1), mep=1, tl=0, tc=0, mp=0, glow=1, sp=1.2)),
    (580, dict(st=8, la=-12, pa=-16, lean=1, head=(1, 0), mep=0.8, tl=1, tc=1, mp=1, sp=1)),
    (730, dict(st=5, la=8, pa=-10, lean=0.8, head=(1, 0), mep=0.4, tl=1, tc=0, mp=1, sp=1)),
    (840, dict(st=2, la=10, pa=4, lean=0.2, tc=-1, sp=1.6)),
    (940, dict(st=0, la=-4, pa=7, tl=-1, sp=1.3)),
    (1060, dict(la=2, pa=-3)),
    (1220, {}),
]
A_RELEASE, A_HIT = 460, 600           # la perle quitte la lanterne ; elle touche l'ennemi (arrêt sur l'image)

# 3) L'attaque spéciale « Grâce des eaux » (sort d'équipe : grand soin + régénération) : rien ne vise l'ennemi, tout
# naît sur elle et s'étend EN CERCLE autour d'elle. L'eau sourd sous sa robe et monte en trône d'eau qui l'élève ; elle
# lève lentement la main, paume au ciel, et TIENT : une perle de jade se forme au-dessus de sa paume, la lanterne
# s'embrase. Puis la vasque DÉBORDE : la perle s'ouvre, sa silhouette s'éclaire, l'anneau d'eau part d'elle au sol tout
# autour (MOMENT DE LANCEMENT, comme l'image 6 du pixel art, 720 ms) ; la pluie de jade monte en cloche et retombe en
# cercle ; l'anneau s'éloigne et se défait ; la fontaine rentre dans le sol.
SPECIAL = [
    (0, {}),
    (130, dict(head=(0, -1), mep=1, glow=1, tl=-1)),
    (230, dict(lift=3, head=(0, -1), mep=1, glow=1, arm=(0, -3), tl=1, tc=1, mp=1, la=-3, pa=-3)),
    (320, dict(lift=9, head=(0, -1), mep=1, glow=1.2, arm=(0, -8), tl=1, tc=1, mp=1, la=-4, pa=-6, sp=1.8)),
    (410, dict(lift=16, head=(0, 0), mep=1, glow=2, arm=(-1, -12), tl=1, tc=1, mp=1, la=-2, pa=-4, sp=0)),
    (560, dict(lift=20.6, breath=1, head=(0, -1), mep=1, glow=2.2, arm=(-1, -14), tl=0, tc=0, mp=0, la=1, pa=2, sp=0)),
    (650, dict(lift=21, breath=1, head=(0, -1), mep=1, glow=2.4, arm=(-1, -14), tl=0, tc=0, mp=0, la=1, pa=2, sp=0)),
    (720, dict(lift=21, breath=1, head=(0.4, -1), mep=0.6, glow=2.6, arm=(-1, -15), tl=-1, tc=-1, la=0, pa=1, sp=0, ec=0.3)),
    (790, dict(lift=21, breath=1, head=(1, -1), mep=0, glow=3, arm=(-1, -15), tl=-1, tc=-1, la=-1, pa=-1, sp=0, ec=1)),
    (930, dict(lift=21, head=(1, -1), glow=2.6, arm=(-1, -14), tl=0, tc=0, sp=0, ec=0.5)),
    (1020, dict(lift=21, head=(1, 0), glow=2.2, arm=(-1, -14), tl=1, tc=0, sp=0.9, ec=0.1)),
    (1110, dict(lift=20, head=(1, 0), glow=2, arm=(-1, -13), tl=1, tc=1, sp=1.5)),
    (1200, dict(lift=18, head=(0, 0), glow=1.8, arm=(-1, -12), tl=0, tc=1, sp=1.5, la=-2)),
    (1290, dict(lift=15, head=(0, -1), glow=1.2, arm=(-1, -11), tl=-1, tc=0, sp=1.5, la=-3, pa=-2)),
    (1380, dict(lift=10, head=(0, -1), glow=1, arm=(0, -8), sp=1.5, la=-2, pa=-3, tl=-1, tc=-1, mp=-1)),
    (1470, dict(lift=5, head=(0, 0), glow=1, arm=(0, -5), sp=1.4, la=2, pa=-2, tl=-1, tc=-1, mp=-1)),
    (1570, dict(lift=0.6, head=(0, 0.8), glow=0.8, arm=(0, -2), sp=1.3, la=3, pa=4, tl=1, tc=1, mp=1)),
    (1680, dict(la=-1, pa=2, sp=1.1)),
    (1850, {}),
]
S_LAUNCH = 720                         # le moment de lancement (arrêt sur l'image : 720 → 930 ms)


# ======================================================================== la pose souveraine (en boucle)

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


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la lanterne de palais se balance lentement au bout de la crosse (le pompon suit en retard) et sa
    flamme de jade s'avive. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(la=7.0 * math.sin(u), pa=6.0 * math.sin(u - 1.3), glow=0.9 * (0.5 - 0.5 * math.cos(u)))


def idle_offsets(T):
    """La respiration (3 s) et ses mouvements secondaires, en retard les uns sur les autres."""
    u = 2 * math.pi * T / IDLE_T
    return dict(breath=0.5 - 0.5 * math.cos(u), hy=0.35 * math.sin(u - 0.7), tilt=0.5 * math.sin(u - 1.0),
                la=2.6 * math.sin(u - 0.4), pa=3.2 * math.sin(u - 1.5), tl=0.9 * math.sin(u - 2.2), tc=0.7 * math.sin(u - 1.4),
                mp=0.8 * math.sin(u - 2.6), mf=0.6 * math.sin(u - 2.3), glow=0.35 * (0.5 + 0.5 * math.sin(2 * u)),
                sp=0.22 * math.sin(2 * u + 0.6))


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
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = max(P['breath'], 0.0) if act else idl['breath']
    if act:
        P['breath'] = src['breath'] + w * idl['breath']
    P['head'] = (P.pop('hx'), P.pop('hy'))
    P['arm'] = (P.pop('ax'), P.pop('ay'))
    for n, v in signe(T).items():                    # le signe du repos (anim.signe)
        P[n] += w * v
    P['ph'] = 2 * math.pi * T
    # le regard qui se pose, méprisant, puis un clignement (une fois par boucle du repos : le cycle de 4 s d'avant,
    # ramené sur IDLE_T, seulement au repos)
    c4 = (T % IDLE_T) * 4.0 / IDLE_T
    P['mep'] = max(P['mep'], w * env(c4, 2.5, 2.7, 3.15, 3.35))
    P['blink'] = 1.0 if (w > 0.95 and 3.6 <= c4 < 3.68) else 0.0
    # les bijoux scintillent chacun son tour ; les étincelles de la lanterne aussi
    tw = []
    for name, a, b in (('couronne', 0.25, 0.6), ('ceinture', 1.25, 1.6), ('oreille', 2.0, 2.3)):
        k = env(c4, a, (a + b) / 2, (a + b) / 2, b)
        if k > 0.05:
            tw.append((name, k))
    P['tw'] = tw
    P['lspk'] = tuple(max(0.0, 1.0 + 0.35 * math.sin(3 * 2 * math.pi * T / IDLE_T + i * 2.1) + 0.6 * P['glow'] * 0.25) for i in range(3))
    P['_tl'] = tl
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ; une
    forme marquée d'un 4e élément ne reçoit pas de contour (détail peint dedans)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0, jade=False):
    """Une goutte (d'eau, ou de lumière de jade) : ronde devant, effilée derrière (dans le sens de sa course)."""
    if op <= 0.02 or r <= 0.1:
        return ''
    a = math.atan2(vy, vx) if (vx or vy) else math.pi / 2
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    C = JADE if jade else WATER
    gr = g_lin(fig, (x + r, y - r), tail, [(0, C[1]), (0.45, C[2]), (1, C[3])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.38, r * 0.26), '#ffffff', 0.95, 'n')],
                    ink=JINK if jade else WINK, w=1.0, op=op)


def foam(fig, cx, cy, r, op=1.0, seed=0):
    """Une boule d'écume : quelques bulles réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = [(0.0, 0.0, 1.0), (0.78, 0.22, 0.72), (-0.82, 0.3, 0.68), (0.18, -0.58, 0.64), (-0.4, -0.4, 0.5), (1.3, 0.5, 0.45)]
    rnd = rnd[:4 + seed % 3]
    balls = [(cx + dx * r, cy + dy * r, rr * r) for dx, dy, rr in rnd]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r * 0.9), [(0, '#ffffff'), (0.5, WATER[1]), (1, WATER[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), WINK, WINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="#ffffff" opacity="0.9"/>' % (fm(cx + 0.3 * r), fm(cy - 0.35 * r), fm(0.3 * r))
    return '<g opacity="%g">%s%s%s</g>' % (max(0, min(1, op)), sil, col, hi)


def spark(fig, c, r, op=1.0):
    """Une étincelle de jade à quatre branches, un contour de jade sombre, un cœur blanc."""
    if r <= 0.2 or op <= 0.02:
        return ''
    sh = sparkle_shape(c[0], c[1], r, 0.28)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#ffffff'), (0.5, JADE[1]), (1, JADE[3])])
    return outlined([(sh, gr, 1), (ellipse(c[0], c[1], r * 0.3, r * 0.3), '#ffffff', 1, 'n')], ink=JINK, w=1.0, op=op)


def halo(fig, c, r, color, op):
    """Une lueur douce (dégradé radial, aucun flou)."""
    if op <= 0.02 or r <= 0.3:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(fig, c, r, [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]))


def pearl(fig, c, r, stretch=None, op=1.0, core=1.0):
    """La perle d'eau au cœur de jade (la flamme de la lanterne) : une boule modelée, éclairée en haut à droite ; stretch
    = (dx, dy) : elle s'étire derrière elle dans sa course."""
    if r <= 0.2 or op <= 0.02:
        return ''
    if stretch and math.hypot(*stretch) > 0.5:
        a = math.atan2(-stretch[1], -stretch[0])      # vers l'avant
        pts = [(c[0] + r * math.cos(a + math.radians(d)), c[1] + r * math.sin(a + math.radians(d))) for d in (-100, -50, 0, 50, 100)]
        tail = (c[0] - math.cos(a) * (r + math.hypot(*stretch)), c[1] - math.sin(a) * (r + math.hypot(*stretch)))
        body = sm(pts + [tail], sharp=(5,), t=0.95)
    else:
        body = ellipse(c[0], c[1], r, r)
    gr = fig.rad(c[0] + 0.35 * r, c[1] - 0.4 * r, r * 1.5, r * 1.5, [(0, WATER[0]), (0.3, WATER[1]), (0.65, WATER[2]), (1, WATER[3])])
    items = [(body, gr, 1),
             (ellipse(c[0] - 0.1 * r, c[1] + 0.1 * r, r * 0.5 * core, r * 0.5 * core), fig.rad(c[0], c[1], r * 0.55, r * 0.55,
                                                                                         [(0, '#ffffff'), (0.4, JADE[2]), (1, JADE[3])]), 1, 'n'),
             (ribbon([(c[0] - 0.7 * r, c[1] + 0.55 * r), (c[0] - 0.1 * r, c[1] + 0.78 * r), (c[0] + 0.55 * r, c[1] + 0.6 * r)],
                     [0.1, 0.22 * r, 0.1]), WATER[4], 0.5, 'n'),
             (ellipse(c[0] + 0.38 * r, c[1] - 0.42 * r, 0.3 * r, 0.22 * r), '#ffffff', 1, 'n')]
    return outlined(items, w=1.2, op=op)


def petal(fig, base, ang, length, width, op=1.0, cut=0.0, jade=False):
    """Un pétale d'eau pointu (lotus) : de la base vers la pointe, un peu courbé, éclairé sur son bord droit ; cut
    (0..1) : sa base se détache (il se défait)."""
    if length < 1 or op <= 0.02:
        return ''
    a = math.radians(ang)
    d = (math.cos(a), -math.sin(a))
    side = (d[1], -d[0])
    s = 1 if ang < 90 else -1
    p0 = (base[0] + d[0] * length * cut, base[1] + d[1] * length * cut)
    p1 = (base[0] + d[0] * length * 0.4 + side[0] * s * width * 0.2, base[1] + d[1] * length * 0.4 + side[1] * s * width * 0.2)
    p2 = (base[0] + d[0] * length * 0.75 + side[0] * s * width * 0.35, base[1] + d[1] * length * 0.75 + side[1] * s * width * 0.35)
    p3 = (base[0] + d[0] * length + side[0] * s * width * 0.2, base[1] + d[1] * length + side[1] * s * width * 0.2)
    w = width * (1 - cut * 0.6)
    sh = lock(p0, p1, p2, p3, w, n=12, bulge=0.75, tipw=0.0)
    vein = lock(p0, p1, p2, ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2), w * 0.36, n=8, bulge=0.4)
    C = JADE if jade else WATER
    gr = g_lin(fig, p0, p3, [(0, C[3]), (0.45, C[2]), (1, C[1])])
    return outlined([(sh, gr, 1), (vein, '#ffffff', 0.55, 'n')], ink=JINK if jade else WINK, w=1.2, op=op)


def ring_svg(fig, c, rx, ry, w, op, tones=None):
    """L'anneau d'eau au sol (un ruban le long d'une ellipse, plus épais devant), sa crête d'écume ; rend
    (silhouettes + couleurs) en SVG brut, à poser derrière ET devant (découpé : moitié de devant)."""
    if op <= 0.02 or rx < 1 or w < 0.15:
        return ''
    n = 48
    pts = [(c[0] + rx * math.cos(2 * math.pi * i / n), c[1] + ry * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    ws = [w * (0.7 + 0.3 * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    outer = [(c[0] + (rx + wi / 2) * math.cos(2 * math.pi * i / n), c[1] + (ry + wi / 2 * RING_FLAT * 2.2) * math.sin(2 * math.pi * i / n)) for i, wi in enumerate(ws)]
    inner = [(c[0] + (rx - wi / 2) * math.cos(2 * math.pi * i / n), c[1] + max(0.2, ry - wi / 2 * RING_FLAT * 2.2) * math.sin(2 * math.pi * i / n)) for i, wi in enumerate(ws)]
    from lib import Shape
    band = Shape(sm(outer[:-1], t=0.9).subs + sm(inner[:-1], t=0.9).subs, evenodd=True)
    crest = [(c[0] + (rx + ws[i] * 0.2) * math.cos(2 * math.pi * i / n), c[1] + (ry + ws[i] * 0.1) * math.sin(2 * math.pi * i / n) - 0.25 * ws[i])
             for i in range(n + 1)]
    gr = fig.lin(c[0] + rx, c[1] - ry, c[0] - rx, c[1] + ry, [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])])
    hi = ribbon(crest[30:47], [0.1] + [max(0.2, w * 0.28)] * 15 + [0.1])
    hi2 = ribbon(crest[3:20], [0.1] + [max(0.2, w * 0.2)] * 15 + [0.1])
    return outlined([(band, gr, 1), (hi, '#ffffff', 0.9, 'n'), (hi2, '#ffffff', 0.7, 'n')], w=1.2, op=op)


def clip_below(fig, y, inner):
    """Ce SVG, découpé sous la ligne y (la moitié de devant d'un anneau posé au sol, la lèvre d'une vasque)."""
    cid = fig.uid('cb')
    fig.defs.append('<clipPath id="%s"><rect x="-400" y="%s" width="1200" height="600"/></clipPath>' % (cid, fm(y)))
    return '<g clip-path="url(#%s)">%s</g>' % (cid, inner)


# ---- l'attaque de base : la perle d'eau au cœur de jade, la fleur de lotus

CACHE = {}


def lob(t):
    """La course en cloche de la perle : de la lanterne à l'ennemi, en passant haut."""
    p0 = CACHE['release']
    p2 = (FOE[0], FOE[1] - 4)
    p1 = ((p0[0] + p2[0]) / 2 - 6, min(p0[1], p2[1]) - 46)
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def fx_attack(tl):
    def f(fig, ctx):
        fc = ctx['flame']
        back, front = fig.fx_back, fig.fx_front
        # l'eau de l'air vient se rassembler contre la lanterne (gouttes qui arrivent en spirale), la perle grossit
        if tl < A_RELEASE:
            c = (fc[0] + 9.0, fc[1] + 1.2)
            g = smooth((tl - 20) / 300)
            if tl < 360:
                for i, (dx, dy, sz, ph) in enumerate(((16, -12, 1.2, 0.0), (22, 6, 1.1, 0.25), (8, 14, 0.9, 0.45), (2, -15, 0.8, 0.6),
                                                       (-6, 12, 0.7, 0.7))):
                    k = smooth((tl - 30 - ph * 160) / 170)
                    if 0 < k < 1:
                        sw = 1 - k
                        x = c[0] + dx * sw + 3 * math.sin(k * 3) * sw
                        y = c[1] + dy * sw
                        front.append(drop(fig, x, y, -dx, -dy, sz, op=min(1, 4 * k)))
            if tl < 350:
                front.append(halo(fig, c, 5 + 4 * g, JADE[2], 0.35 * g))
                front.append(pearl(fig, c, 1.6 + 2.2 * g))
            else:
                # le coup de poignet : la perle suit la lanterne, étirée ; une traîne d'eau suit l'arc de la lanterne
                k = smooth((tl - 350) / 110)
                c = (fc[0] + 9.0 + 2.0 * k, fc[1] + 1.2 - 3.2 * k)
                pts = crpath([(c[0] - 15, c[1] + 9), (c[0] - 9, c[1] + 8.5), (c[0] - 3, c[1] + 4.5), (c[0], c[1])], 14)
                ws = [0.3 + 3.0 * (i / 14) ** 1.4 for i in range(15)]
                tr = ribbon(pts, ws)
                back.append(outlined([(tr, g_lin(fig, pts[0], pts[-1], [(0, WATER[3]), (1, WATER[1])]), 1)], w=1.1, op=0.9))
                front.append(pearl(fig, c, 3.9 + 0.3 * k, stretch=(5 * k, 3 * k)))
        elif tl < A_HIT:
            # la perle vole en cloche ; derrière elle, une traîne de gouttes de plus en plus petites (le long de la courbe)
            t = smooth((tl - A_RELEASE) / (A_HIT - A_RELEASE)) * 0.92 + 0.08 * (tl - A_RELEASE) / (A_HIT - A_RELEASE)
            c = lob(t)
            d = lob(min(1, t + 0.02))
            e = lob(max(0, t - 0.02))
            v = (d[0] - e[0], d[1] - e[1])
            L = math.hypot(*v) or 1
            v = (v[0] / L, v[1] / L)
            for dt, sz in ((0.08, 1.4), (0.15, 1.0), (0.22, 0.7)):
                if t - dt > 0.02:
                    q = lob(t - dt)
                    front.append(drop(fig, q[0], q[1], v[0], v[1], sz))
            front.append(halo(fig, c, 8, JADE[2], 0.25))
            front.append(pearl(fig, c, 4.6, stretch=(-v[0] * 5, -v[1] * 5)))
        # la perle éclate sur l'ennemi en fleur de lotus : le bouton s'ouvre, la fleur grande ouverte, les pétales se
        # défont en gouttes, les dernières retombent, une flaque
        if tl >= A_HIT - 10:
            u = tl - A_HIT
            c = (FOE[0], FOE[1] + 2)
            op = 1 - smooth((u - 420) / 200)
            opn = smooth(u / 150)
            grow = 0.55 + 0.45 * smooth(u / 180)
            cut = smooth((u - 240) / 160)
            drop_y = 8 * smooth((u - 250) / 200)
            # le pop de l'impact (l'eau éclate en couronne d'écume), puis la fleur
            if u < 140:
                back.append(halo(fig, (c[0], c[1] - 3), 14, WATER[1], 0.6 * (1 - u / 140)))
                front.append(foam(fig, c[0], c[1] - 2, 4.2 * (1 - u / 200), seed=2))
            PET = ((90, 22, 7.6), (62, 20, 7.0), (118, 20, 7.0), (34, 15, 6.4), (146, 15, 6.4))
            for i, (ang, ln, wd) in enumerate(PET):
                a2 = 90 + (ang - 90) * (0.35 + 0.7 * opn)
                b = (c[0], c[1] + (drop_y if cut > 0 else 0))
                if u < 520:
                    (back if i == 0 else front).append(petal(fig, b, a2, ln * grow, wd, op=op, cut=cut))
            if 120 < u < 420:
                k = smooth((u - 120) / 80)
                front.append(pearl(fig, (c[0], c[1] - 2), 2.2 * k * (1 - smooth((u - 300) / 120)), op=op))
            # les étincelles de jade qui montent de la fleur
            for i, (dx, sz, t0) in enumerate(((0, 1.6, 120), (-9, 1.2, 180), (8, 1.0, 230), (3, 0.9, 330))):
                k = (u - t0) / 400
                if 0 < k < 1:
                    front.append(spark(fig, (c[0] + dx + 2 * math.sin(k * 5 + i), c[1] - 8 - 26 * k), sz * (1 - 0.3 * k), op=1 - smooth((k - 0.6) / 0.4)))
            # les gouttes des pétales qui se défont, puis la flaque au sol
            if u > 240:
                for j in range(7):
                    a = math.radians(30 + 20 * j)
                    k = (u - 240 - 12 * j) / 320
                    if 0 < k < 1:
                        x = c[0] + (10 + 10 * k) * math.cos(a) * 1.1
                        y = c[1] - 10 * math.sin(a) * (1 - k) + 34 * k * k
                        if y < GR - 1:
                            front.append(drop(fig, x, y, math.cos(a) * 0.3, 1.0, 1.0 - 0.3 * (j % 2), op=1 - smooth((k - 0.8) / 0.2)))
                k = smooth((u - 360) / 200) * (1 - smooth((u - 560) / 300))
                if k > 0.02:
                    pud = ellipse(c[0], GR - 0.2, 16 * k + 2, 1.4 * k + 0.3)
                    back.append(outlined([(pud, g_lin(fig, (c[0] + 16, GR - 2), (c[0] - 16, GR + 2), [(0, WATER[1]), (1, WATER[3])]), 1)],
                                         w=1.0, op=k))
    return f


# ---- l'attaque spéciale : le trône d'eau, la perle de jade, l'anneau, la pluie de jade

def tint(fig, k):
    """Sa silhouette s'éclaire de jade presque blanc (le soin passe en elle) ; au plus fort, une lueur de jade autour du
    contour. Ajouté en premier des effets de devant (juste sur ses morceaux)."""
    if k <= 0.02:
        return
    paths, halo_ = [], []
    for p in fig.parts:
        if not p.outline:
            continue
        tf = ' transform="matrix(%s)"' % ' '.join(fm(v) for v in p.M) if p.M != (1, 0, 0, 1, 0, 0) else ''
        paths.append('<path d="%s"%s/>' % (p.shape.d(), tf))
    body = ''.join(paths)
    fig.fx_front.insert(0, '<g fill="#e8fff8" opacity="%g">%s</g>' % (0.22 * k, body))
    fig.fx_back.append('<g fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round" opacity="%g">%s</g>' % (
        JADE[2], JADE[2], fm(2 * 0.95 + 1.6 * k), min(1, 1.1 * k), body))


def fountain(fig, ctx, lift, phase, rise, spill):
    """Le trône d'eau sous elle : la flaque au sol, la colonne qui ondule (serrée au milieu, évasée au pied), la vasque
    (sa surface derrière l'ourlet, sa lèvre devant), deux accoudoirs d'eau qui s'enroulent en volute et retombent en
    cascade ; quand elle déborde, la lèvre gonfle et les cascades grossissent."""
    back, front = fig.fx_back, fig.fx_front
    cx = THRONE_X
    G = GR + 0.2
    # la flaque
    rx, ry = 26 + 22 * rise, 1.4 + 1.4 * rise
    if rise > 0.02:
        pud = ellipse(cx, G - 0.4, rx, ry)
        back.append(outlined([(pud, g_lin(fig, (cx + rx, G - ry), (cx - rx, G + ry), [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])]), 1),
                              (ribbon([(cx - rx * 0.5, G - 0.9 * ry), (cx, G - 1.25 * ry), (cx + rx * 0.7, G - 1.0 * ry)], [0.1, 0.5, 0.1]), '#ffffff', 0.85, 'n')],
                             w=1.1, op=min(1, rise * 2)))
    if lift < 1.0:
        return
    top = G - lift
    # la colonne : large en haut, serrée au milieu, évasée au pied ; ses bords ondulent
    L, R = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = top + (G - top) * t
        hw = 22 - 10 * math.sin(math.pi * min(1.0, t * 1.12)) * (1 - 0.45 * spill) + 9 * t * t
        hw = min(hw, 4 + lift * 1.6)
        wob = 1.1 * math.sin(phase + t * 6.0)
        off = 0.8 * math.sin(phase * 0.7 + t * 3.0)
        L.append((cx - hw + wob + off, y))
        R.append((cx + hw + wob * 0.6 + off, y))
    col = sm(L + R[::-1], sharp=(n, n + 1), t=0.8)
    gr = g_lin(fig, (cx + 24, top), (cx - 24, G), [(0, WATER[1]), (0.35, WATER[2]), (0.75, WATER[3]), (1, WATER[4])])
    hl = ribbon(crpath([(R[1][0] - 3, R[1][1]), (R[n // 2][0] - 2.4, R[n // 2][1]), (R[n - 1][0] - 4, R[n - 1][1])], 10), [0.2, 1.6, 1.2, 0.2])
    hl2 = ribbon(crpath([(L[2][0] + 4, L[2][1]), (L[n // 2][0] + 3, L[n // 2][1]), (L[n - 2][0] + 5, L[n - 2][1])], 10), [0.2, 0.9, 0.6, 0.2])
    back.append(outlined([(col, gr, 1), (hl, '#ffffff', 0.75, 'n'), (hl2, WATER[1], 0.5, 'n')], w=1.3))
    # les accoudoirs : de chaque côté, un bras d'eau monte de la lèvre et s'enroule vers dehors ; une cascade en retombe
    if lift >= 4:
        h = min(14.0, lift * 0.9)
        for sgn in (-1, 1):
            base = (cx + sgn * 26, top + 1.5)
            cc = (cx + sgn * 33.4, top - h + 0.6)
            spiral = [base, (cx + sgn * 28, top - h * 0.5)]
            for j in range(11):
                a = math.radians(180 + j * 30)
                rr = 3.4 * (1 - 0.62 * j / 10)
                spiral.append((cc[0] + sgn * rr * math.cos(a), cc[1] + rr * math.sin(a)))
            path = crpath(spiral, 24)
            ws = [4.6 - 2.2 * i / 24 for i in range(25)]
            arm = ribbon(path, ws)
            back.append(outlined([(arm, g_lin(fig, base, cc, [(0, WATER[3]), (0.6, WATER[2]), (1, WATER[1])]), 1),
                                  (ribbon(path[2:14], [0.1, 0.9, 0.6, 0.1]), '#ffffff', 0.7, 'n')], w=1.2))
            q = (cx + sgn * 37.5, top - h + 4)
            fall = crpath([q, (q[0] + sgn * 2.6, q[1] + 5), (q[0] + sgn * 4, (q[1] + G) / 2 + 2), (q[0] + sgn * 3.2, G - 1.6)], 14)
            fw = [2.6 - 1.0 * k / 14 + 0.35 * math.sin(phase * 1.3 + k * 0.9) + 1.0 * spill for k in range(15)]
            back.append(outlined([(ribbon(fall, fw), g_lin(fig, q, (q[0], G), [(0, WATER[2]), (1, WATER[3])]), 1),
                                  (ribbon(fall[1:10], [0.1, 0.6, 0.1]), '#ffffff', 0.6, 'n')], w=1.1))
            back.append(foam(fig, q[0] + sgn * 3.4, G - 1.6, 2.4 + 1.0 * spill, seed=int(phase) + (sgn > 0)))
    # la vasque : sa surface (derrière l'ourlet), sa lèvre de devant (devant l'ourlet), une volute d'écume de chaque côté
    vrx = 20 + 13 * min(1.0, lift / 10) + 2 * spill
    vry = 3.4 + 1.4 * min(1.0, lift / 10) + 0.8 * spill
    vc = (cx, top + 0.6)
    bowl = ellipse(vc[0], vc[1], vrx, vry)
    grb = g_lin(fig, (vc[0] + vrx, vc[1] - vry), (vc[0] - vrx, vc[1] + vry), [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])])
    rim = ribbon([(vc[0] - vrx * 0.8, vc[1] - vry * 0.55), (vc[0], vc[1] - vry * 0.95), (vc[0] + vrx * 0.85, vc[1] - vry * 0.5)], [0.1, 0.8, 0.1])
    lip = ribbon([(vc[0] + vrx * math.cos(math.radians(a)), vc[1] + vry * math.sin(math.radians(a))) for a in range(0, 181, 15)],
                 [0.4] + [2.2 + 0.8 * spill] * 11 + [0.4])
    bowl_svg = outlined([(bowl, grb, 1), (rim, '#ffffff', 0.8, 'n'), (lip, WATER[1], 0.9, 'n')], w=1.3)
    back.append(bowl_svg)
    front.append(clip_below(fig, vc[1] + 0.2, outlined([(bowl, grb, 1), (lip, WATER[1], 0.95, 'n'),
                                                         (ribbon([(vc[0] - vrx * 0.5, vc[1] + vry * 0.75), (vc[0] + vrx * 0.1, vc[1] + vry * 0.98),
                                                                  (vc[0] + vrx * 0.6, vc[1] + vry * 0.8)], [0.1, 0.7, 0.1]), '#ffffff', 0.8, 'n')], w=1.3)))
    front.append(spark(fig, (vc[0] - 9 + 3 * math.sin(phase), vc[1] + 1.6), 1.0))


def palm_pearl(fig, ctx, level, t):
    """La perle de lumière de jade au-dessus de la paume : elle se forme (0..1), elle s'ouvre en éclat (1..2), s'efface."""
    c = ctx['spark']
    front = fig.fx_front
    if level <= 1:
        r = 0.8 + 2.8 * level
        front.append(halo(fig, c, 6 + 6 * level, JADE[2], 0.45 * level))
        for i in range(3):
            a = t * 3 + i * 2.1
            q = (c[0] + (7 - 4 * level) * math.cos(a), c[1] + (5 - 3 * level) * math.sin(a))
            front.append(spark(fig, q, 0.9, op=1 - level * 0.6))
        sh = ellipse(c[0], c[1], r, r)
        gr = fig.rad(c[0] + 0.35 * r, c[1] - 0.4 * r, r * 1.4, r * 1.4, [(0, '#ffffff'), (0.35, JADE[1]), (0.8, JADE[3]), (1, JADE[4])])
        front.append(outlined([(sh, gr, 1), (ellipse(c[0] + 0.35 * r, c[1] - 0.4 * r, 0.3 * r, 0.25 * r), '#ffffff', 1, 'n')], ink=JINK, w=1.1))
    else:
        k = level - 1
        front.append(halo(fig, c, 14 + 10 * k, JADE[1], 0.6 * (1 - k)))
        # la perle s'ouvre : quatre pétales de lumière qui s'écartent (une fleur, pas des rayons), son cœur blanc
        for i, ang in enumerate((90, 10, 170, 270)):
            ln = 4 + 6 * k
            a = math.radians(ang + 30 * k)
            b = (c[0] + 1.5 * k * math.cos(a), c[1] - 1.5 * k * math.sin(a))
            front.append(petal(fig, b, math.degrees(a), ln, 3.2 * (1 - 0.4 * k), op=1 - smooth((k - 0.25) / 0.35), jade=True))
        front.append(spark(fig, c, 3.4 * (1 - 0.5 * k), op=1 - smooth(k / 0.7)))


def lantern_flare(fig, ctx, level):
    """La flamme de jade de la lanterne s'embrase : une lueur de jade et des petites étincelles qui tournent autour."""
    fc = ctx['flame']
    if level <= 0.02:
        return
    fig.fx_back.append(halo(fig, fc, 12 + 6 * level, JADE[2], 0.25 * level))
    ph = ctx['P']['ph']
    for i in range(3):
        a = ph * 0.8 + i * 2.1
        q = (fc[0] + 10 * math.cos(a), fc[1] + 6 * math.sin(a))
        fig.fx_front.append(spark(fig, q, 0.7 + 0.35 * level, op=min(1, level)))


def ground_ring(fig, rx, w, op, tag):
    """L'anneau d'eau posé au sol autour d'elle : sa moitié du fond derrière elle, sa moitié de devant devant la fontaine."""
    c = (THRONE_X, GR - 0.6)
    ry = rx * RING_FLAT
    svg = ring_svg(fig, c, rx, ry, w, op)
    if svg:
        fig.fx_back.append(svg)
        fig.fx_front.append(clip_below(fig, c[1], ring_svg(fig, c, rx, ry, w, op)))


def jade_rain(fig, t, lift):
    """La pluie de jade : des gouttes de lumière lancées par la fontaine dans toutes les directions montent en cloche et
    retombent en cercle autour d'elle (celles du fond plus haut, celles de devant plus bas) ; elles s'allument en petites
    étincelles là où elles touchent le sol."""
    for i in range(11):
        a = math.radians(i * 360 / 11 + 12)
        R = 42 + 10 * ((i * 7) % 3)
        k = t * (1.0 + 0.12 * (i % 3)) - 0.05 * (i % 4)
        if k <= 0:
            continue
        top = (THRONE_X + 31 * math.cos(a), GR - lift + 0.6 + 4.5 * math.sin(a))     # elles partent du bord de la vasque
        gx, gy = THRONE_X + R * math.cos(a), GR - 0.5 + R * RING_FLAT * math.sin(a)
        if k < 1:
            x = top[0] + (gx - top[0]) * k
            y = top[1] + (gy - top[1]) * k - 34 * 4 * k * (1 - k) * (0.85 + 0.15 * (i % 2))
            vx = gx - top[0]
            vy = (gy - top[1]) - 34 * 4 * (1 - 2 * k)
            el = drop(fig, x, y, vx, vy, 1.15, jade=True)
            (fig.fx_back if math.sin(a) < 0 else fig.fx_front).append(el)
        elif k < 1.5:
            q = (k - 1) / 0.5
            el = spark(fig, (gx, gy - 1.2), 1.8 * (1 - q) + 0.4, op=1 - q)
            (fig.fx_back if math.sin(a) < 0 else fig.fx_front).append(el)


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        lift = P['lift']
        ph = P['ph']
        # le trône d'eau
        rise = smooth(tl / 300) * (1 - smooth((tl - 1500) / 300))
        spill = env(tl, 660, 740, 900, 1250)
        fountain(fig, ctx, lift, ph * 0.9, rise, spill)
        # la perle de jade au-dessus de la paume : elle se forme (410 → 650), s'ouvre au lancement, s'efface
        if 380 < tl < 1060:
            if tl < 720:
                palm_pearl(fig, ctx, smooth((tl - 380) / 270), ph)
            else:
                palm_pearl(fig, ctx, 1 + smooth((tl - 720) / 300), ph)
        lantern_flare(fig, ctx, env(tl, 300, 650, 950, 1400) * 1.6)
        # l'anneau d'eau part d'elle au sol tout autour, une seconde onde plus fine le suit ; ils se défont
        if tl > 680:
            u = (tl - 680) / 1000
            for d0, w0 in ((0.0, 3.6), (0.16, 2.0)):
                uu = u - d0
                if uu <= 0:
                    continue
                rx = 30 + 92 * (1 - (1 - min(1, uu)) ** 2)
                op = 1 - smooth((uu - 0.55) / 0.4)
                ground_ring(fig, rx, w0 * (1 - 0.5 * min(1, uu)), op, d0)
        if tl > 720:
            jade_rain(fig, (tl - 720) / 520, 21)
        # quelques étincelles de jade qui restent sur elle
        if tl > 1350:
            for (gx, gy, t0) in ((ctx['head'][0] - 8, ctx['head'][1] - 14, 1350), (ctx['chest'][0] + 16, ctx['chest'][1] - 8, 1450),
                                 (ctx['chest'][0] - 22, ctx['chest'][1] + 16, 1560)):
                k = (tl - t0) / 300
                if 0 < k < 1:
                    fig.fx_front.append(spark(fig, (gx, gy), 2.2 * math.sin(math.pi * k)))
        tint(fig, P['ec'])
    return f


# ======================================================================== montage

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
    ImageDraw.Draw(sh).ellipse([cx - 38 * k, fy - 3.0 * k, cx + 38 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
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
    P = pose_at(T, act, t0)
    fx = []
    if act:
        tl = (T - t0) * 1000
        if act == 'attack':
            if 'release' not in CACHE:
                Pr = pose_at(t0 + (A_RELEASE - 1) / 1000.0, act, t0)
                ctx = N.build(pose=Pr).ctx
                CACHE['release'] = (ctx['flame'][0] + 11.0, ctx['flame'][1] - 2.0)
            fx = [fx_attack(tl)]
        else:
            fx = [fx_special(tl)]
    return N.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        moments = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]] or \
            [1.0, 3.3, a_s + 0.2, a_s + 0.38, a_s + 0.44, a_s + 0.52, a_s + 0.66, a_s + 0.8,
             s_s + 0.25, s_s + 0.5, s_s + 0.75, s_s + 0.85, s_s + 1.0, s_s + 1.2, s_s + 1.45, s_s + 1.7]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, 'planche.png')
        sheet_.save(out)
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
    for width, colors in ((400, 128), (380, 96), (360, 80)):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                        '-vf', 'fps=12,scale=%d:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=%d:stats_mode=diff[p];'
                        '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle' % (width, colors), gifp], check=True)
        if os.path.getsize(gifp) <= 3 * 1024 * 1024:
            break
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : le trône d'eau est UNE silhouette (colonne, accoudoirs en volute, cascades et vasque fondus,
# reflets peints dedans, sans contour sombre), la perle de jade une boule de lumière, les anneaux et la pluie de jade
# des rubans et des gouttes étirées par leur course, les étincelles des lumières ; l'attaque garde son dessin.
import effets_pro as E  # noqa: E402
from shapely.geometry import box as _box  # noqa: E402


def _fountain(fig, ctx, lift, phase, rise, spill):
    back, front = fig.fx_back, fig.fx_front
    cx = THRONE_X
    G = GR + 0.2
    rx, ry = 26 + 22 * rise, 1.4 + 1.4 * rise
    if rise > 0.02:
        pud = E.ellipse_g(cx, G - 0.4, rx, ry)
        back.append(E.group([E.bloom(fig, pud, E.pal('eau')['halo'], 0.3), E.path(pud, E.lin(fig, (cx + rx, G - ry), (cx - rx, G + ry),
                                                                                              [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])]))], min(1, rise * 2)))
    if lift < 1.0:
        return
    top = G - lift
    L, R = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = top + (G - top) * t
        hw = 22 - 10 * math.sin(math.pi * min(1.0, t * 1.12)) * (1 - 0.45 * spill) + 9 * t * t
        hw = min(hw, 4 + lift * 1.6)
        wob = 1.1 * math.sin(phase + t * 6.0)
        off = 0.8 * math.sin(phase * 0.7 + t * 3.0)
        L.append((cx - hw + wob + off, y))
        R.append((cx + hw + wob * 0.6 + off, y))
    parts = [E.poly(L + R[::-1])]
    if lift >= 4:
        h = min(14.0, lift * 0.9)
        for sgn in (-1, 1):
            base = (cx + sgn * 26, top + 1.5)
            cc = (cx + sgn * 33.4, top - h + 0.6)
            spiral = [base, (cx + sgn * 28, top - h * 0.5)]
            for j in range(11):
                a = math.radians(180 + j * 30)
                rr = 3.4 * (1 - 0.62 * j / 10)
                spiral.append((cc[0] + sgn * rr * math.cos(a), cc[1] + rr * math.sin(a)))
            path = crpath(spiral, 24)
            parts.append(E.strip(path, [4.6 - 2.2 * i / (len(path) - 1) for i in range(len(path))]))
            q = (cx + sgn * 37.5, top - h + 4)
            fall = crpath([q, (q[0] + sgn * 2.6, q[1] + 5), (q[0] + sgn * 4, (q[1] + G) / 2 + 2), (q[0] + sgn * 3.2, G - 1.6)], 14)
            parts.append(E.strip(fall, [2.6 - 1.0 * k / (len(fall) - 1) + 0.35 * math.sin(phase * 1.3 + k * 0.9) + 1.0 * spill for k in range(len(fall))]))
            front.append(E.nuage(fig, q[0] + sgn * 3.4, G - 1.8, 2.6 + 1.0 * spill, 'eau', seed=int(phase) + (sgn > 0)))
    vrx = 20 + 13 * min(1.0, lift / 10) + 2 * spill
    vry = 3.4 + 1.4 * min(1.0, lift / 10) + 0.8 * spill
    vc = (cx, top + 0.6)
    bowl = E.ellipse_g(vc[0], vc[1], vrx, vry + 0.6)
    g = E.fuse(parts + [bowl], close=1.2).intersection(_box(-1e4, -1e4, 1e4, G + 0.2))
    P = E.pal('eau')
    hi = (cx + 24, top - 6)
    lo = (cx - 24, G)
    body = [E.bloom(fig, g, P['halo'], 0.35, grow=1.4, s=1.6),
            E.path(g, E.lin(fig, hi, lo, [(0, WATER[1]), (0.35, WATER[2]), (0.75, WATER[3]), (1, WATER[4])])),
            E.path(E.inside(E.lit(g, 1.4), g, 0.2), '#ffffff', 0.7),
            E.path(E.inside(E.ellipse_g(vc[0] + 1, vc[1] - 0.6, vrx * 0.82, vry * 0.6), g), WATER[1], 0.8)]
    back.append(E.group(body))
    # devant elle : la lèvre de la vasque (la moitié basse de la vasque, dans la même silhouette)
    lip = E.inside(bowl.intersection(_box(-1e4, vc[1] + 0.2, 1e4, 1e4)), g)
    front.append(E.group([E.path(lip, E.lin(fig, (vc[0] + vrx, vc[1]), (vc[0] - vrx, vc[1] + vry), [(0, WATER[1]), (1, WATER[3])])),
                          E.path(E.inside(E.lit(lip, 0.9), lip), '#ffffff', 0.8)]))


def _palm_pearl(fig, ctx, level, t):
    c = ctx['spark']
    if level <= 1:
        fig.fx_front.append(E.lumiere(fig, c, 8 + 8 * level, 0.6 * level, 'jade'))
        fig.fx_front.append(E.boule(fig, c, 0.8 + 2.8 * level, t * 40, 'jade'))
    else:
        k = level - 1
        fig.fx_front.append(E.lumiere(fig, c, 16 + 12 * k, 1 - k, 'jade'))
        fig.fx_front.append(E.couronne(fig, c, 3 + 7 * k, 2.6 * (1 - k) + 0.4, t * 40, 0.0, 'jade', op=1 - smooth((k - 0.25) / 0.5), seed=1))


def _ground_ring(fig, rx, w, op, tag):
    c = (THRONE_X, GR - 0.6)
    ry = rx * RING_FLAT
    fig.fx_back.append(E.ruban(fig, E.arc_ell(c, rx, ry, 180, 360), w * 1.7, 'eau', op=op * 0.75, kind='fuseau'))
    fig.fx_front.append(E.ruban(fig, E.arc_ell(c, rx, ry, 0, 180), w * 1.7, 'eau', op=op, kind='fuseau'))


def _jade_rain(fig, t, lift):
    for i in range(7):
        a = math.radians(i * 360 / 7 + 12)
        R = 42 + 10 * ((i * 7) % 3)
        k = t * (1.0 + 0.12 * (i % 3)) - 0.05 * (i % 4)
        if k <= 0:
            continue
        top = (THRONE_X + 31 * math.cos(a), GR - lift + 0.6 + 4.5 * math.sin(a))
        gx, gy = THRONE_X + R * math.cos(a), GR - 0.5 + R * RING_FLAT * math.sin(a)
        lay = fig.fx_back if math.sin(a) < 0 else fig.fx_front
        if k < 1:
            x = top[0] + (gx - top[0]) * k
            y = top[1] + (gy - top[1]) * k - 34 * 4 * k * (1 - k) * (0.85 + 0.15 * (i % 2))
            vx = gx - top[0]
            vy = (gy - top[1]) - 34 * 4 * (1 - 2 * k)
            lay.append(E.goutte(fig, x, y, vx * 3, vy * 3, 1.2, 'jade'))
        elif k < 1.5:
            q = (k - 1) / 0.5
            lay.append(E.lumiere(fig, (gx, gy - 1.2), 5 * (1 - q) + 1, 1 - q, 'jade'))


E.accrocher(sys.modules[__name__], {
    'fountain': _fountain,
    'palm_pearl': _palm_pearl,
    'ground_ring': _ground_ring,
    'jade_rain': _jade_rain,
    'spark': lambda fig, c, r, op=1.0: E.lumiere(fig, c, r * 2.6, op, 'jade'),
    'halo': lambda fig, c, r, color, op: E.lumiere(fig, c, r, op, 'jade'),
})


if __name__ == '__main__':
    main()
