# Arcan vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/arcan/build.py)
# — respiration, attaque de base « Coup de col », attaque spéciale « Fronde d'Éole » (sort d'équipe) — dans le style
# lisse de l'interface, à 24 images par seconde (même méthode que Kael, Myrr, Eldra : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/arcan/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/arcan/
#   python3 refonte-graphique/ui-moderne/heros/arcan/anim.py --planche [t1 t2 …]   # une planche d'images clés (brouillon)
#
# Méthode : le dessin (arcan.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et se
# penche depuis les hanches, la tête suit avec un léger retard, le sac gonfle avec une image de retard (la toile se
# tend), il grogne (la mâchoire s'ouvre) ; les bras sont placés par cinématique inverse depuis les poings (le coude
# tourne autour de sa vraie jointure, rien ne se décroche) ; les cols du sac sont des tubes de toile tendus du sac aux
# poings (ils s'étirent avec le geste) ; dans la spéciale, le sac quitte les épaules : le même contour passe du dôme
# au ballon tenu par un col (aucun saut), tourne au-dessus de sa tête, est brandi, se vide, pend tout flasque, puis
# revient sur les épaules et se regonfle. Poses clés et durées reprises du pixel art.
# Effets du vent (mêmes formes et mêmes tons qu'Eldra et Myrr) : rubans qui s'enroulent en volutes, boule de vent
# comprimé, éclats, bouffées, feuilles ; pour la spéciale (sort d'équipe) : geyser de vent chaud vers le ciel, anneaux
# qui s'élargissent autour de lui, orbes d'énergie en gerbe dans toutes les directions, aura de flammes douces.
# Aucun flou SVG ; jamais de rayons droits répétés.
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
import arcan as A  # noqa: E402
from atelier import sm, lock, ribbon, ellipse, sides, bez, resample, mapp, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of  # noqa: E402

ROOT = A.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'arcan')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-arcan'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-62.0, -60.0, 330.0, 185.6)  # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = A.GRD
FOE = (200.0, GR - 40)               # le milieu de l'ennemi
HIT = (198.0, GR - 40)               # là où frappe la boule de vent
CEN = (66.0, GR - 1.0)               # le milieu entre ses pieds

WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']   # le vent (celui d'Eldra et de Myrr)
WINK = '#123c4a'                     # le contour des effets de vent
WARM = ['#fffbe8', '#fff0b0', '#ffd45c', '#f6ac3e', '#e66c32', '#ac362e']   # le vent chaud, l'aura
FINK = '#5a1e18'                     # le contour des effets chauds
ORB = ['#ffffff', '#dff2ff', '#9cc8f8', '#5a8ee8']                         # les orbes d'énergie bleu-blanc
DUST = ['#f6e4c0', '#d6b68a', '#a07c64']
DINK = '#4a3036'


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
    for i in range(n - 1):
        if ts[i] <= t <= ts[i + 1]:
            h = ts[i + 1] - ts[i]
            u = (t - ts[i]) / h
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1
            h10 = u ** 3 - 2 * u ** 2 + u
            h01 = -2 * u ** 3 + 3 * u ** 2
            h11 = u ** 3 - u ** 2
            return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]
    return vs[-1]


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


# les réglages animés (voir arcan.py) ; ffx, ffy : le poing lointain ; bm : le sac quitte les épaules (0 → 1) ; bdir,
# bL, bR, bfull, bwob, bsway : le ballon (direction, longueur, rayon, plein, la toile ondule, le bout se courbe) ;
# bfront : le sac passe devant sa tête
BASE = dict(crouch=0.0, lean=0.0, headx=0.0, heady=0.0, tilt=0.0, jaw=0.0, sk=0.0, ffx=A.FF0[0], ffy=A.FF0[1], fa=-90.0,
            fend=40.0, fopen=0.0, nend=140.0, nopen=0.0, cs=0.0, pg=0.0, wind=0.0, aura=0.0,
            bm=0.0, bdir=165.0, bL=40.0, bR=15.0, bfull=1.0, bwob=0.0, bsway=0.0, bfront=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'ff':
            d['ffx'], d['ffy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Coup de col » (pixel : ATTAQUE) : il lève le poing lointain et serre le sac contre lui (le sac
# gonfle, la toile se tend, il grogne : tenu), puis lance le poing vers l'ennemi comme un coup de poing (souffle de la
# vitesse) et desserre le col : le bout froncé s'ouvre en corolle et une boule de vent comprimé en jaillit ; elle file
# en arc (monte, puis plonge) et frappe l'ennemi (éclat, volutes, feuilles). Le sac se dégonfle un peu ; il resserre
# le col, ramène le poing, et le sac reprend son souffle.
ATTACK = [
    (0, {}),
    (110, dict(ff=(106.0, 26.0), fa=-84, crouch=1, lean=-1, sk=1, jaw=1, fend=-30, cs=1.0, pg=0.5)),
    (240, dict(ff=(103.0, 20.5), fa=-96, crouch=2, lean=-2, sk=2, jaw=2, head=(-1, 0), tilt=-3, fend=-96, cs=1.5, pg=1.0)),
    (470, dict(ff=(102.6, 19.8), fa=-97, crouch=2.2, lean=-2.3, sk=2.2, jaw=2, head=(-1.2, 0), tilt=-3.4, fend=-98, cs=1.2, pg=1.0)),
    (515, dict(ff=(134.0, 42.0), fa=-4, crouch=2, lean=2, sk=2, jaw=2, head=(1, 0), tilt=2, fend=-4, cs=-1.6, pg=-1.0)),
    (565, dict(ff=(137.0, 43.0), fa=-6, crouch=2, lean=2.2, sk=1, jaw=2, head=(1, 0), tilt=2, fend=-4, fopen=1, cs=-1.0, pg=-1.2)),
    (625, dict(ff=(136.0, 43.0), fa=-6, crouch=2, lean=2, sk=-1, jaw=1, head=(0.8, 0), tilt=1.5, fend=-3, fopen=1, cs=0.6, pg=-0.6)),
    (690, dict(ff=(134.0, 44.0), fa=-5, crouch=2, lean=1, sk=-2, jaw=1, fend=-2, fopen=0.8, cs=0.9, pg=0.2)),
    (850, dict(ff=(126.0, 41.0), fa=-24, crouch=1, lean=1, sk=-2, jaw=0, fend=10, fopen=0, cs=-0.6, pg=0.4)),
    (990, dict(ff=(115.0, 35.0), fa=-62, crouch=1, sk=-1, fend=30, cs=0.4)),
    (1190, {}),
]
ATT_REL = 560          # il desserre le col : la boule de vent sort
ATT_HIT = 690          # elle frappe l'ennemi

# 3) La spéciale « Fronde d'Éole » (sort d'équipe : l'attaque de toute l'équipe monte, tous les alliés reçoivent de
# l'énergie) : il attrape le sac par un col et le fait tourner au-dessus de sa tête (le vent tourne autour de lui),
# le freine et le brandit à bout de bras, la bouche vers le ciel ; il l'ouvre en poussant son cri de guerre
# (LANCEMENT, 830 ms) : un geyser de vent chaud jaillit vers le ciel et retombe des deux côtés en volutes, des anneaux
# s'élargissent autour de lui, des orbes d'énergie partent en gerbe dans toutes les directions, une aura de flammes
# douces monte sur lui. Le sac se vide, pend tout flasque au bout de son poing, puis revient sur ses épaules (pof !).
WHIRL_G = (108.0, 17.0)
RAISE_G = (101.0, 16.0)
SPECIAL = [
    (0, {}),
    (110, dict(crouch=1, sk=1, jaw=1)),
    (260, dict(ff=(104.0, 22.0), fa=-95, crouch=2, jaw=2, sk=1, bm=1, bdir=156.1, bL=42, bR=18, cs=1, fend=-100)),
    (630, dict(ff=WHIRL_G, fa=-92, crouch=2, jaw=2, sk=1, bm=1, bdir=156.1, bL=44, bR=17, head=(-1, 0), fend=-100, wind=1)),
    (680, dict(ff=RAISE_G, fa=-92, crouch=3, jaw=2, head=(0, -1), tilt=-4, bm=1, bdir=104, bL=46, bR=15.5, aura=0.5, fend=-95, wind=1)),
    (800, dict(ff=(101.0, 15.6), fa=-92, crouch=3, jaw=2, head=(0, -1.2), tilt=-4.5, bm=1, bdir=105, bL=47, bR=15.5, aura=0.8, fend=-95, wind=1)),
    (845, dict(ff=(101.0, 15.4), fa=-92, crouch=3, jaw=2.4, head=(0, -1.3), tilt=-5, bm=1, bdir=106, bL=48, bR=16, nopen=1, aura=1, fend=-95, wind=1.4)),
    (1040, dict(ff=(101.0, 15.6), fa=-92, crouch=3, jaw=2.2, head=(0, -1.2), tilt=-4.5, bm=1, bdir=106, bL=48, bR=16, bfull=0.95, nopen=1, aura=1, fend=-95, wind=1.4)),
    (1150, dict(ff=RAISE_G, fa=-92, crouch=2, jaw=2, bm=1, bdir=107, bL=48, bR=15, bfull=0.55, bwob=0.6, nopen=1, aura=1, fend=-95, wind=1.2)),
    (1280, dict(ff=RAISE_G, fa=-90, crouch=2, jaw=1, bm=1, bdir=110, bL=46, bR=14, bfull=0.2, bwob=1.0, bsway=1, nopen=1, aura=0.9, fend=-95, wind=1)),
    (1400, dict(ff=(108.0, 18.0), fa=-80, crouch=1.5, jaw=1, bm=1, bdir=116, bL=40, bR=10, bfull=0.05, bwob=1.0, bsway=-1, nopen=0.8, aura=0.8, fend=-80, wind=0.6)),
    (1470, dict(ff=(120.0, 24.0), fa=-55, crouch=1, bm=1, bdir=40, bL=32, bR=8, bfull=0.05, bwob=1.0, bsway=1, nopen=0.7, aura=0.6, fend=-50, bfront=1)),
    (1640, dict(ff=(127.0, 40.0), fa=-12, crouch=1, bm=1, bdir=-88, bL=27, bR=7.5, bfull=0.1, bwob=0.9, bsway=1.4, nopen=0.6, aura=0.35, fend=-10, bfront=1, head=(0.6, 0.6))),
    (1790, dict(ff=(126.0, 41.0), fa=-14, crouch=1, bm=1, bdir=-94, bL=27, bR=7.5, bfull=0.1, bwob=0.8, bsway=-1.2, nopen=0.6, aura=0.1, fend=-12, bfront=1, head=(0.6, 0.6))),
    (1910, dict(ff=(112.0, 38.0), fa=-70, crouch=1, sk=-3, jaw=1, bm=0, nopen=0, fend=30, cs=1.2)),
    (2020, dict(sk=2.2, jaw=1, cs=-1)),
    (2180, {}),
]
SP_LAUNCH = 830        # MOMENT DE LANCEMENT : le geyser jaillit, les orbes partent vers l'équipe
ORBIT = [(260, 160.0), (430, 250.0), (510, 340.0), (575, 430.0), (630, 520.0)]


def orbit(theta, L=40.0, R=15.0, lift=0.3):
    """Le sac qui tourne autour du poing levé, vu un peu d'en dessus : theta = 0 vers l'ennemi, 90 derrière lui,
    180 vers la gauche, 270 devant lui (devant sa tête). Renvoie la direction vue, la longueur vue, devant ou non."""
    a = math.radians(theta)
    v = (math.cos(a), -0.34 * math.sin(a) - lift)
    k = math.hypot(*v)
    return math.degrees(math.atan2(-v[1], v[0])), max(L * k, R * 0.9), math.sin(a) < -0.15


# ======================================================================== la respiration (2 s, en boucle)

def idle_offsets(T):
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    d = dict(sk=0.9 * math.sin(u - 1.1), crouch=0.35 * (0.5 - 0.5 * math.cos(u - 2.7)), heady=0.3 * math.sin(u - 0.7),
             tilt=0.6 * math.sin(u - 1.0), jaw=0.7 * max(0.0, math.sin(u - 3.5)) ** 2, cs=0.9 * math.sin(u + 0.4),
             pg=0.6 * math.sin(u + 0.2), fend=6 * math.sin(u - 1.5), nend=-6 * math.sin(u - 1.5))
    return d, br


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
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
        if action == 'special' and ORBIT[0][0] <= tl <= ORBIT[-1][0]:
            th = monotone([o[0] for o in ORBIT], [o[1] for o in ORBIT], tl)
            d, L, front = orbit(th, act['bL'], act['bR'])
            act['bdir'], act['bL'], act['bfront'] = d, L, 1.0 if front else 0.0
            # le poing suit la traction du sac (un petit cercle)
            a = math.radians(th)
            act['ffx'] = act['ffx'] + 1.6 * math.cos(a) * min(1, (tl - 260) / 80)
            act['ffy'] = act['ffy'] - 0.6 * math.sin(a) * min(1, (tl - 260) / 80)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    br *= w
    out = dict(breath=br, crouch=P['crouch'], lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'], jaw=max(0.0, P['jaw']),
               sk=P['sk'], fa=P['fa'], fend=P['fend'], fopen=max(0.0, min(1.0, P['fopen'])), nend=P['nend'],
               nopen=max(0.0, min(1.0, P['nopen'])), cs=P['cs'], pg=P['pg'], wind=P['wind'], aura=max(0.0, P['aura']))
    if act:
        # le poing lointain : sa place (repère du dessin) + ce que la respiration et le tassement lui ajoutent
        idl_dy = 0.8 * w * idl['crouch'] - 0.6 * br
        out['ff'] = (P['ffx'], P['ffy'] + idl_dy)
    m = max(0.0, min(1.0, P['bm']))
    if m > 0.001:
        out['bag'] = dict(m=smooth(m), dir=P['bdir'], L=P['bL'], R=P['bR'], full=max(0.02, min(1.0, P['bfull'])),
                          wob=P['bwob'], sway=P['bsway'], front=P['bfront'] > 0.5)
    out['ph'] = 2 * math.pi * T * 0.8 + 1.5 * P['wind'] * T
    out['blink'] = 1.0 if ((w > 0.95 and 1.30 <= (T % 4.0) < 1.38) or (action == 'special' and 1700 <= tl < 1770)) else 0.0
    return out


# ======================================================================== les effets (dégradés, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, r if ry is None else ry, stops)


def glow(fig, c, r, color, op, ry=None):
    ry = r if ry is None else ry
    if op <= 0.01 or r <= 0.1:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(ry), fig.rad(
        c[0], c[1], r, ry, [(0, color, op), (0.45, color, op * 0.4), (1, color, 0)]))


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
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


def spiral(p, d, r0, turn, s, n=14):
    """Une volute : depuis p dans la direction d, elle s'enroule (s = +1 sens horaire à l'écran) sur `turn` degrés."""
    L = math.hypot(*d) or 1
    dx, dy = d[0] / L, d[1] / L
    nx, ny = (-dy * s, dx * s)
    C = (p[0] + nx * r0, p[1] + ny * r0)
    a0 = math.atan2(p[1] - C[1], p[0] - C[0])
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = a0 + s * math.radians(turn) * t
        r = r0 * (1 - 0.65 * t)
        out.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290, warm=False):
    """Une rafale : un ruban effilé le long d'une courbe, qui s'enroule en volute au bout. tail : l'arrière s'efface."""
    if op <= 0.02 or w < 0.15:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 18)
    d = (p3[0] - p2[0], p3[1] - p2[1])
    if curl > 0.3:
        c = c + spiral(p3, d, curl, turn, s, 14)
    n = len(c)
    i0 = int(tail * (n - 4))
    c = c[i0:]
    n = len(c)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        ws.append(max(0.08, w * (math.sin(math.pi * min(1, t * 1.25)) ** 0.8) * (1 - 0.55 * t)))
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(c, ws)
    core = stroke_shape(c, [x * 0.42 for x in ws])
    if warm:
        gr = g_lin(fig, c[0], c[-1], [(0, WARM[3]), (0.35, WARM[2]), (0.7, WARM[1]), (1, WARM[2])])
        return outlined([(sh, gr, 1), (core, WARM[0], 0.9)], ink=FINK, w=1.0, op=op)
    gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.35, WIND[2]), (0.7, WIND[1]), (1, WIND[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0, warm=False):
    """L'éclat du vent : une boule de lumière (dégradé), un croissant d'onde du côté visé."""
    if op <= 0.02 or r < 0.3:
        return ''
    tones = WARM[:4] if warm else [WIND[0], WIND[1], WIND[3], WIND[4]]
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.92 * op), (0.3, tones[1], 0.65 * op), (0.65, tones[2], 0.25 * op), (1, tones[3], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper_=0.0)
    out += outlined([(ring, tones[1], 1)], ink=FINK if warm else WINK, w=1.0, op=op * 0.9)
    return out


def arc_band(C, R, a0, a1, w, taper_=0.8, n=28, ry=None):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    k = 1.0 if ry is None else ry / R
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper_)
        outer.append((C[0] + R * math.cos(a), C[1] + k * R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + k * (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def puff(fig, cx, cy, r, op=1.0, k=0, warm=False, dust=False):
    """Une bouffée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = [(0, 0, 1), (0.8, 0.3, 0.72), (-0.82, 0.28, 0.7), (0.2, -0.55, 0.62), (-0.35, -0.35, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in j[:4 + (k % 2)]]
    tones, ink = (WARM[0], WARM[1], WARM[3]), FINK
    if not warm:
        tones, ink = (WIND[0], WIND[1], WIND[2]), WINK
    if dust:
        tones, ink = DUST, DINK
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def leaf(fig, x, y, a, s=1.6, op=1.0, dry=False):
    """Une feuille arrachée qui tourbillonne (vert tendre, ou jaune paille), nervure claire."""
    if op <= 0.02:
        return ''
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.6, 0), P(-0.2, -0.85), P(1.6, 0), P(-0.2, 0.85)], sharp=(0, 2), t=0.9)
    vein = ribbon([P(-1.3, 0), P(0, -0.05), P(1.3, 0)], [0.05, 0.22 * s, 0.05])
    st = [(0, '#f4ec9c'), (0.5, '#e2d66e'), (1, '#a89a3e')] if dry else [(0, '#c8f0a0'), (0.5, '#84ba4a'), (1, '#38743e')]
    gr = g_lin(fig, P(1, -1), P(-1, 1), st)
    return outlined([(sh, gr, 1), (vein, '#f6ffe0', 0.8)], ink='#173c34', w=0.9, op=op)


def ring_pts(c, rx, ry, a0, a1, n=40):
    return [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def flat_ring(fig, c, rx, ry, w, op, back, warm=False, a_off=0.0, span=160):
    """Un anneau couché autour de lui (une ellipse) : la moitié de derrière passe derrière lui, celle de devant devant ;
    un ruban effilé aux deux bouts (jamais un cercle fermé), un fil clair dessus."""
    if op <= 0.02 or rx < 1:
        return ''
    a0 = (190 if back else 10) + a_off
    pts = ring_pts(c, rx, ry, a0, a0 + span, 36)
    ws = [max(0.05, w * math.sin(math.pi * i / 36) ** 0.6) for i in range(37)]
    body = stroke_shape(pts, ws)
    core = stroke_shape([(x, y - 0.25 * w) for x, y in pts], [x * 0.38 for x in ws])
    if warm:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WARM[4]), (0.5, WARM[2]), (1, WARM[3])])
        return outlined([(body, gr, 1), (core, WARM[0], 0.9)], ink=FINK, w=0.9, op=op * (0.8 if back else 1))
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=op * (0.75 if back else 1))


def ell_arc(fig, C, rx, ry, a0, a1, w, op, warm=False):
    """Un ruban le long d'un arc d'ellipse (angles en degrés), effilé aux deux bouts, plus épais vers a1 (la tête)."""
    if op <= 0.02:
        return ''
    n = 30
    pts = [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    ws = [max(0.05, w * (i / n) ** 0.9 * math.sin(math.pi * min(1, i / n * 1.15)) ** 0.5) for i in range(n + 1)]
    ws[-1] = 0.05
    body = stroke_shape(pts, ws)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    if warm:
        gr = g_lin(fig, pts[0], pts[-1], [(0, WARM[3]), (1, WARM[1])])
        return outlined([(body, gr, 1), (core, WARM[0], 0.9)], ink=FINK, w=0.9, op=op)
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (1, WIND[1])])
    return outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=op)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0):
    """Une langue de flamme douce de l'aura : large et pâle à la base, fine et rouge au bout, en S."""
    if h < 0.6 or op <= 0.02:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.6), w * 0.55, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, WARM[1]), (0.35, WARM[2]), (0.72, WARM[4]), (1, WARM[5])])
    gin = g_lin(fig, p0, q(p3, 0.6), [(0, WARM[0]), (0.6, WARM[1]), (1, WARM[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], ink=FINK, w=1.2, op=op)


def orb(fig, c, r, vel, gold=False, op=1.0):
    """Un orbe d'énergie (bleu-blanc ou or) : une boule de lumière et sa traîne effilée derrière lui."""
    if op <= 0.02 or r < 0.2:
        return ''
    tones = WARM if gold else ORB + ['#3a64c0']
    L = math.hypot(*vel) or 1
    u = (vel[0] / L, vel[1] / L)
    tail_len = min(14.0, 2.5 + L * 0.6)
    tail = [add(c, u, -tail_len * t) for t in (1.0, 0.66, 0.33, 0.0)]
    tw = [0.05, r * 0.7, r * 1.4, r * 1.9]
    tsh = stroke_shape(tail, tw)
    gt = g_lin(fig, tail[0], c, [(0, tones[3], 0), (0.6, tones[2], 0.8), (1, tones[1], 1)])
    out = glow(fig, c, r * 3.2, tones[2], 0.45 * op)
    body = ellipse(c[0], c[1], r, r)
    gb = g_rad(fig, (c[0] + r * 0.3, c[1] - r * 0.3), r * 1.3, [(0, '#ffffff'), (0.45, tones[1]), (1, tones[2])])
    out += outlined([(tsh, gt, 1), (body, gb, 1)], ink=FINK if gold else '#1c2a5a', w=0.9, op=op)
    return out


def bezp(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


# ---- 2) l'attaque : la boule de vent comprimé

_ATT = {}


def wind_ball(fig, c, r, ph, op=1.0):
    """La boule de vent comprimé : un cœur blanc (un contour) et une volute qui s'enroule autour."""
    out = glow(fig, c, r * 2.0, WIND[2], 0.5 * op)
    core = ellipse(c[0], c[1], r * 0.62, r * 0.62)
    gc = g_rad(fig, (c[0] + r * 0.2, c[1] - r * 0.2), r * 0.8, [(0, '#ffffff'), (0.55, WIND[1]), (1, WIND[3])])
    out += outlined([(core, gc, 1), (ellipse(c[0] + r * 0.18, c[1] - r * 0.22, r * 0.22, r * 0.16), '#ffffff', 0.9)], w=1.0, op=op)
    for j, (a0, rr, w) in enumerate(((ph, r * 1.05, r * 0.5), (ph + 170, r * 0.8, r * 0.38))):
        out += ell_arc(fig, c, rr, rr * 0.9, a0 - 200, a0, w, op * 0.95)
    return out


def fx_attack(tl):
    def f(fig, ctx):
        M = ctx.get('end_f')
        if tl < ATT_REL:
            _ATT['M'] = M
        M0 = _ATT.get('M', M)
        # le poing lancé : un souffle de vitesse courbe, de sa place levée à sa place tendue
        k = env(tl, 470, 505, 540, 640)
        if k > 0:
            G0, G = (102.6, 19.8), ctx['GF']
            mid = add(lerp(G0, G, 0.5), (8, -10))
            fig.fx_back.append(gust(fig, G0, mid, mid, G, 3.6, curl=0, op=0.75 * k, tail=max(0.0, (tl - 540) / 120)))
        # il serre le sac : deux fines volutes d'air entrent dans la toile (préparation)
        k = env(tl, 120, 220, 400, 480)
        if k > 0:
            p = mapp(ctx['UC'], (60, 0))
            fig.fx_back.append(gust(fig, add(p, (-24, -6)), add(p, (-16, -10)), add(p, (-8, -6)), add(p, (-3, -1)), 1.6, curl=2.2, s=1, op=0.6 * k))
            p = mapp(ctx['UC'], (104, 6))
            fig.fx_back.append(gust(fig, add(p, (14, -12)), add(p, (10, -8)), add(p, (5, -6)), add(p, (1, -2)), 1.4, curl=2.0, s=-1, op=0.55 * k))
        # le bout s'ouvre : éclat blanc, la boule de vent sort et file en arc jusqu'à l'ennemi
        T = HIT
        if M0 is not None:
            P0, P1, P2, P3 = M0, add(M0, (26, -24)), add(T, (-28, -24)), T
            kp = env(tl, ATT_REL - 10, ATT_REL + 20, ATT_REL + 60, ATT_REL + 160)
            if kp > 0:
                fig.fx_front.append(pop(fig, add(M, (2.4, 0)), 4.4 * (0.6 + 0.4 * kp), facing=0, op=kp))
                for j, s_ in enumerate((1, -1)):
                    q = add(M, (2, -5 * s_))
                    fig.fx_back.append(gust(fig, q, add(q, (4, -3 * s_)), add(q, (8, -4 * s_)), add(q, (10, -7 * s_)), 1.5, curl=2.4, s=-s_, op=kp * 0.8))
            if ATT_REL <= tl <= ATT_HIT:
                u = smooth((tl - ATT_REL) / (ATT_HIT - ATT_REL))
                c = bezp(P0, P1, P2, P3, u)
                # la traîne : un fuseau courbe derrière la boule, effilé
                ts = [max(0.0, u - 0.45 + 0.45 * i / 10) for i in range(11)]
                pts = [bezp(P0, P1, P2, P3, t) for t in ts]
                ws = [0.05] + [0.4 + 5.5 * (i / 10) ** 1.6 for i in range(1, 10)] + [0.05]
                if math.dist(pts[0], pts[-1]) > 2:
                    body = stroke_shape(pts, ws)
                    core = stroke_shape(pts, [x * 0.4 for x in ws])
                    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.6, WIND[2]), (1, WIND[1])])
                    fig.fx_front.append(outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=0.9))
                fig.fx_front.append(wind_ball(fig, c, 4.5 + 4.5 * u, 360 * u * 2.2, op=1.0))
        # l'impact : éclat, volutes qui s'ouvrent, feuilles et bouffées
        if tl >= ATT_HIT - 10:
            v = (tl - ATT_HIT) / (ATT_ATTACK_END - ATT_HIT)
            v = max(0.0, v)
            kh = env(tl, ATT_HIT - 10, ATT_HIT + 20, ATT_HIT + 120, ATT_HIT + 320)
            fig.fx_front.append(pop(fig, T, 10 * (0.7 + 0.5 * kh), facing=10, op=kh))
            fade = 1 - smooth(v * 1.1)
            for j, (dx, dy, s_, r0) in enumerate(((11, -12, 1, 4.0), (12, 12, -1, 3.6), (-9, -14, -1, 3.0), (-6, 13, 1, 2.6))):
                g = 1 + 1.6 * smooth(v * 1.6)
                q = (T[0] + dx * g, T[1] + dy * g)
                d = norm((dx, dy))
                fig.fx_front.append(gust(fig, add(q, d, -8 * g), add(q, d, -5 * g), add(q, d, -2), q, 2.6 - 0.8 * v,
                                         curl=r0 * (0.8 + 0.6 * v), s=s_, tail=0.5 * v, op=fade))
            for j, (dx, dy, a0, dry) in enumerate(((18, -20, 30, False), (22, 4, 120, True), (-4, -26, 200, False), (12, 18, 300, True))):
                g = smooth(v * 1.4)
                q = (T[0] + dx * (0.4 + g), T[1] + dy * (0.4 + g) + 10 * v * v)
                fig.fx_front.append(leaf(fig, q[0], q[1], a0 + 400 * v, 1.6, op=fade))
            if v > 0.1:
                fig.fx_back.append(puff(fig, T[0] - 6 - 6 * v, T[1] + 6, 3.0 + 2.0 * v, op=fade * 0.8, k=1))
                fig.fx_back.append(puff(fig, T[0] + 8 + 8 * v, T[1] - 8, 2.6 + 2.0 * v, op=fade * 0.7, k=0))
    return f


ATT_ATTACK_END = 1190


# ---- 3) la spéciale : la fronde, puis le sort d'équipe

# les orbes : (direction de départ en degrés, y vers le bas ; distance ; départ après le lancement (ms) ; rayon ; or ? ;
# derrière lui ?) — ceux de derrière sont plus petits (plus loin) ; un monte droit au ciel ; ceux de devant retombent
# au sol de part et d'autre de ses pieds
ORBS = [(-92, 110, 0, 2.6, True, False), (-150, 120, 20, 2.4, False, False), (-30, 120, 30, 2.4, True, False),
        (-170, 125, 60, 2.2, True, False), (-8, 130, 70, 2.3, False, False), (-120, 95, 90, 1.7, False, True),
        (-62, 100, 100, 1.7, True, True), (160, 110, 120, 2.4, False, False), (18, 115, 140, 2.4, True, False),
        (-105, 130, 160, 1.6, False, True), (-75, 125, 170, 2.0, False, False), (135, 80, 190, 2.0, True, False),
        (45, 85, 210, 2.0, False, False)]
# l'aura : des langues de flamme douces qui montent sur lui (repère du buste au repos) : (x, y, hauteur, largeur, phase)
AURA = [(28, 62, 24, 8.0, 0.0), (42, 50, 26, 8.6, 1.3), (100, 54, 26, 8.4, 2.1), (118, 66, 22, 7.6, 2.9), (10, 76, 20, 7.0, 3.7),
        (122, 78, 19, 7.0, 4.4), (46, 96, 20, 7.6, 5.1), (98, 96, 20, 7.6, 0.7), (54, 14, 22, 8.0, 1.9), (76, 8, 24, 8.4, 3.3),
        (36, 30, 20, 7.4, 4.0), (92, 20, 20, 7.4, 5.6)]
AURA_FRONT = [(24, 113, 12, 6.4, 0.4), (40, 114, 9, 5.6, 2.2), (96, 114, 10, 6.0, 1.1), (114, 113, 12, 6.4, 3.0)]


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        feet = CEN
        U = ctx['U']
        # ---- il se ramasse : la poussière se lève à ses pieds ----
        k = env(tl, 60, 200, 300, 520)
        if k > 0:
            fig.fx_back.append(puff(fig, feet[0] - 34 - 4 * k, GR - 2, 2.2 + 1.6 * k, op=k * 0.8, k=1, dust=True))
            fig.fx_back.append(puff(fig, feet[0] + 36 + 4 * k, GR - 2, 2.2 + 1.6 * k, op=k * 0.8, k=0, dust=True))
        # ---- la fronde : le vent tourne autour de lui en suivant le sac ----
        if 260 <= tl <= 760:
            th = monotone([o[0] for o in ORBIT], [o[1] for o in ORBIT], min(tl, 630))
            if tl > 630:
                th += (tl - 630) * 0.9
            kw = env(tl, 260, 330, 640, 760)
            G = ctx['GF']
            rx = 44.0
            C = (G[0], G[1] - 0.14 * rx)
            lvl = min(2.0, (tl - 260) / 160)
            # la traîne du sac : un ruban courbe qui le suit (la moitié de derrière passe derrière lui)
            a1 = -th
            lay = fig.fx_back if math.sin(math.radians(th)) > 0.15 else fig.fx_front
            lay.append(ell_arc(fig, C, rx, 0.34 * rx, a1 + 110, a1 + 18, 3.0 + lvl * 1.2, kw * 0.9))
            if lvl >= 1:
                lay2 = fig.fx_front if lay is fig.fx_back else fig.fx_back
                lay2.append(ell_arc(fig, C, rx - 8, 0.34 * (rx - 8), a1 + 240, a1 + 160, 2.0 + lvl * 0.6, kw * 0.8))
            # l'anneau au sol, la poussière, les feuilles qui montent en spirale
            rr = 30 + 6 * lvl
            fig.fx_back.append(flat_ring(fig, (feet[0], GR - 2), rr, 6 + lvl, 1.6 + 0.8 * lvl, kw * min(1, lvl), True, a_off=th * 0.5 % 40))
            fig.fx_front.append(flat_ring(fig, (feet[0], GR - 2), rr, 6 + lvl, 1.6 + 0.8 * lvl, kw * min(1, lvl), False, a_off=th * 0.5 % 40))
            for j in range(6):
                a = math.radians(j * 60 + th * 0.8)
                h = ((tl - 260) / 500 * 0.9 + j / 6 * 0.6) % 1.0
                x = feet[0] + math.cos(a) * (44 + 12 * h)
                y = GR - 8 - h * 50 + math.sin(a) * 6
                if abs(x - feet[0]) > 44:
                    fig.fx_front.append(leaf(fig, x, y, j * 70 + th, 1.5, op=kw * min(1, lvl - 0.5) * (1 - h * 0.6), dry=(j % 3 == 0)))
        # ---- l'aura : des flammes douces rouge-orangé et or montent sur lui ----
        au = P['aura']
        if au > 0.02:
            T = tl / 1000
            fig.glow(*mapp(U, (66, 60)), 62, 58, WARM[3], 0.18 * au)
            # des points du corps (ils suivent ses gestes) : épaules, coudes, poings, crâne, hanches, genoux
            HD = ctx['HEAD']
            anchors = [(add(ctx['SN'], (-9, -3)), 30, 9.0), (add(ctx['SF'], (9, -2)), 30, 9.0), (add(ctx['EN'], (-6, -1)), 26, 8.0),
                       (add(ctx['EF'], (6, -1)), 26, 8.0), (add(ctx['GN'], (-5, 1)), 22, 7.4), (mapp(HD, (60, 14)), 28, 8.6),
                       (mapp(HD, (80, 9)), 30, 9.0), (mapp(HD, (46, 32)), 24, 8.0), (mapp(U, (44, 98)), 24, 8.0),
                       (mapp(U, (100, 98)), 24, 8.0), ((30, 104), 20, 7.4), ((106, 103), 20, 7.4)]
            for j, (b, h, w) in enumerate(anchors):
                ph = j * 1.37
                fl = 0.75 + 0.25 * math.sin(T * 9 + ph * 1.7)
                fig.fx_back.append(tongue(fig, b, h * au * fl, w * (0.7 + 0.3 * au), bend=math.sin(T * 7 + ph), lean=0.15 * math.sin(T * 5 + ph), op=min(1, au * 1.4)))
            for j, (x, y, h, w, ph) in enumerate(AURA_FRONT):
                fl = 0.75 + 0.25 * math.sin(T * 10 + ph * 2)
                fig.fx_front.append(tongue(fig, (x, y + 1.5), h * au * fl, w, bend=math.sin(T * 8 + ph), lean=0.1 * math.sin(T * 6 + ph), op=min(1, au * 1.3)))
        # ---- le LANCEMENT : un éclair chaud au col ouvert, le geyser de vent chaud vers le ciel ----
        M = ctx.get('end_n')
        bu = ctx['bu']
        if M is not None and SP_LAUNCH - 40 <= tl <= 1500:
            kf = env(tl, SP_LAUNCH - 30, SP_LAUNCH, SP_LAUNCH + 80, SP_LAUNCH + 300)
            if kf > 0:
                fig.fx_back.append(glow(fig, M, 110 * (0.6 + 0.4 * kf), WARM[1], 0.35 * kf))
                fig.fx_front.append(glow(fig, M, 30 * kf, '#ffffff', 0.7 * kf))
                fig.fx_front.append(pop(fig, M, 5.0 * (0.6 + 0.5 * kf), facing=ang_of(bu), op=kf, warm=True))
            kg = env(tl, SP_LAUNCH - 10, SP_LAUNCH + 40, 1180, 1420)
            if kg > 0:
                u = (tl - SP_LAUNCH) / 600
                # la colonne : des bouffées chaudes qui montent du col, de plus en plus grosses
                for j in range(5):
                    s = ((tl - SP_LAUNCH) / 420 + j / 5) % 1.0
                    q = add(M, bu, 4 + 26 * s)
                    q = (q[0] + 2.0 * math.sin(s * 6 + j), q[1])
                    fig.fx_front.append(puff(fig, q[0], q[1], (2.2 + 3.2 * s) * (0.6 + 0.4 * kg), op=kg * (1 - s ** 2), k=j, warm=True))
                # elle retombe des deux côtés en volutes
                top = add(M, bu, 24)
                for j, s_ in enumerate((-1, 1)):
                    g = smooth(min(1, u * 1.6))
                    p0 = add(top, (0, 2))
                    p3 = add(top, (s_ * (14 + 16 * g), 14 + 16 * g))
                    fig.fx_front.append(gust(fig, p0, add(p0, (s_ * 6, -8)), add(p3, (s_ * 2, -14)), p3, 2.8, curl=3.6, s=-s_ if s_ > 0 else 1,
                                             op=kg * 0.95, warm=True, tail=0.3 * g))
                    p3b = add(top, (s_ * (8 + 10 * g), 24 + 10 * g))
                    fig.fx_front.append(gust(fig, add(p0, (0, 6)), add(p0, (s_ * 4, 0)), add(p3b, (s_ * 2, -8)), p3b, 2.0, curl=2.6, s=-s_ if s_ > 0 else 1,
                                             op=kg * 0.8, tail=0.3 * g))
        # ---- les anneaux qui s'élargissent autour de lui (un chaud, un de jade, l'élément du vent) ----
        if SP_LAUNCH - 10 <= tl <= 1700:
            for j, (delay, warm, y_, w) in enumerate(((0, True, 70, 3.4), (90, False, 82, 2.6), (40, True, 112, 2.6))):
                u = smooth((tl - SP_LAUNCH - delay) / 520)
                if u <= 0:
                    continue
                op = env(tl, SP_LAUNCH + delay - 10, SP_LAUNCH + delay + 40, 1250, 1700)
                rx = 26 + 54 * u if j < 2 else 22 + 48 * u
                c = mapp(U, (66, y_)) if j < 2 else (feet[0], GR - 1.5)
                ry = rx * (0.24 if j < 2 else 0.14)
                fig.fx_back.append(flat_ring(fig, c, rx, ry, w - 1.0 * u, op, True, warm=warm))
                fig.fx_front.append(flat_ring(fig, c, rx, ry, w - 1.0 * u, op, False, warm=warm))
            # la poussière s'écarte en rond à ses pieds
            u = smooth((tl - SP_LAUNCH) / 600)
            kd = env(tl, SP_LAUNCH, SP_LAUNCH + 80, 1300, 1700)
            for j, sx in enumerate((-1, 1)):
                fig.fx_back.append(puff(fig, feet[0] + sx * (40 + 26 * u), GR - 2 - 2 * u, 2.6 + 1.8 * u, op=kd * 0.85, k=j, dust=True))
                fig.fx_front.append(puff(fig, feet[0] + sx * (28 + 30 * u), GR + 0.5, 2.0 + 1.4 * u, op=kd * 0.8, k=j + 1, dust=True))
        # ---- les orbes d'énergie, en gerbe dans toutes les directions ----
        if M is not None and tl >= SP_LAUNCH:
            if 'M' not in _SP or tl < SP_LAUNCH + 20:
                _SP['M'] = M
            M0 = _SP['M']
            for (ang, dist, t0, r, gold, back) in ORBS:
                t = (tl - SP_LAUNCH - t0) / 560
                if t <= 0 or t >= 1.05:
                    continue
                s = 1 - (1 - min(1, t)) ** 2.2
                d = unit(ang)
                end = (feet[0] + d[0] * dist, (GR - 46) + d[1] * dist * 0.85)
                if end[1] > GR - 2:
                    end = (end[0], GR - 2)
                ctrl = add(lerp(M0, end, 0.5), (0, -26))
                c = ((1 - s) ** 2 * M0[0] + 2 * s * (1 - s) * ctrl[0] + s * s * end[0], (1 - s) ** 2 * M0[1] + 2 * s * (1 - s) * ctrl[1] + s * s * end[1])
                s2 = 1 - (1 - min(1, t + 0.04)) ** 2.2
                c2 = ((1 - s2) ** 2 * M0[0] + 2 * s2 * (1 - s2) * ctrl[0] + s2 * s2 * end[0], (1 - s2) ** 2 * M0[1] + 2 * s2 * (1 - s2) * ctrl[1] + s2 * s2 * end[1])
                vel = sub(c2, c)
                op = env(t, 0.0, 0.06, 0.75, 1.02)
                lay = fig.fx_back if back else fig.fx_front
                lay.append(orb(fig, c, r * (0.6 + 0.4 * min(1, t * 4)), (vel[0] * 3, vel[1] * 3), gold=gold, op=op))
        # ---- le sac se vide : des bouffées sortent encore du col, puis il claque au vent ----
        if 1150 <= tl <= 1500 and M is not None:
            v = (tl - 1150) / 350
            fig.fx_front.append(puff(fig, *add(M, bu, 6 + 10 * v), 2.0 * (1 - v) + 0.5, op=(1 - v) * 0.9, k=1, warm=True))
        # ---- pof ! il le remet sur ses épaules : l'air rentre, il se regonfle ----
        k = env(tl, 1880, 1960, 2010, 2160)
        if k > 0:
            v = (tl - 1880) / 280
            top = mapp(ctx['UC'], (62, 2))
            for j, (dx, dy, s_) in enumerate(((-30, 8, 1), (30, 6, -1), (-12, -6, 1), (16, -8, -1))):
                q = add(top, (dx * (0.8 + 0.4 * v), dy - 6 * v))
                fig.fx_front.append(gust(fig, q, add(q, (4 * s_, -3)), add(q, (8 * s_, -5)), add(q, (10 * s_, -9)), 1.6, curl=2.4, s=-s_, op=k * 0.85))
            fig.fx_front.append(puff(fig, top[0] - 36 - 4 * v, top[1] + 30, 2.4, op=k * 0.7, k=1))
            fig.fx_front.append(puff(fig, top[0] + 40 + 4 * v, top[1] + 28, 2.2, op=k * 0.7, k=0))
    return f


_SP = {}


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre."""
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


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre au sol sous lui."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 50 * k, fy - 3.4 * k, cx + 50 * k, fy + 3.4 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


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
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
        if act == 'special' and tl < 50:
            _SP.clear()
        if act == 'attack' and tl < 50:
            _ATT.clear()
    return A.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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


def find_offset(sprite, frame):
    """Où le dessin pixel art (pieds en (64, 116)) est posé dans une image d'animation."""
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    ys, xs = np.nonzero(s[:, :, 3] > 200)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = s[y0:y1, x0:x1]
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub_ = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub_ - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1] - x0, best[2] - y0


def pixel_frames(name):
    """Les images d'une animation pixel art (GIF de contrôle, fond clair retiré), à l'échelle 1, et la place du
    point « sol » (64, 116) du dessin dans ces images."""
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd'))
    import hd
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-arcan-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (abs(a[:, :, 0].astype(int) - 232) <= 1) & (abs(a[:, :, 1].astype(int) - 236) <= 1) & (abs(a[:, :, 2].astype(int) - 242) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('arcan'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du vent, le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'eldra.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (118, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (A.FEET[0] - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25)[0] for i in range(n)], PW, PH, 'b')
    anims = {nm: pixel_frames(nm) for nm in ('pose', 'attaque', 'speciale')}

    def pixel_at(Tv):
        for a_, s_, e_ in segs:
            if s_ <= Tv < e_:
                nm = {'idle': 'pose', 'attack': 'attaque', 'special': 'speciale'}[a_]
                frames, off = anims[nm]
                tms = (Tv - s_) * 1000
                if nm == 'pose':
                    tms %= sum(d for _, d in frames)
                acc = 0
                for im, d in frames:
                    if tms < acc + d:
                        return im, off
                    acc += d
                return frames[-1][0], off
        return anims['pose'][0][0][0], anims['pose'][1]
    out = []
    for i, p in enumerate(pngs):
        Tv = i / FPS
        left = crop.copy()
        im, (ox, oy) = pixel_at(Tv)
        big = im.resize((round(im.width * SC), round(im.height * SC)), Image.NEAREST)
        layer = Image.new('RGBA', left.size)
        layer.paste(big, (round(feet[0] - (ox + 64) * SC), round(feet[1] - (oy + 116) * SC)), big)
        left.alpha_composite(layer)
        left = left.resize((PW, PH), Image.NEAREST)
        right = crop.resize((PW, PH), Image.NEAREST)
        right.alpha_composite(Image.open(p))
        fr = Image.new('RGBA', (VW, VH), (24, 16, 40, 255))
        y = (VH - PH) // 2
        fr.paste(left, (0, y))
        fr.paste(right, (VW - PW, y))
        q = os.path.join(TMP, 'c%04d.png' % i)
        fr.convert('RGB').save(q)
        out.append(q)
    return out, n


def compose(pngs, w, h, view):
    bg = background(w, h, view)
    bg.alpha_composite(shadow_layer(w, h, view))
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)


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
        moments = [1.0, 1.5, a_s + 0.24, a_s + 0.47, a_s + 0.53, a_s + 0.6, a_s + 0.7, a_s + 0.85,
                   s_s + 0.2, s_s + 0.43, s_s + 0.55, s_s + 0.7, s_s + 0.86, s_s + 1.1, s_s + 1.3, s_s + 1.47,
                   s_s + 1.66, s_s + 1.9, s_s + 2.0, s_s + 2.12]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) if not x.startswith('a') and not x.startswith('s') else
                       (a_s if x[0] == 'a' else s_s) + float(x[1:]) for x in args]
        # les images d'avant (pour les envois du sac et de la boule) sont rendues dans l'ordre
        res = [frame_svg(T, segs) for T in sorted(moments)]
        moments = sorted(moments)
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, 640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = Image.open(p)
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255))
            sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r[0] for r in res], VW, VH, 'a')
    compose(pngs, VW, VH, VIEW)
    names2, n2 = game_size_part()
    allf = pngs + names2
    for i, p in enumerate(allf):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
    mp4 = os.path.join(OUT, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', mp4], check=True)
    # le GIF : la partie 1 seulement (repos ×2, attaque ×2, spéciale), ≈ 400 px de large
    gifp = os.path.join(OUT, 'anim.gif')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-frames:v', str(n),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024),
          '— partie 1 : %.1f s, partie 2 : %.1f s' % (total, n2 / FPS))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
