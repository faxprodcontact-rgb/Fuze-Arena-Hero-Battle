# L'homme-poisson vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/homme-poisson/
# build.py) — la garde nerveuse (il sautille sur ses jambes pliées, les nageoires ondulent), l'attaque de base « Coup de
# harpon », l'attaque spéciale « Ruée des abysses » — dans le style lisse de l'interface (comme Kael : heros/kael/anim.py,
# et son général Kesha : heros/kesha/anim.py, dont il reprend les outils d'eau).
#
#   python3 refonte-graphique/ui-moderne/monstres/homme-poisson/anim.py                # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/homme-poisson/anim.py --planche [t…]  # planche d'images clés (contrôle)
#
# Méthode : chaque image redessine homme-poisson.py dans une POSE (il se ramasse sur ses jambes, le buste respire et se
# penche depuis les hanches, la tête suit avec un temps de retard, la gueule s'ouvre autour de sa charnière, une onde
# court dans les nageoires, le pagne suit ; la lance avance dans son axe et les deux bras la suivent par cinématique
# inverse ; en l'air les jambes se replient). Les poses clés reprennent celles du pixel art (mêmes temps : ramassé tenu,
# bond très court, arrêt sur l'impact, retrait sec, sauts en arrière), reliées par des courbes douces sans dépassement,
# 24 images/s. Les effets d'eau (ruban, gerbes, gouttes, écume, bulles des abysses, spirale, explosion, pluie, flaque)
# sont ceux des héros d'eau vectoriels (mêmes couleurs que Kesha et Ilian) : dégradés, un seul contour bleu nuit, aucun
# flou.
import importlib.util
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
_spec = importlib.util.spec_from_file_location('homme_poisson', os.path.join(HERE, 'homme-poisson.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import taper, crpath  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', K.NOM)
TMP = os.environ.get('HP_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-22, -42, 290, 163.125)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WINK = '#0c1846'                     # le contour de l'eau (bleu nuit presque noir, comme Kesha et Ilian)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']

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


PAIRS = {'head': ('headx', 'heady')}
SCAL = ['crouch', 'lean', 'tilt', 'gape', 'd', 'fin', 'wamp', 'pan', 'shift', 'drop', 'tuck', 'pitch', 'ang']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Coup de harpon » (pixel : ATTAQUE). Il se ramasse d'un coup (tenu) : lance tirée en arrière, buste en arrière,
# nageoires et crête dressées, gueule ouverte. Il FILE d'un bond vers l'ennemi (nageoires couchées par la vitesse, ruban
# d'eau derrière lui), la lance part dans son axe et pique : arrêt sur l'image, gerbe au bout de la pointe, gueule grande
# ouverte. Il retire la lance d'un coup sec et revient en deux sauts légers en arrière ; il retombe accroupi.
CROUCH = dict(crouch=2.6, lean=-2.6, head=(-1.0, 1.0), tilt=-3, d=-4.4, gape=2.2, fin=1.0, pan=1.2)
ATTACK = [
    (0, {}),
    (110, dict(crouch=0.9, lean=-0.8, d=-1.4, gape=0.8, fin=0.3, pan=0.4)),
    (300, CROUCH),
    (420, dict(CROUCH, crouch=2.8, lean=-2.9, d=-4.5, gape=2.4)),
    (465, dict(shift=15, crouch=0.6, lean=2.4, head=(1, 0), tilt=1, d=2, gape=1.6, fin=-1.0, pan=-2)),
    (510, dict(shift=31, crouch=0.8, lean=3.4, head=(1.4, 0), tilt=2, d=11, gape=3.2, fin=-1.0, pan=-2)),
    (535, dict(shift=34, crouch=1.0, lean=3.6, head=(1.6, 0.2), tilt=2.4, d=14, gape=4.4, fin=-0.7, pan=-1.6)),
    (675, dict(shift=34, crouch=1.1, lean=3.5, head=(1.5, 0.3), tilt=2.2, d=13.6, gape=4.2, fin=-0.6, pan=-1.4)),
    (735, dict(shift=30, crouch=1.8, lean=1.0, head=(0, 1), tilt=-1, d=0, gape=1.0, fin=0.2, pan=1)),
    (815, dict(shift=18, drop=-7, crouch=-0.4, tuck=0.6, lean=-1, head=(0, 1), d=0, gape=0.6, fin=0.4, pan=1)),
    (895, dict(shift=7, drop=-4, crouch=0.0, tuck=0.35, lean=-1, d=0, fin=0.3, pan=0.4)),
    (965, dict(crouch=2.4, lean=0, head=(0, 1), pan=-1)),
    (1090, dict(crouch=0.8, head=(0, 0.6), pan=-0.3)),
    (1240, {}),
]
ATTACK_HIT = 535

# 3) « Ruée des abysses » (pixel : SPECIALE). Il se ramasse très bas, gueule ouverte : les bulles des abysses montent
# autour de lui (tenu). Il FONCE sur l'ennemi dans un ruban d'eau et le pique trois fois, très vite (une gerbe à chaque
# coup, de plus en plus grosse). Il se ramasse et BONDIT : un jet d'eau le lance en l'air ; au plus haut, l'eau
# s'enroule en volutes autour de la pointe. Il plonge sur l'ennemi et le PIQUE (arrêt sur l'image) : explosion d'eau
# (écume, couronne de nappes, bulles, gouttes). L'eau retombe en pluie et fait une flaque sous l'ennemi ; il revient
# d'un grand saut en arrière et retombe accroupi dans une petite gerbe.
XS = 54
SPECIAL = [
    (0, {}),
    (150, dict(crouch=3.2, lean=-2.6, head=(-1, 1), tilt=-3, d=-4.4, gape=3.0, fin=1.0, pan=1.2)),
    (390, dict(crouch=3.4, lean=-2.8, head=(-1.1, 1.2), tilt=-3.4, d=-4.5, gape=3.2, fin=1.1, pan=1.3)),
    (440, dict(shift=26, crouch=0.6, lean=3.0, head=(1, 0), d=-1, gape=2.0, fin=-1.0, pan=-2)),
    (490, dict(shift=XS, crouch=0.8, lean=3.4, head=(1.4, 0), tilt=2, d=11, gape=3.4, fin=-0.8, pan=-2)),
    (560, dict(shift=XS, crouch=1.4, lean=2.0, head=(0.4, 0.4), d=-1, gape=1.2, fin=-0.4, pan=-1)),
    (620, dict(shift=XS + 2, crouch=0.8, lean=3.6, head=(1.5, 0), tilt=2.2, d=12, gape=3.6, fin=-0.8, pan=-2)),
    (690, dict(shift=XS + 2, crouch=1.4, lean=2.0, head=(0.4, 0.4), d=-1, gape=1.2, fin=-0.4, pan=-1)),
    (760, dict(shift=XS + 4, crouch=0.8, lean=4.0, head=(1.8, 0), tilt=2.8, d=14, gape=4.4, fin=-0.9, pan=-2)),
    (850, dict(shift=XS - 2, crouch=3.4, lean=-1.0, head=(0, 1), tilt=-2, d=-4, gape=1.0, fin=1.0, pan=1)),
    (930, dict(shift=XS + 2, drop=-26, crouch=-0.6, tuck=0.5, lean=1.0, head=(0, 1), d=-4, gape=2.0, fin=-1.0, pan=-2)),
    (1020, dict(shift=XS + 6, drop=-36, crouch=0.4, tuck=1.0, lean=2.0, d=-4.4, gape=3.0, fin=-0.4, pan=-1, pitch=4)),
    (1085, dict(shift=XS + 7, drop=-35, crouch=0.4, tuck=1.0, lean=2.2, d=-4.4, gape=3.2, fin=-0.3, pan=-1, pitch=8, ang=2)),
    (1150, dict(shift=XS + 12, drop=-26, crouch=0.4, tuck=0.7, lean=4.2, head=(1.6, 0), tilt=3, d=10, gape=4.6, fin=-1.0,
                pan=-2, pitch=16, ang=6)),
    (1370, dict(shift=XS + 12, drop=-25, crouch=0.5, tuck=0.65, lean=4.0, head=(1.5, 0.2), tilt=2.6, d=9.6, gape=4.4,
                fin=-0.8, pan=-1.6, pitch=15, ang=5.6)),
    (1440, dict(shift=XS - 4, drop=-28, crouch=0.2, tuck=0.6, lean=-2.0, head=(-1, 1), tilt=-2, d=-2, gape=1.0, fin=0.6,
                pan=1, pitch=-4)),
    (1540, dict(shift=30, drop=-22, tuck=0.5, lean=-1.0, head=(0, 1), d=0, fin=0.5, pan=1, pitch=-2)),
    (1630, dict(shift=12, drop=-10, tuck=0.3, lean=-1.0, d=0, fin=0.3, pan=0.4)),
    (1710, dict(crouch=3.0, lean=0, head=(0, 1), pan=-1)),
    (1860, dict(crouch=1.4, head=(0, 1), pan=-0.4)),
    (2060, {}),
]
SP_HITS = [(490, 0.8), (620, 0.9), (760, 1.1)]
SP_PLUNGE = 1150


# ======================================================================== la garde nerveuse (en boucle)

def idle_offsets(T):
    ub = 2 * math.pi * T / 0.6           # il rebondit sur ses jambes pliées (deux fois par souffle et demi)
    ur = 2 * math.pi * T / 1.8           # le souffle
    return dict(breath=0.5 - 0.5 * math.cos(ur), crouch=0.75 * (0.5 - 0.5 * math.cos(ub)),
                heady=0.4 * (0.5 - 0.5 * math.cos(ub - 0.9)) - 0.15, headx=0.15 * math.sin(ub - 0.9),
                tilt=0.7 * math.sin(ur - 0.6), gape=0.6 + 0.6 * math.sin(ur - 1.2), d=0.35 * math.sin(2 * math.pi * T / 0.42),
                pan=0.6 * math.sin(ub - 1.3), wamp=0.55, fin=0.08 * math.sin(ur))


def blink_at(T):
    """La membrane passe sur l'œil (toutes les 3,4 s, aller-retour en 0,2 s)."""
    k = (T % 3.4) - 2.1
    if 0 <= k <= 0.22:
        return math.sin(math.pi * k / 0.22) ** 0.7
    return 0.0


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : garde (pondérée) + action en cours."""
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
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath']
    P['head'] = (P.pop('headx'), P.pop('heady'))
    # l'onde des nageoires court toujours ; plus forte quand il file (les nageoires battent)
    P['wave'] = 2 * math.pi * T / 0.95
    P['wamp'] = P['wamp'] + (1 - w) * 0.35
    P['blink'] = blink_at(T) if w > 0.95 else 0.0
    return P, tl


# ======================================================================== l'eau (outils et couleurs de Kesha)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour ; une 4e valeur = pas de silhouette (un reflet dedans)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, 2 * op)), sil, col)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte : ronde devant, effilée derrière (dans le sens de sa course), éclairée en haut à droite."""
    if op <= 0.02:
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


def bubble(fig, x, y, r, op=1.0):
    """Une bulle des abysses : un anneau d'eau (clair en haut à droite, plus sombre en bas à gauche), un reflet blanc ;
    le milieu reste transparent (on voit à travers)."""
    if r < 0.3 or op <= 0.02:
        return ''
    ringsh = ellipse(x, y, r, r).hole(ellipse(x - 0.06 * r, y + 0.06 * r, r * 0.66, r * 0.66))
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, '#ffffff'), (0.4, WATER[1]), (1, WATER[3])])
    inner = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.22"/>' % (fm(x), fm(y), fm(r * 0.7), WATER[2])
    hi = ellipse(x + 0.38 * r, y - 0.42 * r, 0.26 * r, 0.18 * r, -35)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, 2 * op)), inner,
                                          outlined([(ringsh, gr, 1), (hi, '#ffffff', 1, 'n')], w=0.9, op=1))


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
    """Un filet / ruban d'eau le long d'une courbe : fin derrière, plein devant, crête claire."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=20)
    sh = taper(c, w0, w1, tip='round')
    crest = taper([(x + 0.25, y - 0.35) for x, y in c[4:]], w0 * 0.2, w1 * 0.3, tip='round')
    gr = g_lin(fig, c[0], c[-1], [(0, WATER[3]), (0.6, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.85, 'n')], w=1.1, op=op)


def mound(fig, X, h, L, op=1.0, foamy=1.0):
    """Une bosse d'eau posée au sol (gerbe qui retombe, flaque) : dos courbe, écume sur le dessus."""
    if h < 0.6 or op <= 0.02:
        return ''
    G = GR + 0.4
    sh = sm([(X - L, G), (X - L * 0.6, G - h * 0.55), (X - L * 0.2, G - h), (X + L * 0.25, G - h * 0.95), (X + L * 0.65, G - h * 0.45),
             (X + L, G)], sharp=(0, 5), t=0.9)
    gr = g_lin(fig, (X + L * 0.5, G - h), (X - L * 0.6, G), [(0, WATER[2]), (0.45, WATER[3]), (1, WATER[4])])
    crest = sm([(X - L * 0.55, G - h * 0.58), (X - L * 0.2, G - h * 0.98), (X + L * 0.25, G - h * 0.93), (X + L * 0.6, G - h * 0.5),
                (X + L * 0.2, G - h * 0.68), (X - L * 0.2, G - h * 0.72)], t=0.9)
    glint = ribbon([(X - L * 0.7, G - h * 0.2), (X - L * 0.5, G - h * 0.45), (X - L * 0.3, G - h * 0.62)], [0.2, max(0.5, h * 0.06), 0.2])
    return outlined([(sh, gr, 1), (crest, '#ffffff', min(1, foamy), 'n'), (glint, WATER[1], 0.6, 'n')], w=1.4, op=op)


def curl(fig, C, r0, a0, turn, w, op=1.0, cw=False, light=False):
    """Une volute d'eau : un ruban qui s'enroule en spirale autour de C (de r0 vers le centre), effilé au bout."""
    if op <= 0.02 or r0 < 0.5:
        return ''
    n = 22
    pts = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (turn * t if cw else -turn * t))
        r = r0 * (1 - 0.6 * t)
        pts.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    sh = taper(pts, w, w * 0.18, tip='sharp', wmid=w * 0.85)
    gr = g_lin(fig, pts[0], pts[-1], [(0, WATER[2] if light else WATER[3]), (0.6, WATER[2]), (1, '#ffffff')])
    hl = taper([(x + 0.25, y - 0.3) for x, y in pts[3:-4]], w * 0.25, w * 0.12, tip='sharp')
    return outlined([(sh, gr, 1), (hl, '#ffffff', 0.75, 'n')], w=1.1, op=op)


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


def splash_hit(fig, X, Y, tau, big=1.0, seed=0):
    """La gerbe au bout de la pointe quand elle pique : des nappes qui partent en éventail, une boule d'écume, des
    gouttes (tau : secondes depuis l'impact)."""
    if tau < 0 or tau > 0.8:
        return
    e = env(tau, 0, 0.03, 0.14, 0.4)
    for j, (ang, L, bd, w) in enumerate(((-52, 18, -50, 4.2), (10, 15, -40, 3.8), (-104, 12, 40, 3.0), (-80, 13, 20, 3.2),
                                         (40, 10, 30, 2.8))):
        L_ = L * big * (0.45 + 0.55 * min(1, tau / 0.12))
        (fig.fx_back if j in (0, 1) else fig.fx_front).append(
            sheet(fig, (X - 1, Y), ang + 6 * seed, L_ * (0.45 + 0.55 * e), bd, w * big * (0.75 + 0.25 * e), op=0.5 * e ** 1.5,
                  tail=min(0.25, max(0, tau - 0.15) * 1.2)))
    pe = env(tau, 0, 0.02, 0.1, 0.3)
    if pe > 0:
        fig.fx_front.append(foam(fig, X + 2.2, Y - 0.4, (4.2 * pe + 1.0) * big, op=pe, seed=1 + seed))
    for j, (vx, vy) in enumerate(((60, -95), (95, -40), (30, -125), (85, 15), (-15, -110), (115, -70), (50, -20))):
        if tau < 0.75:
            x, y = ballistic((X + 2, Y), (vx * big, vy * big), 260, tau)
            if y < GR:
                fig.fx_front.append(drop(fig, x, y, vx, vy + 260 * tau, 1.0 if j % 2 else 0.75, op=min(1, (0.75 - tau) * 4)))


def dash_ribbon(fig, pts, k):
    """Le ruban d'eau qui le suit quand il file (de ses pieds à son dos), avec quelques gouttes arrachées."""
    if k <= 0.02 or len(pts) < 3:
        return
    fig.fx_back.append(stream(fig, pts, 0.6, 5.0 * k + 0.6, op=min(1, 2.5 * k)))


def landing(fig, X, k, big=1.0):
    """La petite gerbe quand il retombe : deux nappes basses, de l'écume, quelques gouttes."""
    if k <= 0 or k >= 1:
        return
    e = math.sin(math.pi * min(1, k * 1.3)) if k < 0.77 else max(0, (1 - k) / 0.23)
    for j, (dx, ang, L, bd, w) in enumerate(((-10, -150, 10, -30, 3.0), (10, -30, 10, 30, 3.0), (-4, -115, 8, -20, 2.6),
                                             (4, -65, 8, 20, 2.6))):
        fig.fx_front.append(sheet(fig, (X + dx * big, GR + 0.2), ang, L * big * (0.4 + 0.6 * min(1, k * 2.5)), bd, w * big,
                                  op=min(1, e * 1.6), tail=max(0, k - 0.5) * 1.2))
    fig.fx_front.append(mound(fig, X, 3.2 * big * e, 16 * big, op=min(1, e * 1.5)))
    for j in range(3):
        fig.fx_front.append(foam(fig, X - 8 * big + 8 * big * j, GR - 1.0, 1.4 * big * e, op=min(1, e * 1.5), seed=j))


# ---- l'attaque de base

HIT = {}


def fx_attack(tl, path, back_pts):
    def f(fig, ctx):
        tip = ctx['tip']
        # le ruban d'eau derrière lui quand il file, la traînée de la pointe
        k = env(tl, 430, 470, 520, 620)
        dash_ribbon(fig, back_pts, k)
        if 440 <= tl <= 560 and len(path) >= 2:
            kk = env(tl, 440, 480, 535, 570)
            fig.fx_back.append(stream(fig, path + [tip], 0.5, 3.6 * kk + 0.4, op=min(1, 3 * kk)))
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0:
            if 'c' not in HIT:
                HIT['c'] = tip
            splash_hit(fig, HIT['c'][0], HIT['c'][1], tau)
        # il retombe : quelques gouttes de ses nageoires, une petite gerbe sous les pieds
        if 950 <= tl <= 1300:
            landing(fig, 66 + ctx['P']['shift'], (tl - 950) / 330.0, 0.7)
    return f


# ---- l'attaque spéciale

SPH = {}


def fx_special(tl, path, back_pts):
    def f(fig, ctx):
        t = tl
        P = ctx['P']
        # 1) les bulles des abysses montent autour de lui pendant qu'il se ramasse
        if 60 <= t <= 700:
            for j, (x0, sp, r, ph) in enumerate(((44, 34, 1.6, 0.0), (58, 40, 1.1, 0.35), (92, 36, 1.4, 0.15), (100, 44, 1.0, 0.55),
                                                  (72, 30, 1.2, 0.7), (36, 42, 0.9, 0.85), (84, 46, 0.8, 0.45))):
                tt = (t - 60) / 1000.0 - ph * 0.25
                if 0 < tt < 0.62:
                    y = GR - 4 - sp * tt * 2.2
                    x = x0 + 1.6 * math.sin(tt * 14 + j) + (P['shift'] if t > 430 else 0)
                    fig.fx_front.append(bubble(fig, x, y, r * (0.6 + 0.6 * min(1, tt * 4)), op=min(1, (0.62 - tt) * 5, tt * 10)))
        # 2) il fonce : le ruban d'eau
        dash_ribbon(fig, back_pts, env(t, 400, 440, 480, 580))
        # 3) les trois coups : une gerbe à chaque coup, de plus en plus grosse ; la traînée de la pointe
        if len(path) >= 2:
            for th_, _ in SP_HITS:
                kk = env(t, th_ - 50, th_ - 15, th_, th_ + 30)
                if kk > 0:
                    fig.fx_back.append(stream(fig, path + [ctx['tip']], 0.5, 3.2 * kk + 0.4, op=min(1, 3 * kk)))
        for i, (th_, big) in enumerate(SP_HITS):
            tau = (t - th_) / 1000.0
            if 0 <= tau < 0.5:
                key = 'h%d' % i
                if key not in SPH:
                    SPH[key] = ctx['tip']
                X, Y = SPH[key]
                splash_hit(fig, X, Y, tau * (1.3 if i < 2 else 1.0), big, seed=i)
        # 4) le jet d'eau qui le lance en l'air, puis l'eau qui retombe
        if 860 <= t <= 1250:
            k = env(t, 860, 900, 960, 1200)
            fx_ = XS + 71
            top = ctx['feet'][0][1] - 1 if t < 1000 else GR - 30 * k
            H = GR - top
            if H > 2 and k > 0:
                w0 = 14 * k + 3
                pts = [(fx_ - 10, GR + 0.4), (fx_ - 9, GR - H * 0.35), (fx_ - 3, GR - H * 0.7), (fx_ + 1, top)]
                fig.fx_back.append(stream(fig, pts, w0, 5.0 * k + 1, op=min(1, 2 * k)))
                fig.fx_back.append(foam(fig, fx_ + 1, top + 1, 3.6 * k, op=k, seed=3))
                fig.fx_front.append(mound(fig, fx_ - 8, 5 * k, 22, op=min(1, 2 * k)))
                for j, (ang, L, bd) in enumerate(((-150, 14, -40), (-30, 14, 40), (-120, 10, -30))):
                    fig.fx_front.append(sheet(fig, (fx_ - 10 + 6 * j, GR), ang, L * k, bd, 3.6, op=min(1, 2 * k)))
        # 5) au plus haut : l'eau s'enroule en volutes devant la pointe, des bulles
        ev = env(t, 980, 1030, 1110, 1160)
        if ev > 0:
            T_ = ctx['tip']
            C = (T_[0] + 8, T_[1] - 1)
            rot_ = (t - 980) * 0.9
            fig.fx_back.append(curl(fig, C, 13 * ev, 140 + rot_, 320, 4.4 * ev + 0.6, op=ev))
            fig.fx_front.append(curl(fig, (C[0] + 1, C[1] + 3), 8.5 * ev, 320 + rot_ * 1.3, 280, 3.2 * ev + 0.5, op=ev, cw=True, light=True))
            for j, (dx, dy, r) in enumerate(((-6, -14, 1.6), (24, 5, 1.4), (17, -17, 1.0), (-11, 9, 1.0))):
                fig.fx_front.append(bubble(fig, T_[0] + dx, T_[1] + dy - 6 * (t - 980) / 180.0, r, op=ev))
        # 6) il PIQUE en plongeant : explosion d'eau (écume, couronne de nappes, bulles, gouttes), puis pluie et flaque
        tb = (t - SP_PLUNGE) / 1000.0
        if tb >= 0:
            if 'b' not in SPH:
                SPH['b'] = (ctx['tip'][0] + 3, ctx['tip'][1])
            X, Y = SPH['b']
            e = env(tb, 0, 0.03, 0.22, 0.5)
            if e > 0:
                for j, (ang, L, bd, w) in enumerate(((-80, 30, -40, 6.0), (-136, 32, -56, 6.2), (170, 26, -44, 5.4),
                                                     (-30, 24, 46, 5.0), (25, 20, 40, 4.4), (115, 18, -30, 4.0))):
                    L_ = L * (0.4 + 0.6 * min(1, tb / 0.1)) * (1 + 0.25 * tb)
                    (fig.fx_back if j in (0, 1, 3) else fig.fx_front).append(
                        sheet(fig, (X, Y), ang, L_ * (0.5 + 0.5 * e), bd, w * (0.75 + 0.25 * e), op=0.5 * e ** 1.5,
                              tail=min(0.25, max(0, tb - 0.2) * 1.2)))
            pe = env(tb, 0, 0.02, 0.16, 0.36)
            if pe > 0:
                fig.fx_front.append(foam(fig, X + 1, Y, 8.5 * pe + 1.5, op=pe, seed=2))
                fig.fx_front.append(foam(fig, X + 7, Y + 4, 4.2 * pe + 0.6, op=pe, seed=1))
            for j, (dx, dy, r) in enumerate(((-16, -12, 2.4), (14, -16, 1.8), (20, 8, 1.6), (-12, 12, 1.2), (4, -22, 1.2),
                                             (26, -6, 1.0))):
                tt = tb - 0.02 * j
                if 0 < tt < 0.7:
                    fig.fx_front.append(bubble(fig, X + dx * (1 + tt), Y + dy * (1 + tt) - 30 * tt, r * (0.6 + 0.6 * min(1, tt * 6)),
                                               op=min(1, (0.7 - tt) * 4)))
            for j, (vx, vy) in enumerate(((70, -120), (110, -60), (40, -150), (-30, -130), (130, -20), (-70, -90), (90, -100),
                                          (10, -170), (150, -80), (-50, -60))):
                if tb < 0.95:
                    x, y = ballistic((X + 2, Y), (vx, vy), 300, tb)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 300 * tb, 1.2 if j % 3 == 0 else 0.9, op=min(1, (0.95 - tb) * 4)))
            # la pluie qui retombe en désordre, puis la flaque sous l'ennemi
            RAIN = [(-0.9, 0.0, -30, 0.18), (0.8, -0.2, 40, 0.2), (-0.5, -0.4, -15, 0.24), (0.3, -0.5, 20, 0.22),
                    (1.0, -0.1, 50, 0.27), (-1.1, -0.3, -45, 0.3), (0.6, -0.6, 25, 0.33), (-0.2, -0.2, -10, 0.29)]
            for j, (sx, sy, vx, st) in enumerate(RAIN):
                tt = tb - st
                if 0 < tt < 0.6:
                    x, y = ballistic((X + sx * 16, Y - 22 + sy * 14), (vx, -30), 340, tt)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, -30 + 340 * tt, 1.15 if j % 3 == 0 else 0.9, op=min(1, (0.6 - tt) * 6)))
            pud = env(tb, 0.32, 0.46, 0.66, 0.9)
            if pud > 0:
                fig.fx_front.append(mound(fig, X + 2, 3.6 * pud, 26, op=pud, foamy=0.7))
                fig.fx_front.append(foam(fig, X - 10, GR - 1.2, 1.6 * pud, op=pud, seed=4))
                fig.fx_front.append(foam(fig, X + 12, GR - 1.0, 1.3 * pud, op=pud, seed=5))
        # 7) il retombe chez lui dans une petite gerbe
        if 1690 <= t <= 2060:
            landing(fig, 66, (t - 1690) / 370.0, 0.9)
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
    glow = Image.new('RGBA', (w, h))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.12))
    im.alpha_composite(glow)
    return im


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous lui : elle suit ses bonds et pâlit quand il est en l'air."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    lift = max(0.0, -P['drop'])
    s = max(0.35, 1 - lift / 40)
    cx = (70 + P['shift'] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 34 * k * s, fy - 2.6 * k * s, cx + 34 * k * s, fy + 2.6 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : garde ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.5)]
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
    if act:
        if tl < 300:
            HIT.clear()
            SPH.clear()
        path, back = [], []
        for dt in (0.12, 0.08, 0.04):
            if T - dt >= t0:
                Pp, _ = pose_at(T - dt, act, t0)
                c = K.build(pose=Pp).ctx
                path.append(c['tip'])
                back.append((c['pelvis'][0] - 10, c['pelvis'][1] + 6))
        P_now = K.build(pose=P).ctx
        back.append((P_now['pelvis'][0] - 10, P_now['pelvis'][1] + 6))
        fx = [fx_attack(tl, path, back) if act == 'attack' else fx_special(tl, path, back)]
    fig = K.build(ow=ow, pose=P, fx=fx, frame=view)
    if not all(fig.ctx['reach']):
        print('  ! main loin de la hampe à %.2f s (%s, %d ms) : %s' % (T, act, tl, fig.ctx['reach']))
    return fig.svg(), P


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
    subprocess.run(['node', os.path.join(HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.3, a_s + 0.48, a_s + 0.54, a_s + 0.6, a_s + 0.75, a_s + 0.82, a_s + 0.97,
                            s_s + 0.3, s_s + 0.46, s_s + 0.62, s_s + 0.77, s_s + 0.86, s_s + 0.95, s_s + 1.05,
                            s_s + 1.16, s_s + 1.25, s_s + 1.45, s_s + 1.6, s_s + 1.75]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('HP_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P))
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
