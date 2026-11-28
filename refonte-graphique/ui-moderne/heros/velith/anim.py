# Velith vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/velith/build.py) —
# respiration, attaque de base « Revers de griffes », attaque spéciale « Rugissement du glacier » — dans le style lisse
# de l'interface, comme Kael (../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/velith/anim.py                 # → anim.mp4 + anim.gif (sortie/ui/vecto/velith/)
#   python3 refonte-graphique/ui-moderne/heros/velith/anim.py --planche [t…]  # une planche d'instants clés (contrôle)
#
# Méthode : le dessin (velith.py) est fait de morceaux posés par un squelette (le haut du corps qui respire et se penche
# depuis les hanches, la tête, la gueule, le bras proche placé par cinématique inverse depuis le poing qui tient la
# hache, le bras lointain depuis son poignet, la main qui s'ouvre en griffe). Les poses clés reprennent celles du pixel
# art (préparations lourdes, coups très courts, impacts tenus, retours lents) et sont reliées par des courbes douces
# sans dépassement, à 24 images par seconde. Les effets de neige et de glace (bouffées, buée en volutes, croissant de
# neige, éclats et pics de cristal taillés) sont dessinés dans le même style : dégradés, un contour, aucun flou SVG,
# jamais de rayons droits répétés.
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
import velith as V  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import hrand  # noqa: E402

ROOT = V.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'velith')
TMP = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-velith/_images'
FPS = 24
VIEW = (-40, -58, 320, 180)          # la scène de la vidéo, en pixels du dessin (16/9) : la hache levée du saut, les pics
VW, VH = 1280, 720
GR = V.GRD
SINK = '#5a60a0'                     # le contour de la neige et de la buée
IINK = '#1a2a66'                     # le contour de la glace
ICE = V.ICE

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


PAIRS = {'head': ('hx', 'hy'), 'nG': ('ngx', 'ngy'), 'fW': ('fwx', 'fwy')}
SCAL = ['breath', 'crouch', 'lean', 'shift', 'lift', 'feet_up', 'tilt', 'jaw', 'axe', 'fang', 'claw', 'spread', 'ffront',
        'freach', 'nreach', 'pg']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    R = V.REST
    d = {n: R[n] for n in SCAL}
    for key, (a, b) in PAIRS.items():
        d[a], d[b] = R[key]
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


# ======================================================================== les actions (poses clés)
# Repère du dessin : l'épaule lointaine (98, 52), le poing proche sur le manche (25.8, 22), le poignet lointain au
# repos (106.4, 79.2). fang : la main lointaine pointe dans cette direction (degrés, y vers le bas : 90 = en bas).

# 2) « Revers de griffes » (pixel : ATTAQUE). Il se ramasse et se penche en arrière, la griffe levée haut au-dessus de
# l'épaule (la hache remonte en contrepoids, il souffle par le nez), puis se jette en avant et balaie de haut en bas,
# main grande ouverte : un croissant de neige suit la griffe ; à l'impact (tenu), une gerbe de neige et d'éclats de
# glace jaillit devant lui ; le bras retombe lourdement, le poing se referme, il revient en garde.
ATTACK = [
    (0, {}),
    (110, dict(crouch=1, lean=-1, head=(0, 0.8), fW=(113, 50), claw=1, fang=-62, pg=0.5)),
    (300, dict(crouch=2, lean=-3, head=(-1, -0.6), tilt=-3, nG=(24.6, 20.2), fW=(106, 23), claw=1, fang=-96, spread=1.6,
               pg=1)),
    (370, dict(crouch=2.2, lean=-3.3, head=(-1.1, -0.8), tilt=-3.5, nG=(24.4, 19.8), fW=(105.6, 22), claw=1, fang=-98,
               spread=1.7, pg=1)),
    (420, dict(crouch=1, lean=3, head=(1, 0), tilt=1, nG=(25.8, 21.2), fW=(129, 42), claw=1, fang=-28, spread=1.3,
               freach=1.12, pg=0)),
    (470, dict(crouch=2, lean=6, head=(1, 1), tilt=3, nG=(26.6, 22), fW=(129, 72), claw=1, fang=28, spread=1.1,
               freach=1.18, pg=-1)),
    (520, dict(crouch=3, lean=7, head=(1.2, 1.2), tilt=4, nG=(27, 22.6), fW=(125, 82), claw=1, fang=44, spread=1.0,
               freach=1.15, pg=-1.5)),
    (670, dict(crouch=3, lean=6.6, head=(1.1, 1.2), tilt=3.5, nG=(27, 22.6), fW=(123, 84), claw=1, fang=50, freach=1.12,
               pg=-1)),
    (780, dict(crouch=2, lean=5, head=(1, 1), tilt=2, nG=(26.6, 22.4), fW=(117, 88), claw=1, fang=70, freach=1.08)),
    (900, dict(crouch=1, lean=3, head=(0.4, 0.4), nG=(26.2, 22.2), fW=(110, 83), claw=0, fang=88, pg=0.8)),
    (1030, dict(crouch=0.8, lean=1, fW=(107.4, 80.6), pg=0.4)),
    (1180, {}),
]
ATTACK_HIT = 520

# 3) « Rugissement du glacier » (pixel : SPECIALE). Il se frappe la poitrine deux fois du poing (la neige saute du col),
# rugit gueule grande ouverte (bourrasque de buée glacée en volutes), se ramasse, bondit les deux bras levés (la hache
# en haut, la griffe ouverte), retombe en frappant le sol des deux bras : le pommeau de fer d'un côté, le poing de
# l'autre. Arrêt sur l'impact. L'onde court dans le sol gelé vers l'ennemi : une rangée irrégulière de pics de glace
# taillés jaillit, de plus en plus hauts, jusqu'à un gros bouquet de cristaux sous l'ennemi ; puis les pics se brisent
# en éclats et en bouffées de neige pendant qu'il se redresse.
POMMEL = (3.8, 23.6)                                  # le pommeau, depuis le point de prise (hache droite)
SLAM = dict(crouch=8.6, lean=1.5, shift=4, head=(1, 1), tilt=3, nG=(27, 116 - POMMEL[1] - 1.0), fW=(124, 100.5), claw=0,
            fang=84, freach=1.42, nreach=1.17)
SPECIAL = [
    (0, {}),
    (170, dict(crouch=1, breath=1.6, head=(0, -0.8), nG=(25.8, 21), ffront=1, fW=(108, 64), claw=0, fang=150)),
    (250, dict(crouch=1.2, breath=1.6, head=(0, 0), nG=(25.8, 21), ffront=1, fW=(96.5, 66), claw=0, fang=184)),
    (340, dict(crouch=1, breath=1.8, head=(0, -0.8), nG=(25.8, 19.6), ffront=1, fW=(109, 61), claw=0, fang=150)),
    (420, dict(crouch=1.2, breath=1.8, head=(0, 0), nG=(25.8, 20), ffront=1, fW=(96.5, 67), claw=0, fang=186)),
    (470, dict(crouch=0.6, breath=2, head=(0.6, -1.2), tilt=-5, jaw=1.2, nG=(24.8, 18), ffront=1, fW=(106, 72), claw=0,
               fang=120)),
    (520, dict(crouch=0, breath=2, head=(1, -2), tilt=-9, jaw=2, nG=(24.6, 17.4), ffront=0, fW=(108, 75), fang=96)),
    (760, dict(crouch=0, breath=2, head=(1, -2.2), tilt=-10, jaw=2.1, nG=(24.4, 17.2), fW=(108.4, 75.6), fang=94)),
    (920, dict(crouch=8, lean=-2, head=(0, 1), tilt=2, jaw=0.3, nG=(27, 27), fW=(107, 84), fang=90, pg=1.5)),
    (980, dict(crouch=-1.5, lift=12, head=(0, 0), tilt=-2, nG=(35.8, -13.4), fW=(104, 18), claw=1, fang=-88, spread=1.5,
               pg=-1.5)),
    (1100, dict(crouch=0, lift=22, feet_up=5, head=(0, -1), tilt=-3, nG=(37.8, -27.4), fW=(106, 3), claw=1, fang=-92,
                spread=1.7, pg=-2)),
    (1150, dict(crouch=0, lift=9, shift=3, feet_up=2, head=(1, 0), tilt=2, nG=(11.8, 43.6), fW=(122, 67), claw=1,
                fang=40, freach=1.2, pg=1)),
    (1185, SLAM),
    (1400, dict(SLAM, crouch=7.8)),
    (1620, dict(SLAM, crouch=7.4, head=(1, 0.4), jaw=1)),
    (1700, dict(SLAM, crouch=7.2, head=(1, -0.8), tilt=-4, jaw=2)),
    (1940, dict(SLAM, crouch=6.6, head=(1, -1), tilt=-5, jaw=2)),
    (2040, dict(crouch=5, lean=1, shift=3.2, head=(1, 0), jaw=1, nG=(19.8, 66), fW=(119, 88), claw=0, freach=1.15)),
    (2150, dict(crouch=3, shift=2, head=(0.4, 0), jaw=0, nG=(18.8, 45.6), fW=(112, 82))),
    (2270, dict(crouch=1, shift=0.8, nG=(23.8, 25.6), fW=(107, 80))),
    (2410, dict(crouch=0.3, shift=0.2)),
    (2560, {}),
]
SP_HIT = 1185
WAVE0 = 1400                                         # l'onde part dans le sol gelé


# ======================================================================== la respiration (en boucle, 2 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la lame de glace de la hache s'éclaire lentement (facettes qui blanchissent, halo de froid serré),
    puis s'éteint. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(givre=0.5 - 0.5 * math.cos(u))


def idle(T):
    """Il gonfle le torse, la tête suit avec un temps de retard, le poing lointain se balance (encore plus en retard) ;
    les mèches qui pendent ondulent, la crête du crâne frémit ; à l'expiration, une bouffée de buée sort de la gueule."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, hy=-0.6 * (0.5 - 0.5 * math.cos(u - 0.6)), tilt=-0.6 * math.sin(u - 0.9),
                fwx=0.7 * math.sin(u - 1.7), fwy=-0.5 * (0.5 - 0.5 * math.cos(u - 1.4)), crouch=0.35 * (0.5 - 0.5 * math.cos(u - 2.4)),
                pg=0.5 * math.sin(u + 0.4))


def pose_at(T, action=None, t0=0.0):
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
    idl = idle(T)
    src = act or keyed([(0, {})], 0)
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    out = {n: P[n] for n in SCAL}
    for key, (a, b) in PAIRS.items():
        out[key] = (P[a], P[b])
    out['breath'] = P['breath']
    out['ph'] = 2 * math.pi * T * 2 / IDLE_T       # la fourrure : 2 ondes par boucle (0,55 par s avant le 27/11)
    out['givre'] = w * signe(T)['givre']           # le signe du repos : la lame de glace s'éclaire (anim.signe)
    out['sway'] = 1.0 + (1.2 if act else 0.0)
    out['crest'] = max(0.0, math.sin(2 * math.pi * T / IDLE_T - 1.2)) * w
    out['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return out, tl


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def outlined(items, ink=SINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in items if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in items)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


SNOW = [(0, '#ffffff'), (0.55, '#eef3fc'), (1, '#c2cbea')]
MIST = [(0, '#f6fbff'), (0.55, '#d4e6f6', 0.95), (1, '#a8c4e8', 0.9)]


def puff(fig, cx, cy, r, op=1.0, kind='snow', seed=0):
    """Une bouffée de neige (ou de buée) : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = lambda k: 0.85 + 0.3 * hrand(seed, k)
    balls = [(cx, cy, r), (cx + 0.78 * r, cy + 0.28 * r, 0.72 * r * j(1)), (cx - 0.8 * r, cy + 0.32 * r, 0.66 * r * j(2)),
             (cx + 0.12 * r, cy - 0.58 * r, 0.6 * r * j(3))]
    stops = SNOW if kind == 'snow' else MIST
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    ink = SINK if kind == 'snow' else '#5a78b0'
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def wisp(fig, p0, p1, p2, p3, w, op=1.0):
    """Un filet de buée glacée qui file en ondulant (un ruban courbe qui s'affine, le bout à peine recourbé)."""
    from atelier import bez
    pts = bez(p0, p1, p2, p3, 18)
    n = len(pts) - 1
    sh = ribbon(pts, [w * 0.5] + [w * (1 - 0.75 * i / n) * (1 + 0.25 * math.sin(math.pi * i / n)) for i in range(1, n)] + [0.12])
    gr = g_lin(fig, p0, p3, [(0, '#f6fbff', 0.95), (0.6, '#d4e6f6', 0.85), (1, '#b8d0ec', 0.6)])
    return outlined([(sh, gr, 1)], ink='#5a78b0', w=1.0, op=op)


def flake(fig, x, y, s=1.0, op=1.0, rot=0.0):
    """Un flocon : une petite étoile à quatre branches inégales (pas un rayon régulier), blanche."""
    pts = []
    for i in range(8):
        a = math.radians(rot + i * 45)
        rr = s * (1.0 if i % 2 == 0 else 0.35) * (1.0 if i not in (2,) else 0.8)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    sh = sm(pts, sharp=tuple(range(0, 8, 2)), t=0.6)
    return outlined([(sh, '#ffffff', 1)], ink=SINK, w=0.7, op=op)


def shard(fig, c, r, rot, seed=0, op=1.0):
    """Un éclat de glace taillé : un losange irrégulier, une face claire (vers la lumière) et une face sombre, une arête
    très claire."""
    if r < 0.3 or op <= 0.02:
        return ''
    a = [rot + 0, rot + 95 + 25 * hrand(seed, 1), rot + 180 + 20 * hrand(seed, 2), rot + 265 + 20 * hrand(seed, 3)]
    L = [r * 1.3, r * (0.5 + 0.25 * hrand(seed, 4)), r * (0.9 + 0.3 * hrand(seed, 5)), r * (0.45 + 0.2 * hrand(seed, 6))]
    pts = [(c[0] + L[i] * math.cos(math.radians(a[i])), c[1] + L[i] * math.sin(math.radians(a[i]))) for i in range(4)]
    body = sm(pts, sharp=(0, 1, 2, 3), t=0.3)
    light = sm([pts[0], pts[1], pts[2], c], sharp=(0, 1, 2, 3), t=0.3)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, ICE.light), (1, ICE.shadow)])
    ridge = ribbon([pts[2], c, pts[0]], [0.05, 0.35 * r / 2 + 0.15, 0.05])
    return outlined([(body, gr, 1), (light, ICE.hi, 0.55), (ridge, ICE.glint, 0.9)], ink=IINK, w=0.9, op=op)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def snow_trail(fig, C, R, a0, a1, w, op=1.0):
    """Le croissant de neige qui suit la griffe (il s'efface vers l'arrière)."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R, a0, a1, w)
    core = arc_band(C, R - w * 0.12, a0 + (a1 - a0) * 0.3, a1, w * 0.45)
    g1 = g_lin(fig, pa, pb, [(0, '#bfe6f6', 0), (0.5, '#d8f0fa', 0.7 * op), (1, '#effaff', 0.95 * op)])
    g2 = g_lin(fig, pa, pb, [(0, '#ffffff', 0), (1, '#ffffff', op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, core.d(), g2)


def burst(fig, c, r, op=1.0, seed=0, facing=0.0):
    """L'éclat blanc d'un impact : une étoile molle à lobes inégaux (pas de rayons réguliers), cœur blanc."""
    if r < 0.4 or op <= 0.02:
        return ''
    pts = []
    n = 7
    sharp = []
    for i in range(2 * n):
        a = math.radians(facing + i * 180 / n + 10 * (hrand(seed, i) - 0.5))
        rr = r * ((0.75 + 0.5 * hrand(seed, i + 9)) if i % 2 == 0 else 0.42)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        if i % 2 == 0:
            sharp.append(i)
    sh = sm(pts, sharp=tuple(sharp), t=0.8)
    inner = sh.scale(0.55, 0.55, c[0], c[1])
    gr = fig.rad(c[0], c[1], r, r, [(0, '#ffffff'), (0.5, '#eef6ff'), (1, '#b6d6f4')])
    return outlined([(sh, gr, 1), (inner, '#ffffff', 1)], ink=SINK, w=1.0, op=op)


def spike(fig, bx, h, w, lean, seed, grow=1.0, op=1.0):
    """Un pic de glace taillé qui sort du sol : base large, pointe penchée, deux faces séparées par une arête (la face
    claire à droite, vers la lumière), un éclat très clair sur l'arête."""
    hh = max(1.5, h * grow)
    g = GR + 0.6
    tip = (bx + lean * grow, g - hh)
    q1 = 0.38 + 0.12 * hrand(seed, 1)
    q2 = 0.5 + 0.16 * hrand(seed, 2)
    L = (bx - w / 2, g)
    R = (bx + w / 2, g)
    ml = (bx - w * 0.44 + lean * 0.25, g - hh * q1)
    mr = (bx + w * 0.4 + lean * 0.45, g - hh * q2)
    foot = (bx + w * (0.04 + 0.1 * hrand(seed, 3)), g)
    body = sm([L, ml, tip, mr, R], sharp=(0, 1, 2, 3, 4), t=0.3)
    right = sm([foot, tip, mr, R], sharp=(0, 1, 2, 3), t=0.3)
    gl = g_lin(fig, tip, L, [(0, ICE.base), (1, ICE.shadow)])
    gr = g_lin(fig, tip, R, [(0, ICE.hi), (0.5, ICE.light), (1, ICE.base)])
    ridge = ribbon([foot, ((foot[0] + tip[0]) / 2, (foot[1] + tip[1]) / 2), tip], [0.2, 0.7, 0.05])
    glint = ribbon([(tip[0] + (mr[0] - tip[0]) * 0.15, tip[1] + (mr[1] - tip[1]) * 0.15),
                    (tip[0] + (mr[0] - tip[0]) * 0.55, tip[1] + (mr[1] - tip[1]) * 0.55)], [0.1, 0.5])
    return outlined([(body, gl, 1), (right, gr, 1), (ridge, ICE.glint, 0.85), (glint, '#ffffff', 0.9)], ink=IINK, w=1.0, op=op)


def crack(fig, x0, x1, op=1.0, seed=2):
    """La fissure de l'onde dans le sol gelé : une ligne brisée bleu nuit (pas droite), bord clair dessus."""
    if x1 - x0 < 2 or op <= 0.02:
        return ''
    pts = []
    x = x0
    i = 0
    while x < x1:
        pts.append((x, GR + 0.5 + 0.9 * hrand(seed, i)))
        x += 3 + 4 * hrand(seed, i + 50)
        i += 1
    pts.append((x1, GR + 0.6))
    if len(pts) < 3:
        return ''
    core = ribbon(pts, [0.2] + [1.0 + 0.5 * hrand(seed, k + 9) for k in range(len(pts) - 2)] + [0.1])
    hi = ribbon([(p[0], p[1] - 0.8) for p in pts], [0.1] + [0.5] * (len(pts) - 2) + [0.05])
    return '<g opacity="%g"><path d="%s" fill="#26386e"/><path d="%s" fill="#b4d4f2" opacity="0.8"/></g>' % (op, core.d(), hi.d())


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


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 2


# (direction du vol, vitesse, taille, graine) ; chaque éclat tourne sur lui-même : jamais alignés en rayons
SHARDS = [(-8, 1.0, 3.2, 0), (20, 1.25, 2.6, 1), (48, 0.9, 2.2, 2), (-36, 0.8, 2.0, 3), (74, 0.7, 1.5, 4),
          (5, 1.5, 1.3, 5), (31, 0.6, 2.8, 6)]
TUMBLE = [35, -50, 80, 140, -20, 60, -95]
HIT = {}


def mouth_pt(ctx):
    return ctx['mouth']


def fx_breath_idle(T):
    """Au repos, à l'expiration : une petite bouffée de buée sort de la gueule et monte en se défaisant."""
    k = ((T % IDLE_T) - 1.575) / 1.35
    def f(fig, ctx):
        if not (0 <= k <= 1):
            return
        m = mouth_pt(ctx)
        o = env(k, 0, 0.2, 0.55, 1)
        fig.fx_front.append(puff(fig, m[0] + 2 + 9 * k, m[1] - 1 - 7 * k, 1.3 + 1.6 * k, op=0.85 * o, kind='mist', seed=1))
        if k > 0.3:
            kk = (k - 0.3) / 0.7
            fig.fx_front.append(puff(fig, m[0] + 6 + 10 * kk, m[1] - 5 - 7 * kk, 1.0 + 1.0 * kk, op=0.7 * o, kind='mist', seed=2))
    return f


def fx_flakes(T):
    """Deux ou trois flocons qui tombent en se balançant, derrière lui."""
    def f(fig, ctx):
        for (x0, y0, vy, ph) in ((8, -6, 9.0, 0.0), (114, 14, 11.0, 2.0), (54, -16, 10.0, 4.0)):
            t = (T / IDLE_T + ph * 0.13) % 1.0
            x = x0 + 3.0 * math.sin(2 * math.pi * t + ph)
            y = y0 + vy * t * 4.4
            o = env(t, 0, 0.15, 0.8, 1)
            fig.fx_back.append(flake(fig, x, y, 1.3, op=o, rot=40 * t + ph * 30))
    return f


def fx_attack(tl):
    def f(fig, ctx):
        S = ctx['fS']
        tips = ctx.get('ftips') or [ctx['fW']]
        tip = max(tips, key=lambda p: p[0])
        # le souffle par le nez quand il arme (deux bouffées qui partent vers l'avant et le bas)
        o = env(tl, 230, 300, 420, 560)
        if o > 0:
            m = mouth_pt(ctx)
            k = (tl - 230) / 330
            fig.fx_front.append(puff(fig, m[0] + 2 + 7 * k, m[1] + 0.5 + 2 * k, 1.4 + 1.2 * k, op=o * 0.9, kind='mist', seed=3))
            fig.fx_front.append(puff(fig, m[0] + 5 + 10 * k, m[1] + 2 + 3 * k, 1.0 + 1.0 * k, op=o * 0.7, kind='mist', seed=4))
        # le croissant de neige derrière la griffe qui balaie (de haut en bas, devant lui)
        if 372 <= tl <= 640:
            a1 = math.degrees(math.atan2(tip[1] - S[1], tip[0] - S[0]))
            R = math.dist(S, tip) + 2
            tr = min(1.0, (tl - 372) / 100)
            a0 = max(-100, a1 - 95 * tr)
            op = 1.0 if tl < 540 else max(0.0, 1 - (tl - 540) / 100)
            w = 9 if tl < 520 else 9 * op
            fig.fx_back.append(snow_trail(fig, S, R, a0, a1, w, op))
        # l'impact : la gerbe de neige et de glace devant les griffes
        if tl >= ATTACK_HIT - 5:
            if 'c' not in HIT:
                HIT['c'] = (tip[0] + 4, tip[1] - 1)
            c = HIT['c']
            t = (tl - ATTACK_HIT) / 1000
            fig.fx_front.append(burst(fig, (c[0] + 2, c[1]), 7.5 * env(tl, ATTACK_HIT - 5, ATTACK_HIT + 30, ATTACK_HIT + 90, ATTACK_HIT + 200),
                                      op=1.0, seed=4, facing=10))
            for i, (dx, dy, r, d0) in enumerate(((-4, 7, 3.2, 0), (7, -7, 2.6, 30), (11, 5, 2.2, 60), (4, 2, 3.6, 10))):
                ag = max(0.0, (tl - ATTACK_HIT - d0) / 600)
                if 0 < ag < 1:
                    fig.fx_front.append(puff(fig, c[0] + dx * (1 + 1.4 * ag), c[1] + dy * (1 + 0.8 * ag) + 4 * ag, r * (0.7 + 0.8 * ag),
                                             op=1 - ag ** 1.6, seed=10 + i))
            for i, (a, sp, r, sd) in enumerate(SHARDS):
                ag = (tl - ATTACK_HIT) / 650
                if 0 <= ag < 1:
                    v = (math.cos(math.radians(-a)) * 70 * sp, math.sin(math.radians(-a)) * 70 * sp)
                    p = ballistic(c, v, 160, t)
                    if p[1] < GR - 1:
                        fig.fx_front.append(shard(fig, p, r, TUMBLE[i] * t * 4 + a, seed=sd, op=1 - ag ** 2))
            # quelques flocons qui retombent
            for i in range(4):
                ag = (tl - ATTACK_HIT - 150 - 40 * i) / 500
                if 0 < ag < 1:
                    fig.fx_front.append(flake(fig, c[0] + 6 + 5 * i + 2 * math.sin(ag * 6 + i), c[1] + 6 + 16 * ag, 1.1, op=1 - ag, rot=60 * ag))
    return f


def spikes_at(fig, tw, x0):
    """L'onde de pics de glace (tw : ms depuis le départ de l'onde ; x0 : le premier pic)."""
    SPIKES = [(0, 9, 8, 2, 0), (5, 15, 9, -1, 1), (17, 12, 9, 3, 2), (26, 22, 11, 1, 3), (31, 13, 8, 5, 4),
              (36, 27, 12, -2, 5), (50, 18, 10, 2, 6), (57, 31, 12, 4, 7), (64, 19, 9, -4, 8), (76, 40, 14, 2, 9),
              (83, 25, 10, 7, 10), (88, 16, 8, -3, 15), (93, 44, 14, -6, 12), (101, 62, 19, 4, 11), (110, 48, 15, 9, 13),
              (118, 24, 10, 6, 14)]
    FR = 80.0                                   # une « image » du pixel art (l'onde avance de 36 px par image)
    k = tw / FR
    reach = (k + 1) * 36
    back, front = [], []
    if 0 <= k <= 7.5:
        back.append(crack(fig, x0 - 8, min(x0 + reach, x0 + 124), op=env(k, 0, 0.2, 6.5, 7.5)))
    for (dx, h, w, lean, sd) in sorted(SPIKES, key=lambda s: -s[1]):
        age = k - dx / 36
        if age < -0.2:
            continue
        bx = x0 + dx
        brk = 5.0 + dx / 80.0
        if k < brk:
            a = max(0.0, age + 0.2)
            grow = min(1.12, a / 0.8 * 1.12) if a < 0.8 else 1.12 - 0.12 * min(1.0, (a - 0.8) / 0.8)
            back.append(spike(fig, bx, h, w, lean, sd, grow))
            if a < 1.2:
                front.append(puff(fig, bx - 1, GR - 2, 1.4 + w * 0.22, op=1 - a / 1.2, seed=sd))
        else:
            b = k - brk
            if b < 0.6:
                back.append(spike(fig, bx, h, w, lean, sd, 1.0 - 0.6 * b / 0.6, op=1 - b / 0.6 * 0.4))
            if b < 2.2:
                front.append(puff(fig, bx, GR - h * 0.25 * (1 - b / 2.2) - 2, (1.6 + w * 0.25) * (0.8 + 0.4 * b), op=1 - b / 2.2, seed=sd + 3))
                for j, (ox, vy, rr, aa) in enumerate(((-3, -26, 0.32, 60), (3, -30, 0.28, -40), (1, -36, 0.22, 130))):
                    t = b * FR / 1000
                    p = ballistic((bx + ox + lean * 0.5, GR - h * 0.55), (ox * 9, vy * 1.4), 200, t)
                    if p[1] < GR:
                        front.append(shard(fig, p, max(0.8, h * rr * 0.35), aa + sd * 17 + 300 * t, seed=sd + j, op=1 - b / 2.2))
    # le gros bouquet frappe l'ennemi
    c = (x0 + 104, GR - 58)
    if 3.5 <= k < 6:
        q = k - 3.5
        front.append(burst(fig, c, 8.0 * env(q, 0, 0.25, 0.7, 1.4), seed=7, facing=60))
        for i, (a, sp, r, sd) in enumerate(SHARDS):
            t = q * FR / 1000
            v = (math.cos(math.radians(-(a + 50))) * 80 * sp, math.sin(math.radians(-(a + 50))) * 80 * sp)
            p = ballistic(c, v, 150, t)
            if q > 0.1 and p[1] < GR:
                front.append(shard(fig, p, r * 0.9, a + TUMBLE[i] * t * 5, seed=sd, op=max(0.0, 1 - q / 2.5)))
        if q > 0.6:
            qq = (q - 0.6) / 1.9
            front.append(puff(fig, c[0] + 2, c[1] + 3 * qq, 4.5 + 3 * qq, op=max(0.0, 1 - qq), seed=8))
    return back, front


def fx_special(tl):
    def f(fig, ctx):
        m = mouth_pt(ctx)
        # les coups sur la poitrine : la neige saute du col
        for i, t0 in enumerate((250, 420)):
            k = (tl - t0) / 380
            if 0 <= k < 1:
                c = ctx['chest']
                fig.fx_front.append(puff(fig, c[0] + 3 + 4 * k, c[1] - 6 - 6 * k, 2.6 + 1.2 * k, op=1 - k ** 1.5, seed=20 + i))
                fig.fx_front.append(puff(fig, c[0] + 9 + 7 * k, c[1] - 11 - 7 * k, 1.4 + 0.8 * k, op=1 - k, seed=22 + i))
                fig.fx_front.append(flake(fig, c[0] - 5 - 3 * k, c[1] - 12 + 6 * k, 1.1, op=1 - k, rot=50 * k))
        # le rugissement : une bourrasque de buée glacée en volutes et en bouffées (aucun rayon)
        o = env(tl, 490, 560, 820, 960)
        if o > 0:
            k = min(1.0, (tl - 490) / 420)
            L = 18 + 22 * k
            wv = 3 * math.sin(tl / 60)
            fig.fx_front.append(wisp(fig, (m[0] + 1, m[1] - 1), (m[0] + L * 0.35, m[1] - 4 + wv), (m[0] + L * 0.7, m[1] - 10 - wv),
                                     (m[0] + L, m[1] - 14 - 6 * k), 4.6, op=o))
            fig.fx_front.append(wisp(fig, (m[0] + 1, m[1] + 1.5), (m[0] + L * 0.4, m[1] + 4 - wv), (m[0] + L * 0.75, m[1] + 2 + wv),
                                     (m[0] + L * 1.1, m[1] - 2), 3.8, op=o * 0.9))
            for i, (dx, dy, r) in enumerate(((10, -2, 3.2), (24, -9, 3.0), (30, 3, 2.4), (40, -4, 2.0))):
                kk = min(1.0, k * 1.3 - i * 0.12)
                if kk > 0:
                    fig.fx_front.append(puff(fig, m[0] + dx * (0.5 + 0.8 * kk), m[1] + dy * (0.6 + 0.6 * kk), r * (0.6 + 0.6 * kk),
                                             op=o * (1 - 0.3 * kk), kind='mist', seed=30 + i))
            for i, (dx, dy) in enumerate(((22, -24), (42, -6), (14, 12), (36, 12), (50, -18))):
                fig.fx_front.append(flake(fig, m[0] + dx * (0.6 + 0.6 * k), m[1] + dy * (0.6 + 0.5 * k) + 6 * k, 1.2, op=o, rot=90 * k + i * 20))
        # le bond : la neige gicle sous les pieds
        for i, (x, r) in enumerate(((34, 4.0), (88, 3.6), (60, 2.8))):
            k = (tl - 940 - 20 * i) / 380
            if 0 <= k < 1:
                fig.fx_front.append(puff(fig, x + (x - 60) * 0.3 * k, GR - 2 - 4 * k, r * (0.8 + 0.5 * k), op=1 - k, seed=40 + i))
        # la chute : les deux bras s'abattent (deux croissants de neige)
        if 1110 <= tl <= 1300:
            op = 1.0 if tl < 1185 else max(0.0, 1 - (tl - 1185) / 115)
            Sf, Sn = ctx['fS'], ctx['nS']
            tip = ctx['fW']
            a1 = math.degrees(math.atan2(tip[1] - Sf[1], tip[0] - Sf[0]))
            fig.fx_back.append(snow_trail(fig, Sf, math.dist(Sf, tip) + 4, a1 - 85, a1, 10, op))
            G = ctx['nW']
            a2 = math.degrees(math.atan2(G[1] - Sn[1], G[0] - Sn[0]))
            fig.fx_back.append(snow_trail(fig, Sn, math.dist(Sn, G) + 6, a2 + 85, a2, 10, op))
        # l'impact au sol : éclat blanc sous le poing et sous le pommeau, neige qui jaillit, mottes qui roulent
        if tl >= SP_HIT - 5:
            if 'fist' not in HIT:
                HIT['fist'] = (ctx['fW'][0] + 4, GR - 3)
                HIT['pommel'] = (ctx['pommel'][0], GR - 2)
            fx_, px = HIT['fist'], HIT['pommel']
            b = env(tl, SP_HIT - 5, SP_HIT + 30, SP_HIT + 120, SP_HIT + 260)
            fig.fx_front.append(burst(fig, fx_, 8.0 * b, seed=11, facing=30))
            fig.fx_front.append(burst(fig, px, 5.5 * b, seed=12, facing=150))
            for i, (x, dx, r, d0) in enumerate(((fx_[0] + 6, 8, 4.4, 20), (fx_[0] - 10, -6, 3.4, 0), (px[0] - 6, -7, 3.6, 10),
                                                (px[0] + 7, 4, 2.6, 40))):
                k = (tl - SP_HIT - d0) / 700
                if 0 < k < 1:
                    fig.fx_front.append(puff(fig, x + dx * k, GR - 3 - 3 * k, r * (0.7 + 0.6 * k), op=1 - k ** 1.5, seed=50 + i))
            tw = tl - WAVE0
            if tw >= -40:
                back, front = spikes_at(fig, tw, fx_[0] + 10)
                fig.fx_back.extend(back)
                fig.fx_front.extend(front)
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
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, shift, lift, floor_y=GR):
    """L'ombre douce au sol sous lui (elle suit ses pas et pâlit quand il bondit)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 + shift - x0) * k
    s = max(0.45, 1 - lift / 40)
    ImageDraw.Draw(sh).ellipse([cx - 42 * k * s, fy - 2.8 * k * s, cx + 42 * k * s, fy + 2.8 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 4.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
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
    fx = [fx_flakes(T)]
    if act == 'attack':
        fx.append(fx_attack(tl))
    elif act == 'special':
        fx.append(fx_special(tl))
    else:
        HIT.clear()
        fx.append(fx_breath_idle(T))
    return V.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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
        moments = extra or [1.0, a_s + 0.11, a_s + 0.37, a_s + 0.45, a_s + 0.53, a_s + 0.7, a_s + 0.9,
                            s_s + 0.25, s_s + 0.42, s_s + 0.65, s_s + 0.92, s_s + 1.1, s_s + 1.16, s_s + 1.2,
                            s_s + 1.5, s_s + 1.75, s_s + 1.95, s_s + 2.2]
        HIT.clear()
        PV = tuple(map(float, os.environ['VIEWZ'].split())) if os.environ.get('VIEWZ') else VIEW
        fr = []
        for T in sorted(moments):
            fr.append(frame_svg(T, segs, view=PV))
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, PV)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, PV, P['shift'], P['lift']))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % sorted(moments)[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = sys.argv[sys.argv.index('--sortie') + 1] if '--sortie' in sys.argv else os.path.join(TMP, '..', 'planche.png')
        sheet.save(dst)
        print('planche :', dst)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    HIT.clear()
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



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : l'onde de pics de glace est UNE silhouette (cornes de glace fondues avec le bourrelet de sol
# gelé), la fente du sol une courbe lisse, les éclats des galets de glace, la buée et la neige des bouffées fondues, le
# souffle et les traînées des rubans d'un seul tenant, l'éclat de l'impact une lumière ; l'attaque garde son dessin.
import effets_pro as E  # noqa: E402

GLACE = E.pierre_de(ICE, IINK)


def _spikes_at(fig, tw, x0):
    SPIKES = [(0, 9, 8, 2, 0), (5, 15, 9, -1, 1), (17, 12, 9, 3, 2), (26, 22, 11, 1, 3), (31, 13, 8, 5, 4),
              (36, 27, 12, -2, 5), (50, 18, 10, 2, 6), (57, 31, 12, 4, 7), (64, 19, 9, -4, 8), (76, 40, 14, 2, 9),
              (83, 25, 10, 7, 10), (88, 16, 8, -3, 15), (93, 44, 14, -6, 12), (101, 62, 19, 4, 11), (110, 48, 15, 9, 13),
              (118, 24, 10, 6, 14)]
    FR = 80.0
    k = tw / FR
    reach = (k + 1) * 36
    back, front = [], []
    if 0 <= k <= 7.5:
        x1 = min(x0 + reach, x0 + 124)
        if x1 - x0 > 6:
            back.append(E.fissure(fig, [(x0 - 8, GR + 0.6), ((x0 + x1) / 2 - 4, GR + 1.1), (x1, GR + 0.6)], 3.0, 'glace',
                                  op=env(k, 0, 0.2, 6.5, 7.5), glow=0.8, pierre=GLACE))
    sp, crumbs = [], []
    for (dx, h, w, lean, sd) in SPIKES:
        age = k - dx / 36
        if age < -0.2:
            continue
        brk = 5.0 + dx / 80.0
        if k < brk:
            a = max(0.0, age + 0.2)
            grow = min(1.12, a / 0.8 * 1.12) if a < 0.8 else 1.12 - 0.12 * min(1.0, (a - 0.8) / 0.8)
            sp.append((dx, h, w * 1.1, lean * 3.0, grow))
            if a < 1.0 and sd % 3 == 0:
                front.append(E.nuage(fig, x0 + dx - 1, GR - 2.5, 2.0 + w * 0.24, 'glace', op=1 - a, seed=sd, flat=0.7))
        else:
            b = k - brk
            if b < 0.6:
                sp.append((dx, h, w * 1.1, lean * 3.0, 1.0 - 0.6 * b / 0.6))
            if b < 2.2 and sd % 2 == 0:
                front.append(E.nuage(fig, x0 + dx, GR - h * 0.25 * (1 - b / 2.2) - 2.5, (2.0 + w * 0.25) * (0.8 + 0.4 * b), 'glace',
                                     op=1 - b / 2.2, seed=sd + 3))
                for j, (ox, vy, rr) in enumerate(((-3, -26, 0.32), (3, -34, 0.24))):
                    t = b * FR / 1000
                    (px, py), _ = E.vol((x0 + dx + ox + lean * 0.5, GR - h * 0.55), (ox * 12, vy * 1.6), 260, t, drag=0.8)
                    if py < GR:
                        front.append(E.caillou(fig, px, py, max(1.0, h * rr * 0.32), 300 * t + sd * 17, seed=sd + j, op=1 - b / 2.2,
                                               hot=0.3, p='glace', pierre=GLACE))
    if sp:
        back.append(E.aiguilles(fig, x0, GR, sp, min(1.0, k / 2 + 0.3), p='glace', hot=0.5, pierre=GLACE))
    c = (x0 + 104, GR - 58)
    if 3.5 <= k < 6:
        q = k - 3.5
        front.append(E.lumiere(fig, c, 22 * env(q, 0, 0.25, 0.7, 1.4), env(q, 0, 0.25, 0.7, 1.4), 'glace'))
    return back, front


E.accrocher(sys.modules[__name__], {
    'spikes_at': _spikes_at,
    'puff': lambda fig, cx, cy, r, op=1.0, kind='snow', seed=0: E.nuage(fig, cx, cy, r * 1.15, 'glace', op=op * (0.8 if kind == 'mist' else 1), seed=seed),
    'flake': lambda fig, x, y, s=1.0, op=1.0, rot=0.0: E.etincelle(fig, x, y, 6 * math.cos(math.radians(rot)), 25, 0.55 * s, 'glace', op=op),
    'wisp': lambda fig, p0, p1, p2, p3, w, op=1.0: E.ruban(fig, [p0, p1, p2, p3], w * 1.6, 'glace', op=op, kind='pointe'),
    'snow_trail': lambda fig, C, R, a0, a1, w, op=1.0: E.croissant(fig, C, R, a0, a1, w * 1.2, 'glace', op=op),
    'burst': lambda fig, c, r, op=1.0, seed=0, facing=0.0: E.lumiere(fig, c, r * 2.6, op, 'glace'),
})


if __name__ == '__main__':
    main()
