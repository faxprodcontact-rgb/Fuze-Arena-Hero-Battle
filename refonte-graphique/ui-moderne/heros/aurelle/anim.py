# Aurelle vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/auriel/build.py, ancien nom) — respiration, attaque de base « Double coup de
# massue », attaque spéciale « Rocher du cyclope » — mais dans le style lisse de l'interface, sur le modèle de Kael
# (../kael/anim.py) et de Taurok (../taurok/anim.py, dont les outils d'effets de la terre sont recopiés ici).
#
#   python3 refonte-graphique/ui-moderne/heros/aurelle/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/aurelle/)
#   python3 refonte-graphique/ui-moderne/heros/aurelle/anim.py --planche [instants en s] [--sortie image.png]
#
# Méthode : le dessin (aurelle.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette : buste
# qui respire et se penche depuis les hanches, tête, œil qui roule et cligne, épaules, pagne ; le bras proche est placé
# par cinématique inverse depuis le poing qui tient la massue, le coude plié vers l'arrière ; les jambes aussi, pieds au
# sol, genoux vers l'avant). C'est un géant : tout est lent et lourd — longues préparations, coups très courts, impacts
# tenus, retours lents (comme le pixel art). Les poses clés sont reliées par des courbes douces sans dépassement
# (24 images par seconde). Les effets de la terre (poussière ocre, mottes, éclats de roche, fêlure et lueur dorée,
# le gros rocher moussu, traînée de la massue) sont dessinés dans le même style : dégradés, un seul contour, aucun
# flou SVG ; jamais de rayons droits répétés.
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
import aurelle as K  # noqa: E402
from atelier import sm, ribbon, ellipse, rpoly, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'aurelle')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-aurelle/_images'
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


PAIRS = {'G': ('gx', 'gy'), 'head': ('headx', 'heady'), 'nsh': ('nshx', 'nshy'), 'FF': ('ffx', 'ffy'), 'eye': ('eyex', 'eyey')}
SCAL = ['crouch', 'lean', 'tilt', 'pg', 'rn', 'rf', 'lift', 'shift', 'glow', 'ang', 'length', 'front', 'ffa', 'mouth']
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
# G : le milieu du poing proche sur le manche ; ang : la direction du manche vers la tête de la massue (degrés, y vers
# le bas : −90 = vers le haut) ; front : le bras proche passe devant la tête (bras levé, ou ramené devant lui).

# 2) L'attaque de base « Double coup de massue » : il lève la massue encore plus haut et la rejette derrière son dos,
# se cambre et se tasse — longue attente, l'œil s'allume — puis l'abat par-dessus sa tête : premier coup, à hauteur de
# ventre, devant lui (éclat doré, bouffée de poussière). La massue rebondit (elle est lourde, elle remonte toute seule
# au-dessus de lui) et il la rabat aussitôt, plus fort, jusqu'au sol devant ses orteils : deuxième coup, la terre saute
# (fêlure dorée, mottes, cailloux, la poussière qui roule des deux côtés). Arrêt sur l'image, puis il relève lentement
# la massue et revient en garde.
RAISE = dict(G=(21.0, 29.0), ang=-128, lean=-1.0, crouch=0.5, nsh=(0, -1), head=(0, -0.5), eye=(-0.6, -0.4))
WIND = dict(G=(30.0, 22.0), ang=-162, lean=-3.6, crouch=2.0, nsh=(-1, -2), head=(-0.6, 1.0), tilt=-3, glow=0.8,
            eye=(0.8, 0.0), pg=1.0, rn=1.0)
OVER = dict(front=0, G=(49.0, 17.0), ang=-78, lean=-1.0, crouch=1.0, nsh=(2, -2), head=(0, 0), tilt=-1, glow=1.0, pg=0.5)
HIT1 = dict(front=1, G=(90.0, 72.0), ang=-2, lean=3.0, crouch=1.6, nsh=(6, 3), head=(1, 1), tilt=4, glow=1.0, mouth=0.8,
            FF=(113.0, 58.0), ffa=-84, eye=(0.8, 0.4), pg=-1.0)
REB = dict(front=0, G=(52.0, 19.0), ang=-82, lean=0.0, crouch=1.0, nsh=(3, -1), head=(0, 0), tilt=0, glow=0.8, mouth=0.4,
           FF=(115.0, 56.0), pg=0.4)
GROUND = dict(front=1, G=(92.0, 86.0), ang=42, lean=6.0, crouch=3.0, nsh=(7, 2), head=(1.5, 2.0), tilt=6, glow=1.2,
              mouth=1.0, FF=(112.0, 60.0), ffa=-88, eye=(0.6, 0.8), pg=-1.2)
ATTACK = [
    (0, {}),
    (170, dict(RAISE)),
    (330, dict(WIND)),
    (520, dict(WIND, G=(31.0, 21.0), ang=-166, lean=-4.0, crouch=2.3, glow=1.0)),
    (568, dict(OVER)),
    (590, dict(OVER, G=(84.0, 30.0), ang=-24, lean=1.0)),
    (610, dict(HIT1)),
    (720, dict(HIT1, G=(91.0, 73.0), ang=0)),
    (745, dict(HIT1, G=(86.0, 60.0), ang=-24, front=0)),
    (800, dict(REB)),
    (840, dict(REB, G=(86.0, 26.0), ang=-12, lean=3.0, crouch=2.0)),
    (862, dict(GROUND, G=(97.0, 52.0), ang=12, lean=4.0, crouch=2.4)),
    (880, dict(GROUND)),
    (1100, dict(GROUND, G=(92.5, 86.5), crouch=3.2)),
    (1200, dict(front=0.6, G=(62.0, 72.0), ang=-10, lean=3.0, crouch=2.0, nsh=(4, 1), head=(0.5, 1), tilt=2, glow=0.4, mouth=0.2,
                FF=(115.0, 56.0))),
    (1270, dict(front=0, G=(20.0, 60.0), ang=-64, lean=1.2, crouch=1.2, glow=0.2)),
    (1380, dict(front=0, G=(26.0, 44.0), ang=-96, lean=0.4, crouch=0.6, glow=0.1)),
    (1560, {}),
]
ATTACK_HIT = 610
ATTACK_HIT2 = 880

# 3) L'attaque spéciale « Rocher du cyclope » : il lève la massue, l'œil s'embrase (la terre répond), et l'abat sur le
# sol devant lui : une fêlure dorée court sous la terre vers l'avant. Là-bas, le sol se bombe, puis un énorme rocher
# moussu jaillit de terre (mottes, poussière) et monte jusqu'à hauteur de poitrine pendant que le géant ramène la
# massue tout en bas derrière lui, ramassé. Arrêt : le rocher flotte au sommet de sa course. Puis il frappe de bas en
# haut, comme une batte : choc, arrêt sur l'image, le rocher se fend de veines dorées. Le rocher part en cloche en
# tournant sur lui-même et s'écrase sur l'ennemi : il éclate en blocs, la poussière monte en dôme, l'onde dorée court
# au ras du sol. Il repose la massue et revient en garde.
LOWB = dict(front=1, G=(34.0, 86.0), ang=158, lean=-2.0, crouch=2.6, nsh=(-1, 2), head=(0, 1.5), tilt=2, glow=1.6,
            FF=(116.0, 54.0), eye=(1.2, 0.2), pg=1.0)
BAT = dict(front=1, G=(96.0, 73.0), ang=-26, lean=3.0, crouch=1.4, nsh=(6, 3), head=(1.5, 0.5), tilt=-2, glow=2.0,
           mouth=1.0, FF=(112.0, 60.0), ffa=-88, eye=(1.0, -0.4), pg=-1.2)
SPECIAL = [
    (0, {}),
    (200, dict(RAISE, glow=0.8)),
    (380, dict(WIND, glow=1.6)),
    (500, dict(WIND, G=(31.0, 21.0), ang=-166, lean=-4.0, crouch=2.3, glow=2.0)),
    (548, dict(OVER, glow=2.0)),
    (570, dict(OVER, G=(86.0, 28.0), ang=-14, lean=2.0, glow=2.0)),
    (590, dict(GROUND, glow=2.0)),
    (760, dict(GROUND, G=(92.5, 86.5), crouch=3.2, glow=1.8)),
    (1000, dict(LOWB)),
    (1340, dict(LOWB, G=(33.0, 87.0), ang=160, crouch=2.9, lean=-2.4)),
    (1410, dict(BAT, G=(80.0, 80.0), ang=30, lean=3.0)),
    (1452, dict(BAT)),
    (1560, dict(BAT, G=(97.0, 72.0), ang=-29)),
    (1700, dict(front=1, G=(92.0, 57.0), ang=-50, lean=2.0, crouch=1.0, nsh=(4, -1), head=(1, 0), glow=1.2, mouth=0.3,
                FF=(115.0, 56.0), eye=(1.6, 0.0))),
    (2050, dict(front=1, G=(90.0, 58.0), ang=-56, lean=1.6, crouch=1.2, nsh=(4, -1), head=(1, 0.5), glow=1.0, eye=(1.8, 0.4),
                FF=(115.0, 56.0))),
    (2200, dict(front=0.6, G=(62.0, 72.0), ang=-20, lean=2.0, crouch=1.6, nsh=(3, 1), glow=0.4)),
    (2290, dict(front=0, G=(20.0, 60.0), ang=-64, lean=1.0, crouch=1.2, glow=0.2)),
    (2420, dict(front=0, G=(26.0, 44.0), ang=-96, lean=0.4, crouch=0.6, glow=0.1)),
    (2600, {}),
]
SP_SLAM = 590
SP_HIT = 1452
SP_ROCK_X = 140.0            # là où le rocher jaillit
B_TOP = (136.0, 56.0)        # le rocher au sommet de sa course (là où la massue le frappe)
B_R = 9.6
SP_FLY = 560.0               # la durée du vol (ms)
SP_IMPACT = SP_HIT + 80 + SP_FLY
IMP_X = 214.0                # là où il s'écrase (l'ennemi)


# ======================================================================== la respiration (en boucle, 2,4 s)

def eye_roll(T):
    """L'œil unique roule (cycle de 4,8 s) : il regarde en arrière, revient, remonte, puis cligne."""
    keys = [(0.0, 0.0, 0.0), (0.6, 0.0, 0.0), (1.0, -1.8, 0.1), (1.7, -1.8, 0.1), (2.1, 0.0, -0.9), (2.8, 0.2, -0.9),
            (3.2, 0.0, 0.0), (4.8, 0.0, 0.0)]
    t = T % 4.8
    ts = [k[0] for k in keys]
    return monotone(ts, [k[1] for k in keys], t), monotone(ts, [k[2] for k in keys], t)


def idle_offsets(T):
    """Il inspire (le buste monte d'un souffle), les épaules roulent l'une après l'autre (la proche, qui porte la
    massue, puis la lointaine), la tête suit en retard ; la massue levée oscille (sa tête traîne derrière le poing) ;
    à l'expiration il se tasse sur ses jambes, lourd ; le pagne se balance."""
    u = 2 * math.pi * T / 2.4
    br = 0.5 - 0.5 * math.cos(u)
    ex, ey = eye_roll(T)
    return dict(breath=br, crouch=0.7 * (0.5 - 0.5 * math.cos(u - 2.6)), heady=0.5 * math.sin(u - 0.7),
                tilt=-0.8 * math.sin(u - 0.9), rn=0.9 * (0.5 - 0.5 * math.cos(u - 0.4)), rf=0.8 * (0.5 - 0.5 * math.cos(u - 1.3)),
                pg=0.6 * math.sin(u + 0.4), gx=0.5 * math.sin(u - 0.5), gy=-0.9 * (0.5 - 0.5 * math.cos(u - 0.4)),
                ang=1.8 * math.sin(u - 1.4), eyex=ex, eyey=ey, ffy=-0.6 * (0.5 - 0.5 * math.cos(u - 1.3)))


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
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or keyed([(0, {})], 0)
    P = {}
    for n in SCAL:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['G'] = (src['gx'] + w * idl['gx'], src['gy'] + w * idl['gy'])
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['nsh'] = (src['nshx'], src['nshy'])
    P['FF'] = (src['ffx'], src['ffy'] + w * idl['ffy'])
    P['eye'] = (src['eyex'] + w * idl['eyex'], src['eyey'] + w * idl['eyey'])
    P['breath'] = w * idl['breath']
    P['bn'] = -1.0
    # le clignement (au repos, à la fin du roulement de l'œil)
    tb = (T % 4.8) - 3.55
    P['blink'] = (max(0.0, 1 - abs(tb) / 0.08) if w > 0.95 else 0.0)
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


# ---- la traînée de la massue : un croissant de bois clair qui s'efface vers l'arrière, bordé de poussière dorée

def club_trail(fig, C, R, a0, a1, w, op=1.0):
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    if a1 < a0:
        a0, a1 = a1, a0
        pa, pb = pb, pa
        body = arc_band(C, R - 0.5, a1, a0, w)
        rim = arc_band(C, R + 1.0, a1, a0, w * 0.3)
    else:
        body = arc_band(C, R - 0.5, a0, a1, w)
        rim = arc_band(C, R + 1.0, a0, a1, w * 0.3)
    g1 = g_lin(fig, pa, pb, [(0, '#e8c896', 0), (1, '#fff2d4', 0.8 * op)])
    g2 = g_lin(fig, pa, pb, [(0, E[2], 0), (0.6, E[1], 0.8 * op), (1, E[0], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


SHOULDER = (48.0, 58.0)


def swing(fig, ctx, sweep, w, op):
    """La traînée qui suit la tête de la massue (autour de l'épaule), sur `sweep` degrés derrière elle."""
    ch = ctx['club_head']
    C = SHOULDER
    R = math.dist(C, ch)
    a = math.degrees(math.atan2(ch[1] - C[1], ch[0] - C[0]))
    fig.fx_back.append(club_trail(fig, C, R + 5, a - sweep, a, w, op=op))
    fig.fx_back.append(club_trail(fig, C, R - 7, a - sweep * 0.8, a, w * 0.35, op=0.8 * op))


def ground_hit(fig, cx, tau, big=1.0, seed=0):
    """Le coup au sol : éclair doré, le sol se fend, deux dalles, mottes et éclats en éventail, poussière qui roule."""
    fl = env(tau, -0.01, 0.0, 0.05, 0.16)
    if fl > 0:
        fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(cx), fm(GR - 4), fm(70 * big), g_rad(
            fig, (cx, GR - 4), 70 * big, [(0, '#fffef0', 0.8 * fl), (0.15, E[0], 0.45 * fl), (0.5, E[1], 0.12 * fl), (1, E[2], 0)])))
    e = env(tau, 0, 0.03, 0.14, 0.34)
    if e > 0:
        fig.fx_front.append(pop(fig, (cx + 2, GR - 4), 7.0 * big * (0.6 + 0.4 * e), facing=-60, op=e))
    co = env(tau, 0, 0.04, 0.3, 0.7)
    fig.fx_back.extend(crack(fig, cx, (14 + 8 * min(1, tau * 6)) * big, 2, seed=3 + seed, op=co))
    so = env(tau, 0, 0.05, 0.3, 0.55)
    k = min(1.0, tau / 0.08)
    fig.fx_back.append(slab(fig, cx - 10, 6 * k * big, 6, lean=-1.6, seed=5 + seed, op=so))
    fig.fx_front.append(slab(fig, cx + 11, 8 * k * big, 7, lean=2.2, seed=6 + seed, op=so))
    for i, (vx, vy, r) in enumerate(((40, -70, 1.8), (64, -48, 1.4), (22, -84, 1.2), (80, -30, 1.1), (-30, -64, 1.3),
                                     (-50, -40, 0.9), (52, -88, 0.8), (96, -50, 0.8), (8, -96, 0.7), (-16, -80, 0.7))):
        if tau < 0.85:
            x, y = ballistic((cx, GR - 3), (vx * big, vy * big), 190, tau)
            if y < GR - 0.6:
                fig.fx_front.append(rock(fig, (x, y), r * big, seed=i + 11 + seed, rot=tau * 500 + i * 40, op=min(1, 2.4 * (0.85 - tau))))
    if 0.04 < tau < 1.0:
        k = (tau - 0.04) / 0.96
        o = env(k, 0, 0.12, 0.5, 1)
        for side, b2 in ((-1, 1.0), (1, 0.9)):
            fig.fx_back.append(puff(fig, cx + side * (6 + 18 * k), GR - 3.5 - 3 * k, (3 + 3.6 * k) * b2 * big, op=0.9 * o))
            fig.fx_front.append(puff(fig, cx + side * (3 + 10 * k), GR - 2.0, (2 + 2.2 * k) * b2 * big, op=0.85 * o))
        fig.fx_back.append(curl(fig, (cx + 14 + 10 * k, GR - 10 - 8 * k), 3.4 + 1.6 * k, 200 + 90 * k, 280, 2.2, op=0.8 * o, kind='dust'))


def flash(fig, c, R, fl):
    if fl > 0:
        fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(R), g_rad(
            fig, c, R, [(0, '#fffef0', 0.85 * fl), (0.15, E[0], 0.5 * fl), (0.5, E[1], 0.14 * fl), (1, E[2], 0)])))


# ---- l'attaque de base

HIT_AT = {}


def fx_attack(tl):
    def f(fig, ctx):
        # la massue passe par-dessus sa tête (premier coup), puis se rabat jusqu'au sol (deuxième coup)
        if 530 <= tl <= 700:
            e = env(tl, 530, 570, 615, 700)
            swing(fig, ctx, 95, 14 * e + 2, e)
        if 820 <= tl <= 960:
            e = env(tl, 820, 850, 885, 960)
            swing(fig, ctx, 80, 16 * e + 2, e)
        # premier coup, à hauteur de ventre devant lui : un éclat doré, une bouffée de poussière
        tau = (tl - ATTACK_HIT) / 1000.0
        c = HIT_AT.get('h1')
        if c and -0.01 <= tau < 0.5:
            hp = (c[0] + 9, c[1])
            flash(fig, hp, 34, env(tau, -0.01, 0.0, 0.04, 0.14))
            e = env(tau, 0, 0.02, 0.1, 0.26)
            if e > 0:
                fig.fx_front.append(pop(fig, hp, 6.0 * (0.6 + 0.4 * e), facing=0, op=e))
            for i, (vx, vy) in enumerate(((50, -40), (60, 10), (36, -64), (70, -14))):
                if tau < 0.4:
                    x, y = ballistic(hp, (vx, vy), 160, tau)
                    fig.fx_front.append(rock(fig, (x, y), 0.8, seed=40 + i, rot=tau * 600, op=min(1, 3 * (0.4 - tau))))
            if 0.02 < tau < 0.5:
                k = (tau - 0.02) / 0.48
                fig.fx_back.append(puff(fig, hp[0] + 4 + 8 * k, hp[1] - 2 - 4 * k, 2.4 + 2.6 * k, op=0.8 * env(k, 0, 0.15, 0.5, 1)))
        # deuxième coup, au sol devant ses orteils : la terre saute
        tau = (tl - ATTACK_HIT2) / 1000.0
        c = HIT_AT.get('h2')
        if c and tau >= -0.01:
            ground_hit(fig, c[0], tau, big=1.0)
        # il relève la massue : quelques gravillons
        if 1100 < tl < 1350 and c:
            tt = (tl - 1100) / 1000.0
            for i, (vx, vy) in enumerate(((-20, -40), (16, -46), (-6, -54))):
                x, y = ballistic((c[0], GR - 2), (vx, vy), 160, tt)
                if y < GR - 0.5:
                    fig.fx_front.append(rock(fig, (x, y), 0.7, seed=30 + i, rot=tt * 600, op=1 - tt / 0.25))
    return f


# ---- l'attaque spéciale : le gros rocher moussu

BOULDER = [(-1.0, -0.86), (-0.42, -1.0), (0.3, -0.98), (0.88, -0.62), (1.02, 0.08), (0.8, 0.72), (0.18, 1.0),
           (-0.6, 0.9), (-1.02, 0.3)]                               # le contour du rocher (unités du rayon), repris du pixel art
B_VEINS = [[(-0.15, -0.55), (0.05, -0.1), (-0.2, 0.25), (-0.05, 0.6)], [(0.05, -0.1), (0.5, 0.1), (0.6, 0.45)],
           [(-0.2, 0.25), (-0.62, 0.35)]]


def _rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def boulder(fig, c, r, spin=0.0, veins=0, op=1.0, squash=1.0):
    """Le gros rocher : un bloc à facettes éclairé en haut à droite (quel que soit l'angle), sa calotte de mousse (elle
    tourne avec lui), ses fêlures : 0 sombres, 1 ambre, 2 dorées (la terre s'y allume), 3 blanc doré (le choc)."""
    if op <= 0.02:
        return ''
    P_ = lambda q: (c[0] + q[0] * r, c[1] + q[1] * r * squash)
    pts = [P_(_rot(p, spin)) for p in BOULDER]
    body = rpoly(pts, r * 0.22)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, E[3]), (0.5, E[4]), (1, E[5])])
    # les facettes : la face éclairée (haut-droit), la face d'ombre (bas-gauche)
    face = rpoly([P_((0.05, -0.1)), P_((0.25, -0.92)), P_((0.86, -0.56)), P_((0.92, 0.1))], r * 0.12)
    shade = rpoly([P_((0.0, 0.05)), P_((0.7, 0.66)), P_((0.12, 0.96)), P_((-0.62, 0.86)), P_((-0.98, 0.28))], r * 0.12)
    # la mousse : la calotte du dessus du rocher (dans son repère), bord bas en lobes inégaux
    mo_local = [(-1.0, -0.86), (-0.42, -1.0), (0.3, -0.98), (0.84, -0.6), (0.7, -0.38), (0.42, -0.5), (0.16, -0.3),
                (-0.18, -0.46), (-0.5, -0.32), (-0.8, -0.5), (-0.98, -0.4)]
    moss = rpoly([P_(_rot(p, spin)) for p in mo_local], r * 0.1)
    mc = P_(_rot((-0.05, -0.72), spin))
    gm = g_lin(fig, (mc[0] + r * 0.6, mc[1] - r * 0.4), (mc[0] - r * 0.6, mc[1] + r * 0.4), [(0, K.MOSS.light), (0.6, K.MOSS.base), (1, K.MOSS.shadow)])
    items = [(body, gr, 1), (face, E[3], 0.75), (shade, E[5], 0.55), (moss, gm, 1),
             (ellipse(*P_(_rot((0.2, -0.82), spin)), r * 0.16, r * 0.07), K.MOSS.hi, 0.8)]
    vc = [E[6], E[2], E[1], '#fffbe4'][max(0, min(3, veins))]
    for v in B_VEINS:
        pv = [P_(_rot(p, spin)) for p in v]
        wv = 0.5 + 0.25 * veins
        if veins >= 1:
            items.append((ribbon(pv, [0.2] + [wv * 2.4] * (len(pv) - 2) + [0.2]), E[1], 0.25 + 0.1 * veins))
        items.append((ribbon(pv, [0.1] + [wv] * (len(pv) - 2) + [0.1]), vc, 1))
    return outlined([(sh, fl, o) for sh, fl, o in items[:1]] + items[1:], w=1.5, op=op)


def running_crack(fig, x0, x1, op=1.0, level=2):
    """La fêlure dorée qui court au ras du sol, de x0 à x1 (un zigzag doux, une lueur)."""
    if x1 - x0 < 2 or op <= 0.02:
        return []
    n = max(3, int((x1 - x0) / 5))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.3 + (0.9 * hsh(7, i) - 0.45) * (1 if 0 < i < n else 0)) for i in range(n + 1)]
    gl = g_lin(fig, (x0, GR), (x1, GR), [(0, E[2], 0), (0.7, E[1], 0.45 * op), (1, E[0], 0.7 * op)])
    halo = ribbon(pts, [0.4] + [3.4] * (n - 1) + [1.2])
    core = ribbon(pts, [0.2] + [1.3] * (n - 1) + [0.4])
    hot = ribbon(pts, [0.1] + [0.5] * (n - 1) + [0.2])
    return ['<path d="%s" fill="%s"/>' % (halo.d(), gl),
            '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (op, core.d(), E[6], hot.d(), E[1] if level < 2 else E[0])]


GCLIP = {}


def ground_clip(fig):
    """Un découpage « au-dessus du sol » (pour le rocher qui sort de terre)."""
    cid = 'gclip'
    fig.defs.append('<clipPath id="%s"><rect x="-200" y="-300" width="800" height="%s"/></clipPath>' % (cid, fm(GR + 300.4)))
    return cid


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        if 510 <= t <= 660:
            e = env(t, 510, 550, 595, 660)
            swing(fig, ctx, 95, 16 * e + 2, e)
        if 1370 <= t <= 1540:
            e = env(t, 1370, 1410, 1460, 1540)
            swing(fig, ctx, 110, 16 * e + 2, e)
        # le coup au sol (plus petit que l'attaque : la force part dans la terre)
        c = HIT_AT.get('s1')
        tau = (t - SP_SLAM) / 1000.0
        if c and tau >= -0.01:
            ground_hit(fig, c[0], tau, big=0.75, seed=20)
            # la fêlure dorée qui court sous la terre vers l'avant, jusqu'au rocher
            k = min(1.0, max(0.0, (t - SP_SLAM) / 180.0))
            k = k * k * (3 - 2 * k)
            o = env(t, SP_SLAM, SP_SLAM + 20, 1150, 1500)
            fig.fx_back.extend(running_crack(fig, c[0] + 4, c[0] + 4 + (SP_ROCK_X - c[0] - 4) * k, op=o))
        x = SP_ROCK_X
        # le sol se bombe là-bas (une motte qui gonfle, fendue d'or)
        b = env(t, 720, 820, 860, 900)
        if b > 0:
            h = 6 * b
            mound = sm([(x - 12, GR + 0.6), (x - 8, GR - h * 0.7), (x - 2, GR - h), (x + 5, GR - h * 0.85), (x + 11, GR + 0.6)], sharp=(0, 4))
            gmd = g_lin(fig, (x + 8, GR - h), (x - 8, GR), [(0, E[3]), (0.6, E[4]), (1, E[5])])
            fig.fx_back.append(outlined([(mound, gmd, 1), (ribbon([(x - 3, GR - h * 0.9), (x - 1, GR - h * 0.5), (x - 2.4, GR)], [0.1, 0.9, 0.1]), E[1], 1)], w=1.3))
            fig.fx_back.extend(crack(fig, x, 10 + 4 * b, 2, seed=9, op=b))
        # le rocher jaillit (sort de terre, mottes et poussière), monte jusqu'à hauteur de poitrine, flotte
        if 860 <= t < SP_HIT + 80:
            u = min(1.0, (t - 860) / 300.0)
            u = 1 - (1 - u) ** 3
            cy = (GR + B_R) + (B_TOP[1] - GR - B_R) * u + 0.8 * math.sin((t - 860) / 90.0) * (1 if u >= 1 else u)
            cx_ = x + (B_TOP[0] - x) * u
            veins = 0 if t < SP_HIT else 3
            cid = ground_clip(fig)
            fig.fx_front.append('<g clip-path="url(#%s)">%s</g>' % (cid, boulder(fig, (cx_, cy), B_R, spin=-8 + 8 * u, veins=veins)))
            tt = (t - 860) / 1000.0
            for i, (vx, vy, r) in enumerate(((-40, -70, 1.6), (30, -80, 1.8), (55, -50, 1.3), (-60, -40, 1.2), (10, -100, 1.0), (-20, -90, 1.1))):
                if tt < 0.8:
                    px, py = ballistic((x, GR - 2), (vx, vy), 190, tt)
                    if py < GR - 0.5:
                        fig.fx_front.append(rock(fig, (px, py), r, seed=70 + i, rot=tt * 500, op=min(1, 2.5 * (0.8 - tt))))
            if tt < 0.9:
                k = tt / 0.9
                o = env(k, 0, 0.1, 0.5, 1)
                for side in (-1, 1):
                    fig.fx_back.append(puff(fig, x + side * (8 + 12 * k), GR - 3 - 3 * k, 3 + 3 * k, op=0.9 * o))
                    fig.fx_front.append(puff(fig, x + side * (5 + 8 * k), GR - 1.8, 2 + 1.8 * k, op=0.85 * o))
            # la lueur dorée sous le rocher qui flotte (la terre le tient)
            g = env(t, 980, 1100, SP_HIT, SP_HIT + 60)
            if g > 0:
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(GR), fm(16), fm(3.2), g_rad(
                    fig, (x, GR), 16, [(0, E[1], 0.6 * g), (1, E[2], 0)])))
        # le choc de la massue contre le rocher : éclair, éclats, arrêt sur l'image
        tau = (t - SP_HIT) / 1000.0
        if -0.01 <= tau < 0.4:
            hp = (B_TOP[0] - B_R * 0.8, B_TOP[1])
            flash(fig, hp, 40, env(tau, -0.01, 0.0, 0.05, 0.16))
            e = env(tau, 0, 0.02, 0.08, 0.24)
            if e > 0:
                fig.fx_front.append(pop(fig, hp, 6.5 * (0.6 + 0.4 * e), facing=-20, op=e))
        # le vol en cloche, en tournant sur lui-même, de petites volutes de poussière derrière lui
        t_f = t - (SP_HIT + 80)
        if 0 <= t_f < SP_FLY:
            u = t_f / SP_FLY
            p0, p1 = B_TOP, (IMP_X, GR - B_R * 0.9)
            bx = p0[0] + (p1[0] - p0[0]) * u
            by = p0[1] + (p1[1] - p0[1]) * u - 46 * 4 * u * (1 - u)
            for j in range(3):
                uu = u - 0.07 * (j + 1)
                if uu > 0:
                    qx = p0[0] + (p1[0] - p0[0]) * uu
                    qy = p0[1] + (p1[1] - p0[1]) * uu - 46 * 4 * uu * (1 - uu)
                    fig.fx_back.append(puff(fig, qx, qy + 2, 2.6 - 0.6 * j, op=0.7 - 0.2 * j))
            fig.fx_front.append(boulder(fig, (bx, by), B_R, spin=420 * u, veins=2))
        # l'impact sur l'ennemi : il éclate en blocs, la poussière monte en dôme, l'onde dorée court au ras du sol
        cx = IMP_X
        tg = t - SP_IMPACT
        if tg >= -6:
            fl = env(tg, -6, 0, 40, 170)
            flash(fig, (cx, GR - 14), 120, fl)
            if tg >= 0:
                tau = tg / 1000.0
                e = env(tau, 0, 0.03, 0.16, 0.36)
                if e > 0:
                    fig.fx_front.append(pop(fig, (cx - 2, GR - 12), 10 * (0.6 + 0.4 * e), facing=-90, op=e))
                co = env(tau, 0, 0.05, 0.5, 0.9)
                fig.fx_back.extend(crack(fig, cx, 26 + 10 * min(1, tau * 5), 2, seed=7, op=co))
                # l'onde dorée au ras du sol, qui s'éloigne des deux côtés
                w_ = env(tau, 0, 0.04, 0.25, 0.5)
                if w_ > 0:
                    R = 12 + 70 * min(1.0, tau / 0.5)
                    fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%g"/>' % (
                        fm(cx), fm(GR), fm(R), fm(R * 0.09), E[1], fm(2.2 * w_ + 0.3), 0.8 * w_))
                # les blocs du rocher qui volent et retombent en roulant
                for i, (vx, vy, r) in enumerate(((-40, -90, 3.2), (34, -104, 3.6), (66, -70, 2.6), (-70, -60, 2.4),
                                                 (92, -40, 2.0), (-14, -120, 2.0), (48, -126, 1.6), (-96, -36, 1.6))):
                    if tau < 1.4:
                        px, py = ballistic((cx, GR - 10), (vx, vy), 230, tau)
                        py = min(py, GR - r * 0.7)
                        if tau < 1.4:
                            fig.fx_front.append(rock(fig, (px, py), r, seed=60 + i, rot=tau * 360 + i * 30, op=min(1, 2.4 * (1.4 - tau))))
                # deux mottes de mousse
                for i, (vx, vy) in enumerate(((-24, -110), (40, -96))):
                    if tau < 0.9:
                        px, py = ballistic((cx, GR - 12), (vx, vy), 230, tau)
                        if py < GR - 1:
                            fig.fx_front.append(outlined([(ellipse(px, py, 2.2, 1.4, tau * 300), K.MOSS.base, 1),
                                                          (ellipse(px + 0.5, py - 0.4, 1.1, 0.5, tau * 300), K.MOSS.light, 1)],
                                                         ink='#1e3226', w=1.1, op=min(1, 2.5 * (0.9 - tau))))
                # la couronne de dalles
                rise = min(1.0, tau / 0.09)
                so = env(tau, 0, 0.04, 0.42, 0.75)
                sink = max(0.0, (tau - 0.42) / 0.33)
                for i, (dx, h, w2, ln, front) in enumerate(((-22, 10, 8, -3.4, False), (-11, 15, 9, -2.0, False), (2, 18, 10, 0.4, False),
                                                            (14, 14, 9, 2.4, False), (24, 10, 8, 3.6, False),
                                                            (-17, 9, 8, -3.0, True), (18, 10, 8, 3.2, True))):
                    hh = h * rise * (1 - 0.7 * sink)
                    (fig.fx_front if front else fig.fx_back).append(slab(fig, cx + dx, hh, w2, lean=ln, seed=40 + i, op=so))
                # la poussière qui monte en dôme et roule
                if 0.05 < tau < 1.5:
                    k = (tau - 0.05) / 1.45
                    o = env(k, 0, 0.1, 0.5, 1)
                    for dx, dy, r in ((-22, -4, 5), (22, -5, 5.5), (0, -14, 6.5), (-10, -26, 4.5), (12, -30, 4.0)):
                        fig.fx_back.append(puff(fig, cx + dx * (1 + 0.8 * k), GR + dy - 8 * k, r * (0.7 + 0.8 * k), op=0.85 * o))
                    fig.fx_back.append(curl(fig, (cx + 30 + 8 * k, GR - 30 - 10 * k), 4 + 2 * k, 200 + 90 * k, 280, 2.6, op=0.8 * o, kind='dust'))
                    fig.fx_back.append(curl(fig, (cx - 30 - 8 * k, GR - 26 - 10 * k), 3.6 + 2 * k, 340 - 90 * k, -280, 2.4, op=0.7 * o, kind='dust'))
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
        if 'h1' not in HIT_AT:
            HIT_AT['h1'] = K.build(pose=pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)[0]).ctx['club_head']
            HIT_AT['h2'] = K.build(pose=pose_at(t0 + ATTACK_HIT2 / 1000.0, act, t0)[0]).ctx['club_head']
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 's1' not in HIT_AT:
            HIT_AT['s1'] = K.build(pose=pose_at(t0 + SP_SLAM / 1000.0, act, t0)[0]).ctx['club_head']
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
