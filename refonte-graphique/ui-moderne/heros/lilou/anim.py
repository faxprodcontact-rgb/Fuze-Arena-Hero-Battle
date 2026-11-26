# Lilou vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/lilou/build.py) —
# la garde du boxeur qui sautille, l'attaque de base « Une-deux », l'attaque spéciale « Toupie de la marée » — dans le
# style lisse de l'interface (comme Kael : heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/lilou/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/lilou/)
#   python3 refonte-graphique/ui-moderne/heros/lilou/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#
# Méthode : chaque image redessine lilou.py dans une POSE (petit bond du boxeur, genoux qui plient, pieds à plat ; buste
# qui respire et se penche depuis les hanches ; carapace qui suit avec retard ; tête ; pans du bandeau qui flottent ;
# les deux bras suivent leur poignet par cinématique inverse, les gants tournent autour du poignet). Les poses clés
# reprennent celles du pixel art (mêmes temps : ramassée tenue, jab sec, direct avec tout le corps, arrêt sur l'impact,
# retour en sautillant ; pour la spéciale : saut, rentrée dans la carapace, toupie sur la vague jusqu'à l'ennemi,
# sortie d'un bond, uppercut et trombe d'eau, retour en deux bonds), reliées par des courbes douces sans dépassement,
# 24 images/s. Quand elle est rentrée dans sa carapace, la toupie est REDESSINÉE à chaque angle (écailles, rebord,
# trous de la tête et des pattes qui passent en tournant, ses yeux qui guettent, les pans du bandeau qui fouettent).
# Les effets d'eau (gouttes, écume, nappes, traînées, vague, anneau, trombe) sont ceux des héros d'eau vectoriels
# (mêmes formes et couleurs que Kesha) : dégradés, un seul contour, aucun flou.
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import lilou as K  # noqa: E402
from atelier import Figure, Mat, lock, sm, ribbon, ellipse, sides, f as fm, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import crpath, taper  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'lilou')
TMP = os.environ.get('LILOU_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-24, -48, 304, 171)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WINK = '#0c1846'                     # le contour de l'eau (bleu nuit presque noir, comme Kesha et Ilian)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']
SPOUT_X = 250.0                      # où jaillit la trombe (sous l'ennemi)


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


PAIRS = {'head': ('headx', 'heady'), 'nw': ('nwx', 'nwy'), 'fw': ('fwx', 'fwy'), 'sh': ('shx', 'shy'), 'shell': ('slx', 'sly')}
SCAL = ['crouch', 'lean', 'tilt', 'pan', 'shift', 'lift', 'nga', 'fga', 'fabs', 'tail', 'tuck', 'fstretch', 'nstretch', 'inhale']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        elif key in d:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# Les poignets du pixel art (grille du dessin) → décalage depuis le repos.
def fwp(x, y):
    return (x - K.FW0[0], y - K.FW0[1])


def nwp(x, y):
    return (x - K.NW0[0], y - K.NW0[1])


# 2) « Une-deux » (pixel : ATTAQUE). Elle se ramasse derrière sa garde (tenu), puis enchaîne : un JAB sec du poing
# lointain (le bras se détend, une traînée d'eau suit le gant, des gouttes giclent à l'impact) et aussitôt le DIRECT
# du poing proche, tout le corps derrière (elle pivote et glisse vers l'ennemi, la carapace suit) : le gant arrive dans
# une traînée d'eau courbe et frappe (arrêt sur l'image) dans une gerbe d'eau aux jets inégaux. Elle ramène le poing
# et revient en sautillant dans sa garde ; les gouttes retombent.
GATHER = dict(crouch=2.2, lean=-2.3, head=(-1.1, 1.1), tilt=-2.2, nw=(-1.6, 1.1), fw=(-2.8, 1.6), pan=1.1, shell=(0.9, 0))
ATTACK = [
    (0, {}),
    (90, dict(crouch=0.6, lean=-0.6, head=(-0.3, 0.3), pan=0.4)),
    (230, dict(GATHER, crouch=2.0, lean=-2.0)),
    (300, GATHER),
    (335, dict(shift=6, crouch=1.0, lean=2, head=(1, 0), tilt=1, fw=fwp(114.0, 58.6), fga=26, fstretch=1, nw=(0, -1), pan=-1, shell=(-0.8, 0))),
    (355, dict(shift=8, crouch=1.0, lean=2.2, head=(1, 0), tilt=1, fw=fwp(116.4, 58.0), fga=30, fstretch=1.6, nw=(0, -1), pan=-1.8, shell=(-1.4, 0))),
    (440, dict(shift=9, crouch=1.0, lean=2.4, head=(1, 0), fw=fwp(113.0, 58.8), fga=24, fstretch=1.2, nw=(0.4, -0.8), pan=-2, shell=(-1.2, 0))),
    (485, dict(shift=13, crouch=0.9, lean=3, head=(1.2, 0), fw=fwp(99.0, 59.0), fabs=0.6, fga=0, nw=nwp(68.0, 67.0), sh=(3, 1), nga=-4,
               pan=-2, shell=(-0.4, 0))),
    (520, dict(shift=27, crouch=0.6, lean=5, head=(2, 0), tilt=2, fw=fwp(97.0, 58.0), fabs=1, fga=-8, nw=nwp(90.0, 70.0), sh=(8, 2), nga=-6,
               nstretch=1, pan=-3, shell=(-3, 0))),
    (545, dict(shift=30, crouch=0.6, lean=5.6, head=(2, 0), tilt=2.4, fw=fwp(97.0, 58.0), fabs=1, fga=-8, nw=nwp(95.0, 71.0), sh=(9, 2),
               nga=-6, nstretch=1.6, pan=-2.6, shell=(-3.6, 0))),
    (700, dict(shift=30.4, crouch=0.8, lean=5.4, head=(2, 0.2), tilt=2.2, fw=fwp(97.2, 58.4), fabs=1, fga=-8, nw=nwp(94.4, 71.0), sh=(9, 2),
               nga=-6, nstretch=1.2, pan=-2, shell=(-1, 0))),
    (790, dict(shift=23, crouch=1.0, lean=3, head=(1, 1), fw=fwp(99.0, 61.0), fabs=0.5, fga=-4, nw=nwp(74.0, 68.0), sh=(4, 1), nga=-3,
               pan=-1, shell=(1.2, 0))),
    (880, dict(shift=8, lift=2.2, crouch=-0.6, head=(0, 1), fw=(1, 0), pan=1, shell=(0.6, 0.8))),
    (990, dict(crouch=0.9, head=(0, 0.6), pan=1, shell=(0, -0.4))),
    (1110, {}),
]
JAB_HIT = 355
CROSS_HIT = 545

# 3) « Toupie de la marée » (pixel : SPECIALE). Elle se ramasse derrière sa garde (tenu), saute en rentrant la tête et
# RENTRE dans sa carapace : la carapace retombe à plat sur une vague qui se lève et se met à tourner comme une toupie
# (les pans du bandeau fouettent l'air, les yeux guettent par le trou de la tête). La toupie file sur la vague
# jusqu'à l'ennemi : un anneau d'eau tourbillonne autour d'elle, la crête de la vague roule devant, un sillage
# d'écume reste derrière. Arrivée sous l'ennemi, la vague se brise ; elle JAILLIT de sa carapace, accroupie, le poing
# lointain armé bas (tenu), et place un uppercut énorme : une trombe d'eau en spirale jaillit et monte (arrêt sur
# l'image au sommet) ; la trombe s'effondre en pluie, elle retombe et revient en deux bonds.
XT = 136.0                            # où elle jaillit de sa carapace (glissade)
TUCK_END = 330                        # elle disparaît dans sa carapace
POP = 840                             # elle en ressort
SPECIAL = [
    (0, {}),
    (100, dict(crouch=0.5, pan=0.3)),
    (230, dict(crouch=3.0, lean=1.0, head=(1, 2), tilt=2, nw=(-3, 2), fw=(2, -2), pan=1, shell=(0.6, 0))),
    (270, dict(crouch=3.2, lean=1.0, head=(1, 2.2), tilt=2, nw=(-3.2, 2.2), fw=(2, -2), pan=1.1, shell=(0.6, 0))),
    (310, dict(shift=2, lift=9, crouch=-1, lean=0, head=(0, 4), tuck=0.6, nw=(-3, 3), fw=(1, 2), pan=-2, shell=(0, 1))),
    (TUCK_END, dict(shift=3, lift=12, crouch=-1, head=(0, 5), tuck=1.0, nw=(-3, 3), fw=(1, 2), pan=-2, shell=(0, 1))),
    # (dans la carapace : la toupie, plus bas)
    (POP - 10, dict(shift=XT, lift=3, crouch=4.4, lean=1, head=(1, 3), tuck=0.6, fw=fwp(98.0, 84.0), fabs=1, fga=-6, nw=(1, -1),
                    pan=1.6, shell=(0, 1))),
    (POP, dict(shift=XT, crouch=4.2, lean=1, head=(1, 2), tuck=0.2, fw=fwp(98.0, 84.0), fabs=1, fga=-6, nw=(1, -1), pan=1, shell=(0, 0.6))),
    (990, dict(shift=XT, crouch=4.0, lean=1.2, head=(1, 2), fw=fwp(97.6, 85.0), fabs=1, fga=-6, nw=(1, -1), pan=1, shell=(0, 0.4))),
    (1020, dict(shift=XT + 2, lift=6, crouch=-2, lean=1, head=(1, -1), fw=fwp(106.0, 66.0), fabs=0.5, fga=-2, nw=(1, -1), pan=-1, shell=(0, 1.4))),
    (1050, dict(shift=XT + 3, lift=22, crouch=-3, lean=-1, head=(0, -1), tilt=-3, fw=fwp(111.0, 33.0), fstretch=1.5, nw=(1, -2), pan=-2.4,
                shell=(0, 2.4))),
    (1240, dict(shift=XT + 3, lift=22.6, crouch=-3, lean=-1.2, head=(0, -1), tilt=-3.4, fw=fwp(111.0, 32.0), fstretch=1.5, nw=(1, -2),
                pan=-2, shell=(0, 1.4))),
    (1290, dict(shift=XT + 2, lift=14, crouch=-1, lean=0, head=(0, 0), fw=fwp(110.0, 37.0), fstretch=1, nw=(1, -1), pan=0.6, shell=(0, -1))),
    (1370, dict(shift=XT, crouch=3.2, head=(0, 2), fw=fwp(103.0, 66.0), nw=(0, 1), pan=1.4, shell=(0, -1.2))),
    (1420, dict(shift=XT - 21, lift=11, crouch=-1, head=(0, 1), pan=2, shell=(0.6, 1))),
    (1470, dict(shift=XT - 48, crouch=2.6, head=(0, 2), pan=1, shell=(0, -1))),
    (1530, dict(shift=XT - 84, lift=10, crouch=-1, head=(0, 1), pan=2, shell=(0.6, 1))),
    (1590, dict(shift=0, crouch=3.0, head=(0, 2), nw=(0, 1), pan=1, shell=(0, -1))),
    (1710, dict(crouch=1.0, head=(0, 0.6), pan=0.6)),
    (1810, dict(crouch=0.3)),
    (1940, {}),
]
SP_UPPER = 1050
# la toupie : (temps ms, x de son milieu, hauteur au-dessus de la vague, tour (degrés), penchée, écrasée)
TOP_KEYS = [(TUCK_END, 62.0, 22.0, -10.0, 0.0, -0.06),
            (380, 66.0, 10.0, 10.0, 0.0, -0.03),
            (410, 70.0, 0.0, 40.0, 0.0, 0.14),
            (450, 80.0, 0.0, 120.0, 3.0, 0.02),
            (535, 114.0, 0.0, 300.0, 3.0, 0.0),
            (645, 160.0, 0.0, 520.0, 3.0, 0.0),
            (720, 184.0, 0.0, 660.0, 3.0, 0.0),
            (790, 193.0, 0.0, 740.0, 0.0, 0.1),
            (POP - 1, 195.0, 0.0, 770.0, -2.0, 0.04)]


def top_at(tl):
    ts = [k[0] for k in TOP_KEYS]
    return tuple(monotone(ts, [k[i] for k in TOP_KEYS], tl) for i in range(1, 6))


IDLE = 1.21                           # la boucle du repos (s) : deux petits bonds, comme le pixel art (1,21 s)


def idle_offsets(T):
    """La garde du boxeur qui sautille : deux petits bonds par boucle (elle décolle, retombe, plie les genoux), la
    carapace et la tête suivent avec retard, les gants roulent en petits cercles décalés, les pans flottent."""
    u = 2 * math.pi * T / (IDLE / 2)
    v = 2 * math.pi * T / IDLE
    up = max(0.0, math.sin(u)) ** 1.3
    down = max(0.0, -math.sin(u)) ** 1.2
    return dict(lift=0.9 * up, crouch=0.8 * down - 0.2 * up, breath=0.5 - 0.5 * math.cos(v), sly=0.55 * math.sin(u - 1.1),
                slx=0.2 * math.sin(v), heady=0.45 * math.sin(u - 0.8), headx=0.15 * math.sin(v - 0.5), tilt=0.6 * math.sin(v - 1.2),
                nwx=0.7 * math.cos(v), nwy=0.7 * math.sin(v), fwx=0.7 * math.cos(v + 1.9), fwy=0.7 * math.sin(v + 1.9),
                pan=0.7 * math.sin(u - 1.6) + 0.3 * math.sin(v), tail=0.6 * math.sin(u - 1.4))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : sautillement du repos (pondéré) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 150), max(0.0, (tl - (dur - 250)) / 250))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath'] + P.pop('inhale')
    for k, (a, b) in PAIRS.items():
        P[k] = (P.pop(a), P.pop(b))
    P['ph'] = 2 * math.pi * T * 1.6
    P['blink'] = 1.0 if (w > 0.95 and 2.0 <= (T % 3.6) < 2.09) else 0.0
    return P, tl


# ======================================================================== les effets d'eau (un seul contour, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ;
    une 4e valeur dans un élément = pas de silhouette pour lui (un reflet peint dedans)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, 2 * op)), sil, col)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte d'eau : ronde devant, effilée derrière (dans le sens de sa course), éclairée en haut à droite."""
    if op <= 0.02 or r < 0.2:
        return ''
    a = math.atan2(vy, vx) if (vx or vy) else math.pi / 2
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, WATER[1]), (0.45, WATER[2]), (1, WATER[3])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.38, r * 0.26), '#ffffff', 0.95, 'n')], w=1.0, op=op)


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
    return '<g opacity="%g">%s%s%s</g>' % (max(0, min(1, 2 * op)), sil, col, hi)


def sheet(fig, base, ang, length, bend, w, op=1.0, tail=0.0):
    """Une nappe d'eau qui jaillit : un ruban courbe, large à la base, fin et clair au bout, qui se casse en goutte."""
    if length < 1 or op <= 0.02:
        return ''
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    b = bend / 60.0
    p0 = (base[0] + d[0] * length * tail, base[1] + d[1] * length * tail)
    p1 = (base[0] + d[0] * length * 0.35 + nrm[0] * length * b * 0.3, base[1] + d[1] * length * 0.35 + nrm[1] * length * b * 0.3)
    p2 = (base[0] + d[0] * length * 0.7 + nrm[0] * length * b * 0.55, base[1] + d[1] * length * 0.7 + nrm[1] * length * b * 0.55)
    p3 = (base[0] + d[0] * length + nrm[0] * length * b, base[1] + d[1] * length + nrm[1] * length * b)
    sh = lock(p0, p1, p2, p3, w * (1 - tail * 0.6), n=12, bulge=0.35, tipw=w * 0.22)
    core = lock(p0, p1, p2, ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2), w * 0.42 * (1 - tail * 0.6), n=10, bulge=0.1)
    gr = g_lin(fig, p0, p3, [(0, WATER[4]), (0.4, WATER[3]), (0.8, WATER[2]), (1, WATER[1])])
    gc = g_lin(fig, p0, p3, [(0, WATER[3]), (1, '#ffffff')])
    rr = max(0.6, w * 0.2)
    bead = ellipse(p3[0] + d[0] * rr * 0.6, p3[1] + d[1] * rr * 0.6, rr, rr)
    return outlined([(sh, gr, 1), (bead, WATER[1], 1), (core, gc, 0.75, 'n'),
                     (ellipse(p3[0] + d[0] * rr * 0.6 + rr * 0.3, p3[1] + d[1] * rr * 0.6 - rr * 0.35, rr * 0.35, rr * 0.3), '#ffffff', 1, 'n')], op=op)


def stream(fig, pts, w0, w1, op=1.0):
    """Une traînée d'eau le long d'une courbe (derrière le gant qui part) : fine derrière, pleine devant, crête claire."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=20)
    sh = taper(c, w0, w1, tip='round')
    crest = taper([(x + 0.25, y - 0.35) for x, y in c[4:]], w0 * 0.2, w1 * 0.3, tip='round')
    gr = g_lin(fig, c[0], c[-1], [(0, WATER[3]), (0.6, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.85, 'n')], w=1.1, op=op)


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


def burst(fig, X, Y, k, seeds, big=1.0, g=260.0, sizes=(1.2, 0.9)):
    """Des gouttes qui giclent d'un point et retombent (k : secondes depuis l'impact)."""
    out = []
    for j, (vx, vy) in enumerate(seeds):
        if k <= 0:
            break
        x, y = ballistic((X, Y), (vx * big, vy * big), g, k)
        if y < GR - 0.5:
            out.append(drop(fig, x, y, vx * big, vy * big + g * k, sizes[j % len(sizes)] * big, op=min(1, 2.5 - k * 2.2)))
    return out


def splash(fig, X, Y, k, big=1.0, dirs=((58, 13, -40, 3.2), (-18, 9, -30, 2.6)), seed=0):
    """Une gerbe d'impact : des nappes aux angles, longueurs et épaisseurs inégaux (jamais une main ouverte), de l'écume
    au point d'impact (k : 0 → 1 le temps de la gerbe)."""
    back, front = [], []
    if not (0 < k < 1):
        return back, front
    grow = min(1, k * 3.2)
    for j, (ang, L, bd, w) in enumerate(dirs):
        a = -ang
        back.append(sheet(fig, (X, Y), a, L * big * (0.4 + 0.6 * grow), bd * (1 + 0.6 * k), w * big, op=min(1, (1 - k) * 2.2),
                          tail=max(0, k - 0.35) * 1.1))
    front.append(foam(fig, X + 2 * big, Y, (2.4 + 2.2 * math.sin(math.pi * min(1, k * 1.6))) * big, op=min(1, (1 - k) * 2), seed=seed))
    return back, front


def ring_arc(C, rx, ry, a0, a1, w, n=24):
    """Un arc d'anneau (ellipse vue de côté), effilé aux deux bouts."""
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    ws = [w * math.sin(math.pi * i / n) ** 0.7 + 0.1 for i in range(n + 1)]
    left, right = sides(pts, ws)
    return sm(left + right[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.85)


def wave(fig, X, h, L, lead, op=1.0, crest=1.0):
    """La vague qui porte la toupie : un dos d'eau long derrière, une crête qui roule devant (écume), posée au sol."""
    if h < 0.5 or op <= 0.02:
        return ''
    G = GR + 0.4
    xs = [X - L, X - L * 0.6, X - L * 0.25, X + lead * 0.2, X + lead * 0.6, X + lead * 0.85, X + lead]
    ys = [G, G - h * 0.35, G - h * 0.8, G - h, G - h * 0.9, G - h * 0.5, G]
    sh = sm(list(zip(xs, ys)), sharp=(0, 6), t=0.9)
    gr = g_lin(fig, (X + lead * 0.5, G - h), (X - L * 0.5, G), [(0, WATER[2]), (0.4, WATER[3]), (1, WATER[4])])
    cr = sm([(X - L * 0.3, G - h * 0.82), (X, G - h * 1.02), (X + lead * 0.5, G - h * 0.98), (X + lead * 0.85, G - h * 0.55),
             (X + lead * 0.55, G - h * 0.7), (X, G - h * 0.84)], t=0.9)
    glint = ribbon([(X - L * 0.75, G - h * 0.15), (X - L * 0.5, G - h * 0.42), (X - L * 0.3, G - h * 0.62)], [0.2, max(0.5, h * 0.07), 0.2])
    deep = ribbon([(X - L * 0.6, G - 0.6), (X, G - h * 0.3), (X + lead * 0.6, G - 0.6)], [0.2, h * 0.22, 0.2])
    return outlined([(sh, gr, 1), (deep, WATER[4], 0.5, 'n'), (cr, '#ffffff', min(1, crest), 'n'), (glint, WATER[1], 0.6, 'n')],
                    w=1.4, op=op)


def curl(fig, C, r, a0, turn, w, op=1.0):
    """Une volute d'écume (sillage) : un ruban qui s'enroule, effilé."""
    if op <= 0.02 or r < 0.4:
        return ''
    n = 18
    pts = [(C[0] + r * (1 - 0.45 * i / n) * math.cos(math.radians(a0 + turn * i / n)),
            C[1] + r * 0.7 * (1 - 0.45 * i / n) * math.sin(math.radians(a0 + turn * i / n))) for i in range(n + 1)]
    sh = taper(pts, w, w * 0.25, tip='round')
    gr = g_lin(fig, pts[0], pts[-1], [(0, WATER[2]), (1, '#ffffff')])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


def spout(fig, X, top, wb, wt, t, op=1.0, spiral=1.0):
    """La trombe : une colonne d'eau qui monte du sol en tournant ; ses bords ondulent, une bande claire s'enroule
    autour en spirale (seul le côté visible est peint), une couronne d'écume au sommet."""
    if GR - top < 2 or op <= 0.02:
        return ''
    G = GR + 0.4
    H = G - top
    n = 14
    left, right, mids = [], [], []
    for i in range(n + 1):
        k = i / n
        y = G - H * k
        w = wb + (wt - wb) * k ** 0.7
        sway = 2.2 * math.sin(k * 4.2 + t * 7) * k
        x = X + sway
        left.append((x - w / 2, y))
        right.append((x + w / 2, y))
        mids.append((x, y, w))
    sh = sm(left + right[::-1], sharp=(0, 2 * n + 1), t=0.9)
    gr = g_lin(fig, (X - wb / 2, 0), (X + wb / 2, 0), [(0, WATER[4]), (0.35, WATER[3]), (0.75, WATER[2]), (1, WATER[1])])
    items = [(sh, gr, 1)]
    hi = taper([(x + w * 0.26, y) for x, y, w in mids[1:-1]], wb * 0.08, wt * 0.08, tip='round')
    dk = taper([(x - w * 0.3, y) for x, y, w in mids[1:-2]], wb * 0.08, wt * 0.05, tip='round')
    items += [(hi, '#ffffff', 0.7, 'n'), (dk, WATER[5], 0.35, 'n')]
    # la spirale : une bande qui fait le tour (on ne peint que le devant de chaque tour)
    if spiral > 0:
        m = 90
        seg = []
        for i in range(m + 1):
            k = i / m
            y = G - H * k
            w = wb + (wt - wb) * k ** 0.7
            sway = 2.2 * math.sin(k * 4.2 + t * 7) * k
            ph = k * 3.0 * 2 * math.pi + t * 14
            front = math.cos(ph)
            x = X + sway + math.sin(ph) * w * 0.48
            if front > 0.05 and k < 0.97:
                seg.append((x, y - 0.5, w))
            elif len(seg) > 3:
                c = [(a, b) for a, b, _ in seg]
                items.append((taper(c, 0.4, 0.4, tip='round', wmid=max(0.8, seg[len(seg) // 2][2] * 0.16) * spiral), WATER[1], 0.85, 'n'))
                seg = []
            else:
                seg = []
        if len(seg) > 3:
            c = [(a, b) for a, b, _ in seg]
            items.append((taper(c, 0.4, 0.4, tip='round', wmid=max(0.8, seg[len(seg) // 2][2] * 0.16) * spiral), WATER[1], 0.85, 'n'))
    out = outlined(items, w=1.5, op=op)
    cx = mids[-1][0]
    for j, (dx, dy, rr) in enumerate(((-0.62, 2.6, 0.24), (0.66, 2.2, 0.24), (-0.42, -0.6, 0.32), (0.4, -0.8, 0.34),
                                      (-0.16, -2.6, 0.4), (0.18, -3.4, 0.42), (0.0, -5.6, 0.34))):
        out += foam(fig, cx + dx * wt, top + dy * (wt / 14.0), rr * wt * (1 + 0.07 * math.sin(t * 11 + j * 1.7)), op=op, seed=j)
    return out


# ======================================================================== la toupie : Lilou rentrée dans sa carapace

def build_toupie(T, cx, hy, spin, tilt=0.0, squash=0.0, ow=0.95, frame=VIEW, eyes=True, ph=0.0, base=None):
    """La carapace qui tourne comme une toupie, à plat : un dôme d'écailles sur la lentille jaune du plastron, le
    rebord sable ; les écailles, les balanes et les trous (tête, pattes, queue) passent en tournant ; ses yeux guettent
    par le trou de la tête, les deux pans du bandeau en sortent et fouettent l'air."""
    fig = Figure(*frame, ow=ow)
    RX, RY, RB = 26.0, 21.0, 4.2               # demi-largeur, hauteur du dôme, demi-hauteur de l'ellipse du rebord
    by = (GR - 3.2 if base is None else base) - hy
    M = mchain(mR(tilt, cx, by), mS(1 + 0.5 * squash, 1 - squash, cx, by + 3))
    P = lambda pts: [mapp(M, p) for p in pts]
    PS = lambda sh: sh.map(lambda p: mapp(M, p))

    def surf(lon, lat, r=1.0):
        """Un point de la surface du dôme (longitude tournée par la toupie, latitude 0 = rebord, 90 = sommet)."""
        l = math.radians(lon + spin)
        a = math.radians(lat)
        x = cx + RX * r * math.cos(a) * math.sin(l)
        y = by - RY * math.sin(a) + RB * math.cos(a) * math.cos(l)
        vis = math.cos(a) * math.cos(l) + math.sin(a) * 0.35
        return (x, y), vis

    # ---- les pans du bandeau (qui sortent du trou de la tête) : derrière la toupie si le trou est derrière ----
    hl = math.radians(spin)
    hole_front = math.cos(hl) > 0
    hp_, _ = surf(0, 6)
    hp_ = mapp(M, hp_)

    def pans(front):
        out = []
        vel = (math.cos(hl), -0.16 * math.sin(hl))            # le trou file dans ce sens (vers la droite devant)
        rad = (math.sin(hl), 0.16 * math.cos(hl))
        for j, (L, w0, off) in enumerate(((17.0, 3.4, 0.0), (13.0, 3.0, 1.6))):
            d = (-vel[0] * 0.9 + rad[0] * 0.75 - 0.5, -vel[1] * 0.9 + rad[1] * 0.75 - 0.25 - 0.18 * j)
            n_ = math.hypot(*d) or 1
            d = (d[0] / n_, d[1] / n_)
            nrm = (-d[1], d[0])
            pts = []
            for i in range(6):
                t = i / 5
                wob = 1.6 * math.sin(ph * 1.4 - i * 1.3 + off) * t
                pts.append((hp_[0] + d[0] * L * t + nrm[0] * (wob + 2.2 * j - 1.0), hp_[1] + d[1] * L * t + nrm[1] * (wob + 2.2 * j - 1.0)))
            c = crpath(pts, 14)
            sh = taper(c, w0, w0 * 0.8, tip='round')
            out.append((sh, c))
        return out
    if not hole_front:
        for j, (sh, c) in enumerate(pans(False)):
            fig.part('pb%d' % j, sh, K.RED, grad=(c[0][0], c[0][1] - 2, c[-1][0], c[-1][1] + 2, [(0, K.RED.light), (1, K.RED.shadow)]),
                     cel=0.8, rim=0.5, cast=0)

    # ---- la lentille du plastron, sous le rebord ----
    lens = PS(ellipse(cx, by + 2.6, RX - 2.4, RB + 1.6))
    fig.part('lens', lens, K.PLAS, grad=(*mapp(M, (cx + RX, by)), *mapp(M, (cx - RX, by + 6)), [(0, K.PLAS.light), (0.6, K.PLAS.base), (1, K.PLAS.shadow)]),
             cel=1.0, rim=0.4, cast=0)

    # ---- le dôme : haut en demi-ellipse, bas = l'ellipse du rebord ----
    top = [(cx + RX * math.cos(math.radians(a)), by - RY * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    bot = [(cx - RX * math.cos(math.radians(a)), by + RB * math.sin(math.radians(a))) for a in range(10, 171, 10)]
    dome = sm(P(top + bot), t=0.9)
    det = []
    # les sillons entre les écailles (seul le devant est visible) : deux anneaux, des méridiens en quinconce
    def groove(pts_vis, w=1.0):
        segs, cur = [], []
        for p, v in pts_vis:
            if v > 0.02:
                cur.append(mapp(M, p))
            else:
                if len(cur) > 2:
                    segs.append(cur)
                cur = []
        if len(cur) > 2:
            segs.append(cur)
        out = []
        for s in segs:
            out += [(ribbon([(x - 0.2, y + 0.7) for x, y in s[::2]] if len(s) > 4 else [(x - 0.2, y + 0.7) for x, y in s],
                            [0.1] + [w * 0.6] * (len(s[::2] if len(s) > 4 else s) - 2) + [0.1]), K.SHELL.light, 0.5),
                    (ribbon(s, [0.1] + [w] * (len(s) - 2) + [0.1]), K.SHELL.deep, 0.85)]
        return out
    for lat in (24.0, 54.0):
        det += groove([surf(lon, lat) for lon in range(0, 361, 6)], 1.1)
    for lon in (20, 80, 140, 200, 260, 320):
        det += groove([surf(lon, lat) for lat in range(4, 25, 2)], 1.0)
    for lon in (50, 122, 194, 266, 338):
        det += groove([surf(lon, lat) for lat in range(24, 55, 3)], 1.0)
    # chaque écaille bombée : une lumière douce sur celles qui regardent la lumière (en haut à droite)
    for lat, lons in ((14, (50, 110, 170, 230, 290, 350)), (39, (86, 158, 230, 302, 14)), (72, (0,))):
        for lon in lons:
            (x, y), v = surf(lon, lat)
            if v < 0.15:
                continue
            l = math.radians(lon + spin)
            lit = max(0.0, 0.55 * math.sin(math.radians(lat)) + 0.6 * math.cos(math.radians(lat)) * math.sin(l))
            rx = (7.0 if lat < 60 else 9.0) * (0.35 + 0.65 * abs(math.cos(l)) if lat < 60 else 1)
            ry = 3.4 if lat < 60 else 3.6
            q = mapp(M, (x + 0.8, y - 0.8))
            det += [(ellipse(q[0], q[1], rx, ry), ('rad', q[0], q[1], rx, ry, [(0, K.SHELL.hi, 0.55 * lit * min(1, v * 2)), (1, K.SHELL.hi, 0)]), 1)]
    # le rebord sable (écailles marginales) le long du bas
    rim_pts = [mapp(M, surf(lon, 3)[0]) for lon in range(-90 - int(spin) % 1, 91, 6)]
    rim_c = [mapp(M, (cx + RX * math.sin(math.radians(a)), by + RB * math.cos(math.radians(a)) - 1.4)) for a in range(-88, 89, 8)]
    det += [(ribbon(rim_c, [0.6] + [3.0] * (len(rim_c) - 2) + [0.6]), ('lin', *mapp(M, (cx + RX, by)), *mapp(M, (cx - RX, by + 4)),
                                                                     [(0, K.SHELL.hi), (0.5, K.SHELL.light), (1, K.SHELL.base)]), 0.95)]
    del rim_pts
    # les trous de la tête, des pattes et de la queue ; la balane ; ils passent en tournant
    holes = [(0, 3.6, 2.6), (58, 2.8, 2.2), (-58, 2.8, 2.2), (128, 2.6, 2.0), (-128, 2.6, 2.0), (180, 1.8, 1.5)]
    for lon, w, h in holes:
        (x, y), v = surf(lon, 4)
        l = math.radians(lon + spin)
        if math.cos(l) < 0.15:
            continue
        k = math.cos(l)
        q = mapp(M, (x, y))
        det += [(ellipse(q[0], q[1] - 0.2, w * (0.25 + 0.75 * k), h), '#1a0c16', 1),
                (ellipse(q[0] + 0.2, q[1] - 0.9, w * (0.25 + 0.75 * k) * 0.8, h * 0.35), K.SHELL.deep, 0.8)]
        if lon == 0 and eyes and k > 0.55:
            # ses yeux guettent par le trou de la tête
            for ex in (-1.1, 1.1):
                e = (q[0] + ex * k, q[1] + 0.1)
                det += [(ellipse(e[0], e[1], 0.75 * k, 0.6), K.EYE[1], 1), (ellipse(e[0] + 0.25, e[1], 0.32 * k, 0.42), K.EYE[3], 1),
                        (ellipse(e[0] + 0.35, e[1] - 0.25, 0.16, 0.14), '#fff6d0', 1)]
    for (lon, lat, r) in ((200, 30, 1.4), (70, 12, 1.1)):
        (x, y), v = surf(lon, lat)
        if v > 0.25:
            q = mapp(M, (x, y))
            det += [(ellipse(q[0] - 0.3, q[1] + 0.35, r * 1.05, r * 0.8), K.SHELL.deep, 0.5), (ellipse(q[0], q[1], r, r * 0.75), K.CLAW.light, 1),
                    (ellipse(q[0] + 0.05, q[1] - 0.25, r * 0.4, r * 0.22), K.SHELL.deep, 1)]
    fig.part('dome', dome, K.SHELL, grad=(*mapp(M, (cx + RX * 0.6, by - RY)), *mapp(M, (cx - RX * 0.8, by + RB)),
                                          [(0, K.SHELL.light), (0.45, K.SHELL.base), (1, K.SHELL.shadow)]),
             cel=2.0, rim=0.9, cast=1.2, cast_on=['lens'], details=det)
    if hole_front:
        for j, (sh, c) in enumerate(pans(True)):
            fig.part('pf%d' % j, sh, K.RED, grad=(c[0][0], c[0][1] - 2, c[-1][0], c[-1][1] + 2, [(0, K.RED.light), (1, K.RED.shadow)]),
                     cel=0.8, rim=0.5, cast=0.9, cast_on=['dome'])
    fig.ctx = dict(C=(cx, by - RY * 0.4), base=(cx, by + RB), RX=RX)
    return fig


# ======================================================================== les effets des actions

HIT = {}


def fist_path(T, t0, which, dts):
    """Où était le poing un peu avant (pour la traînée d'eau)."""
    out = []
    for dt in dts:
        if T - dt >= t0:
            P, _ = pose_at(T - dt, 'attack', t0)
            out.append(K.skeleton(dict(K.REST, **P))[which])
    return out


def fx_attack(tl, T, t0):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        # la traînée d'eau derrière le jab (le gant lointain part tout droit)
        if 300 <= tl <= 400:
            pts = fist_path(T, t0, 'far_fist', (0.09, 0.06, 0.03)) + [ctx['far_fist']]
            if len(pts) >= 3:
                pts = [(x - 6, y + 1.5) for x, y in pts]
                back.append(stream(fig, pts, 0.4, 3.4, op=env(tl, 300, 320, 360, 400)))
        # l'impact du jab : éclat d'écume, deux petites nappes, des gouttes en avant
        if tl >= JAB_HIT - 5 and 'jab' not in HIT:
            HIT['jab'] = ctx['far_fist']
        if 'jab' in HIT and JAB_HIT <= tl <= 900:
            X, Y = HIT['jab'][0] + 7, HIT['jab'][1]
            k = (tl - JAB_HIT) / 300
            b, fr = splash(fig, X, Y, k, 0.8, dirs=((52, 12, -40, 3.0), (-20, 9, -30, 2.4)), seed=1)
            back += b
            front += fr
            front += burst(fig, X, Y, (tl - JAB_HIT) / 1000, [(60, -70), (85, -35), (40, -95), (70, 10), (95, -60)])
        # la traînée d'eau courbe derrière le direct (le gant proche, tout le corps derrière)
        if 470 <= tl <= 590:
            pts = fist_path(T, t0, 'near_fist', (0.1, 0.075, 0.05, 0.025)) + [ctx['near_fist']]
            if len(pts) >= 3:
                pts = [(x - 7, y + 1.0) for x, y in pts]
                back.append(stream(fig, pts, 0.5, 4.6, op=env(tl, 470, 500, 545, 590)))
        # l'impact du direct : la grande gerbe (trois jets très différents), l'écume, les gouttes qui retombent
        if tl >= CROSS_HIT - 5 and 'cross' not in HIT:
            HIT['cross'] = ctx['near_fist']
        if 'cross' in HIT and CROSS_HIT <= tl:
            X, Y = HIT['cross'][0] + 9, HIT['cross'][1]
            k = (tl - CROSS_HIT) / 420
            b, fr = splash(fig, X, Y, k, 1.0, dirs=((64, 22, -60, 5.2), (-26, 12, -34, 3.4), (122, 9, 46, 2.4)), seed=3)
            back += b
            front += fr
            front += burst(fig, X, Y, (tl - CROSS_HIT) / 1000, [(70, -110), (110, -55), (40, -140), (120, 15), (10, -120), (90, 30),
                                                                (-20, -110), (130, -80)], big=1.0)
    return f


def fx_idle(T):
    def f(fig, ctx):
        pass
    return f


def fx_special(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        P = ctx.get('P', {})
        # elle se ramasse, l'eau monte autour de ses pieds ; elle saute : un cercle de gouttes
        if 200 <= tl <= 420:
            k = (tl - 270) / 1000
            fx0 = 64 + 2
            if k > 0:
                front += burst(fig, fx0 + 6, GR - 1, k, [(-60, -80), (55, -95), (-25, -120), (85, -60), (10, -130)], big=0.8)
            back.append(wave(fig, fx0, 5 * env(tl, 200, 270, 300, 420), 26, 22, op=env(tl, 200, 260, 330, 420)))
        # l'atterrissage à plat sur la vague : une couronne d'eau
        if 400 <= tl <= 620:
            k = (tl - 405) / 215
            X = 70.0
            b, fr = splash(fig, X, GR - 2, k, 1.0, dirs=((150, 13, 30, 3.2), (112, 17, 20, 3.8), (68, 17, -20, 3.8), (28, 13, -30, 3.2)), seed=2)
            back += b
            front += fr
        if TUCK_END <= tl < POP:
            cx, hy, spin, tilt, sq = top_at(tl)
            L = env(tl, 380, 450, 760, 860)
            # le sillage d'écume et ses volutes (ils restent derrière, là où elle est passée)
            for j in range(7):
                tj = tl - 60 - j * 55
                if tj < 420:
                    continue
                xj = top_at(tj)[0] - 26
                age = (tl - tj) / 500
                if age < 1:
                    back.append(curl(fig, (xj, GR - 2.2 - 1.2 * (j % 2)), 3.4 - 1.6 * age, 160 + 50 * j, -260, 1.6, op=(1 - age) * L))
                    front.append(foam(fig, xj + 4, GR - 1.0, 2.0 * (1 - age) + 0.4, op=(1 - age) * L, seed=j))
            # la vague qui la porte : un dos long derrière, la crête qui roule devant
            back.append(wave(fig, cx, 12 * L, 36, 30, op=L, crest=1.0))
            # l'anneau d'eau qui tourbillonne autour d'elle : la moitié du fond derrière, celle de devant par-dessus
            if L > 0.2:
                C = (cx, GR - 9.0)
                for j, (a0, span) in enumerate(((spin * 1.4) % 360, 120), ) if False else ():
                    pass
                for j in range(3):
                    a0 = (spin * 1.3 + j * 120) % 360
                    a1 = a0 + 80
                    sh = ring_arc(C, 34, 6.6, a0, a1, 2.6 * L)
                    gr = g_lin(fig, (C[0] + 34, C[1]), (C[0] - 34, C[1]), [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])])
                    mid = math.sin(math.radians((a0 + a1) / 2))
                    (front if mid > 0 else back).append(outlined([(sh, gr, 1)], w=1.1, op=L))
            # la vague se brise devant elle quand elle freine
            if tl >= 740:
                k = (tl - 740) / 200
                b, fr = splash(fig, cx + 26, GR - 6, k, 1.2, dirs=((40, 20, -50, 4.4), (78, 15, -30, 3.6), (8, 11, -20, 2.8)), seed=4)
                back += b
                front += fr
        # elle jaillit de sa carapace : une gerbe tout autour
        if POP - 20 <= tl <= POP + 260:
            k = (tl - POP + 20) / 280
            X = 64 + XT
            b, fr = splash(fig, X, GR - 4, k, 1.2, dirs=((160, 14, 30, 3.6), (118, 20, 20, 4.4), (62, 20, -20, 4.4), (22, 14, -30, 3.6)), seed=5)
            back += b
            front += fr
            front.append(wave(fig, X, 8 * (1 - k), 30, 26, op=1 - k))
        # l'uppercut : la traînée d'eau du poing qui monte, la trombe qui jaillit, monte, tient, puis s'effondre en pluie
        if 990 <= tl <= 1110:
            pts = []
            for dt in (0.08, 0.06, 0.04, 0.02, 0.0):
                Pp, _ = pose_at(ctx['T'] - dt, 'special', ctx['t0'])
                pts.append(K.skeleton(dict(K.REST, **Pp))['far_fist'])
            pts = [(x + 2, y + 6) for x, y in pts]
            front.append(stream(fig, pts, 0.5, 4.4, op=env(tl, 990, 1010, 1060, 1110)))
        if 1000 <= tl <= 1700:
            rise = env(tl, 1000, 1060, 1260, 1400)
            top = GR - 4 - 150 * rise
            wb = 22 * (0.4 + 0.6 * min(1, (tl - 1000) / 80))
            back.append(spout(fig, SPOUT_X, top, wb, 15, tl / 1000, op=min(1, (1700 - tl) / 200, (tl - 995) / 30),
                              spiral=1.0 if tl < 1300 else max(0, (1400 - tl) / 100)))
            # la pluie : la trombe s'effondre, les gouttes retombent tout autour
            if tl > 1260:
                k = (tl - 1260) / 1000
                for j in range(14):
                    x0 = SPOUT_X + ((j * 37) % 29 - 14) * 1.4
                    y0 = GR - 40 - (j * 53 % 80)
                    x, y = ballistic((x0, y0), ((j % 5 - 2) * 14, -30 - 10 * (j % 3)), 260, k - 0.02 * (j % 4))
                    if y < GR and k > 0.02 * (j % 4):
                        front.append(drop(fig, x, y, (j % 5 - 2) * 14, -30 + 260 * k, 1.2 if j % 3 else 0.9, op=min(1, (1.4 - k) * 2)))
                if tl < 1600:
                    for j in range(3):
                        front.append(foam(fig, SPOUT_X - 8 + 8 * j, GR - 1.4, 2.6 * env(tl, 1260, 1320, 1480, 1600), seed=j))
        # elle retombe et revient en deux bonds : de petites éclaboussures sous les pieds, l'eau ruisselle
        for t_land, X in ((1370, 64 + XT), (1470, 64 + XT - 48), (1590, 64)):
            if t_land - 10 <= tl <= t_land + 260:
                k = (tl - t_land + 10) / 270
                b, fr = splash(fig, X - 8, GR - 0.5, k, 0.6, dirs=((150, 9, 30, 2.6), (32, 9, -30, 2.6)), seed=6)
                back += b
                front += fr
                b, fr = splash(fig, X + 26, GR - 0.5, k, 0.55, dirs=((140, 8, 30, 2.4), (40, 9, -30, 2.4)), seed=7)
                back += b
                front += fr
        if 1290 <= tl <= 1800 and not ctx.get('toupie'):
            k = (tl - 1290) / 1000
            for j, (p, vx) in enumerate(((ctx.get('far_fist'), 10), (ctx.get('shell'), -12), (ctx.get('near_fist'), 6))):
                if p is None:
                    continue
                tt = (k * 3.0 + j * 0.37) % 1.0
                x, y = ballistic((p[0], p[1] + 2), (vx, 0), 220, tt * 0.5)
                if y < GR - 1:
                    front.append(drop(fig, x, y, vx, 220 * tt * 0.5, 0.9, op=min(1, (1.6 - k * 2))))
    return f


# ======================================================================== le fond, l'ombre, la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael et les autres héros)."""
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


def shadow_layer(w, h, view, cx, lift, half=40.0, floor_y=GR):
    """L'ombre douce au sol sous l'héroïne (elle la suit, rétrécit quand elle saute)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    s = max(0.45, 1 - lift / 45)
    X = (cx - x0) * k
    ImageDraw.Draw(sh).ellipse([X - half * s * k, fy - 2.6 * k * s, X + half * s * k, fy + 2.6 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 0.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.85), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.0), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_svg(T, segs, view=VIEW, ow=0.95):
    """Le SVG d'une image, et ce qu'il faut pour l'ombre au sol (x du milieu, hauteur, demi-largeur)."""
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P, tl = pose_at(T, act, t0)
    if act == 'special' and TUCK_END <= tl < POP:
        cx, hy, spin, tilt, sq = top_at(tl)
        L = env(tl, 380, 450, 760, 860)
        fig = build_toupie(T, cx, hy + 5.5 * L, spin, tilt, sq, ow=ow, frame=view, ph=P['ph'])
        fig.ctx.update(P=P, T=T, t0=t0, toupie=True)
        fx_special(tl)(fig, fig.ctx)
        return fig.svg(), (cx, hy + 3, 30.0)
    if act == 'attack':
        if tl < 300:
            HIT.clear()
        fx = [fx_attack(tl, T, t0)]
    elif act == 'special':
        def ctxfx(fig, ctx):
            ctx.update(T=T, t0=t0)
            fx_special(tl)(fig, ctx)
        fx = [ctxfx]
    else:
        fx = [fx_idle(T)]
    fig = K.build(ow=ow, pose=P, fx=fx, frame=view)
    return fig.svg(), (62 + P['shift'], P['lift'], 40.0)


def render(frames_svg, w, h, prefix):
    """Rend les SVG en PNG (un seul navigateur)."""
    import json
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def compose(png, sh, w, h, view):
    im = background(w, h, view)
    im.alpha_composite(shadow_layer(w, h, view, sh[0], sh[1], sh[2]))
    im.alpha_composite(Image.open(png))
    return im


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
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [0.3, a_s + 0.25, a_s + 0.36, a_s + 0.52, a_s + 0.6, a_s + 0.8,
                            s_s + 0.26, s_s + 0.36, s_s + 0.5, s_s + 0.65, s_s + 0.8, s_s + 0.9, s_s + 1.03, s_s + 1.15, s_s + 1.33, s_s + 1.5]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, (p, (_, sh)) in enumerate(zip(pngs, fr)):
            im = compose(p, sh, 640, 360, VIEW)
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('LILOU_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    for i, (p, (_, sh)) in enumerate(zip(pngs, fr)):
        compose(p, sh, VW, VH, VIEW).convert('RGB').save(os.path.join(TMP, 'v%04d.png' % i))
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
