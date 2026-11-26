# Rook vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/rook/build.py)
# — respiration, attaque de base « Gerbe de plumes de feu », attaque spéciale « Renaissance du phénix » — dans le
# style lisse de l'interface, à 24 images par seconde (même méthode que Kael : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/rook/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/rook/
#   python3 refonte-graphique/ui-moderne/heros/rook/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (rook.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et se
# penche depuis la taille, la tête suit avec un temps de retard, chaque aile tourne autour de la vraie épaule (le
# poignet se replie ou s'ouvre, les plumes près du corps pendent, toutes traînent un peu derrière le battement), les
# plumes ondulent sans arrêt comme des flammes (une vague qui court vers les pointes des ailes, de la chevelure, de la
# jupe et de la queue), les pattes restent plantées. Les poses clés et les durées reprennent celles du pixel art,
# reliées par des courbes douces sans dépassement. Effets dans le même style : dégradés, un seul contour, courbes ;
# aucun flou SVG ; jamais de rayons droits répétés. La spéciale est un SORT D'ÉQUIPE : tout naît sur elle et s'étend
# en cercle autour d'elle (anneau de flammes d'or, pluie de plumes d'or, phénix de lumière), rien ne vise l'ennemi.
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
import rook as R  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import plume, lerp, rotp  # noqa: E402

ROOT = R.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rook')
TMP = os.path.join(HERE, '_images')
SCRATCH = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-rook'
FPS = 24
VIEW = (-30, -50, 304, 171)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = R.GRD
FOE = (226.0, GR - 36)               # l'ennemi (milieu du corps), devant elle
FIRE = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']        # le feu (comme Kael)
GOLDL = ['#ffffff', '#fff6c8', '#ffe27a', '#ffc23e', '#e8962a', '#a85a1a']       # le feu d'or bienfaisant
FINK = '#3a0c18'                     # le contour des flammes
GINK = '#7a3410'                     # le contour de la lumière d'or


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


BASE = dict(crouch=0, lean=0, lift=0, headx=0, heady=0, tilt=0, wn=0, wf=0, fold=0, foldF=0, q=0, sk=0, fire=0,
            legs_up=0, amp=1)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Gerbe de plumes de feu » (pixel : ATTAQUE) : elle lève très haut ses deux ailes (le buste
# part en arrière, elle se ramasse ; les pointes s'embrasent, tenue frémissante), puis les rabat d'un seul battement
# vers l'avant (croissants de flamme derrière le bout des ailes) : les ailes à plat, le buste penché vers l'ennemi, une
# gerbe de plumes de feu jaillit et file en éventail vers l'ennemi en tirant des traînées courbes ; elles frappent :
# une fleur de flammes et de braises, tenue ; puis la fumée monte pendant que ses ailes remontent (léger rebond).
ATTACK = [
    (0, {}),
    (110, dict(wn=-3, wf=-3, fold=-1.5, foldF=-1.5)),
    (260, dict(crouch=2, lean=-2, head=(-1, -1), tilt=-2, wn=-14, wf=-13, fold=-6, foldF=-6, q=1, sk=1)),
    (400, dict(crouch=3, lean=-3, head=(-1, -1.2), tilt=-3, wn=-18, wf=-17, fold=-8, foldF=-8, q=1.2, sk=1.5)),
    (450, dict(crouch=3, lean=-3.1, head=(-1, -1.2), tilt=-3, wn=-18.5, wf=-17.5, fold=-8.5, foldF=-8.5, q=1.2, sk=1.5)),
    (500, dict(crouch=1, lean=1, head=(0, 0), wn=18, wf=17, fold=9, foldF=9, q=0, sk=0, amp=0.3)),
    (545, dict(crouch=0, lean=3, head=(1, 0), tilt=2, wn=40, wf=38, fold=4, foldF=4, q=-1, sk=-1.5, amp=0.3)),
    (615, dict(crouch=0, lean=3, head=(1, 0.2), tilt=2, wn=44, wf=42, fold=0, foldF=0, q=-1, sk=-1.5, amp=0.5)),
    (700, dict(lean=2.8, head=(1, 0.2), tilt=1.5, wn=40, wf=38, q=-1, sk=-1, amp=0.6)),
    (860, dict(lean=2, head=(1, 0), tilt=1, wn=33, wf=31, q=-0.8, sk=-0.5)),
    (960, dict(lean=1, wn=14, wf=12, fold=-2, foldF=-2)),
    (1070, dict(head=(0, 0.8), wn=-5, wf=-5, fold=-3, foldF=-3, q=1, sk=0.5)),
    (1200, {}),
]
A_BEAT, A_LAUNCH, A_HIT = 450, 545, 700

# 3) L'attaque spéciale « Renaissance du phénix » (pixel : SPECIALE) : elle s'embrase d'or, se ramasse, s'élève d'un
# grand battement (la flamme d'or roule au sol des deux côtés) et ouvre grand ses ailes : un anneau de flammes d'or
# naît autour de sa taille et s'étend en descendant se poser au sol, des plumes d'or pleuvent en cercle, de petites
# taches sombres se détachent de son plumage et s'évaporent (soin, purification) ; puis elle relève les ailes, une
# lueur se rassemble au-dessus de sa tête et un PHÉNIX DE LUMIÈRE DORÉE s'y déploie (résurrection), puis se défait en
# lueurs qui montent. Elle redescend, se pose, replie ses ailes et revient en pose.
SPECIAL = [
    (0, {}),
    (100, dict(crouch=1, wn=-4, wf=-4)),
    (240, dict(crouch=1.2, wn=-9, wf=-9, fire=1, head=(0, -0.6), fold=-3, foldF=-3)),
    (420, dict(crouch=3, lean=-1, wn=-16, wf=-15, fire=1.4, head=(0, -1), fold=-7, foldF=-7, q=1, sk=1)),
    (500, dict(crouch=-1, lift=12, wn=30, wf=30, fire=1.4, fold=8, foldF=8, legs_up=0.6, amp=0.4, sk=-1)),
    (590, dict(lift=22, wn=-12, wf=-12, fire=1.6, fold=-6, foldF=-6, legs_up=1, q=-1, sk=1)),
    (700, dict(lift=22, wn=12, wf=12, fire=2.2, head=(0, -1), fold=2, foldF=2, legs_up=1, q=0.5)),
    (790, dict(lift=22, wn=12, wf=12, fire=2.0, head=(0, -1), fold=2, foldF=2, legs_up=1)),
    (880, dict(lift=21, wn=7, wf=7, fire=1.6, legs_up=1)),
    (970, dict(lift=20, wn=2, wf=2, fire=1.2, legs_up=1)),
    (1060, dict(lift=20, wn=-12, wf=-12, fire=1.5, head=(0, -1), fold=-4, foldF=-4, legs_up=1)),
    (1170, dict(lift=19, wn=-16, wf=-15, fire=2.0, head=(0, -1), tilt=-2, fold=-6, foldF=-6, legs_up=1)),
    (1250, dict(lift=18, wn=-16, wf=-15, fire=2.6, head=(0, -1.2), tilt=-3, fold=-6, foldF=-6, legs_up=1)),
    (1470, dict(lift=15, wn=-10, wf=-10, fire=1.6, head=(0, -0.6), tilt=-1, legs_up=0.8)),
    (1570, dict(lift=8, wn=-5, wf=-5, fire=0.8, legs_up=0.5)),
    (1660, dict(crouch=2, lift=0, wn=3, wf=3, fire=0.3, head=(0, 1), q=-1, sk=-1)),
    (1760, dict(crouch=1, wn=1, wf=1, head=(0, 0.6))),
    (2020, {}),
]
S_HEAL, S_REZ = 590, 1250


# ======================================================================== la respiration (boucle de 1,6 s)

IDLE_T = 1.6


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    d = dict(crouch=0.45 * (0.5 - 0.5 * math.cos(u + math.pi)) ** 2,
             heady=-0.45 * math.sin(u - 1.0), tilt=0.5 * math.sin(u - 1.3),
             wn=-2.2 * math.sin(u - 0.7) - 0.4, wf=-2.2 * math.sin(u - 0.9) - 0.4,
             fold=-1.0 * math.sin(u - 1.3), foldF=-1.0 * math.sin(u - 1.5),
             q=0.9 * math.sin(u - 1.6), sk=0.5 * math.sin(u - 1.9))
    return d, br


def raw_pose(T, action=None, t0=0.0):
    w = 1.0
    act = None
    tl = 0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    # le frémissement de la préparation (tout tremble d'un rien pendant la tenue)
    if action == 'attack' and 260 <= tl <= 450:
        j = math.sin(tl / 1000.0 * 2 * math.pi * 24)
        P['wn'] += 0.8 * j
        P['wf'] -= 0.8 * j
    return P, w * br, tl


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    P, br, tl = raw_pose(T, action, t0)
    Pp, _, _ = raw_pose(T - 1 / 48, action, t0)
    vn = (P['wn'] - Pp['wn']) * 48           # degrés par seconde
    drag = max(-1.3, min(1.3, vn * 0.0035))
    out = dict(breath=br, crouch=P['crouch'], lean=P['lean'], lift=P['lift'], head=(P['headx'], P['heady']),
               tilt=P['tilt'], wn=P['wn'], wf=P['wf'], fold=P['fold'], foldF=P['foldF'], q=P['q'], sk=P['sk'],
               fire=max(0.0, P['fire']), legs_up=max(0.0, min(1.0, P['legs_up'])), amp=P['amp'], drag=drag,
               ph=2 * math.pi * T / 1.25)
    out['blink'] = 1.0 if (action is None and 2.30 <= (T % 4.2) < 2.38) else 0.0
    return out


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, pal=FIRE, ink=FINK, iw=1.2):
    """Une langue de feu : large et pâle à la base, fine et rouge (ou dorée) au bout, en S."""
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
    gout = g_lin(fig, p0, p3, [(0, pal[1]), (0.35, pal[2]), (0.72, pal[3]), (1, pal[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, pal[0]), (0.6, pal[1]), (1, pal[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], ink=ink, w=iw, op=op)


def ember(fig, x, y, r=0.7, op=1.0, pal=FIRE):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, pal[2], 0.55 * op), (1, pal[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, pal[0], op), (0.6, pal[1], op), (1, pal[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def arc_band(C, R_, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R_ * math.cos(a), C[1] + R_ * math.sin(a)))
        inner.append((C[0] + (R_ - ww) * math.cos(a), C[1] + (R_ - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


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


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def feather_fx(fig, tip, ang, L=11.0, w=3.4, op=1.0, gold=False, ink=None):
    """Une plume de feu (ou d'or) qui vole : la tige sombre à l'arrière, la plume rouge-orangé, la pointe jaune vers
    l'avant ; le haut éclairé."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    root = (tip[0] - L * math.cos(a), tip[1] - L * math.sin(a))
    sh = plume(root, ang, L, w, curl=-10, n=10)
    if gold:
        gr = g_lin(fig, root, tip, [(0, GOLDL[4]), (0.5, GOLDL[3]), (0.85, GOLDL[1]), (1, GOLDL[0])])
        ink = ink or GINK
    else:
        gr = g_lin(fig, root, tip, [(0, '#8a1a30'), (0.35, '#e0401e'), (0.75, '#ff9a2a'), (1, '#ffe486')])
        ink = ink or FINK
    vein = ribbon([lerp(root, tip, 0.05), lerp(root, tip, 0.5), lerp(root, tip, 0.85)], [0.1, 0.45, 0.1])
    return outlined([(sh, gr, 1), (vein, '#fff4c0' if gold else '#ffd070', 0.7)], ink=ink, w=1.0, op=op)


# ---- la respiration : des braises qui montent des ailes en ondulant (en boucle)
EMB = [(-4, 30, 0.0, 1.0), (10, 10, 0.3, 0.8), (22, 46, 0.55, 0.9), (112, 20, 0.15, 0.8), (122, 44, 0.7, 1.0),
       (98, 64, 0.4, 0.7), (30, 70, 0.85, 0.7), (60, 2, 0.6, 0.6)]


def fx_embers(T, op=1.0):
    def f(fig, ctx):
        for x, y, ph, s in EMB:
            k = ((T / 1.9) + ph) % 1.0
            yy = y - 26 * k - ctx['P']['lift']
            xx = x + 2.2 * math.sin(6.0 * k + ph * 7)
            o = op * env(k, 0.0, 0.15, 0.6, 1.0)
            fig.fx_front.append(ember(fig, xx, yy, 0.55 * s, o))
    return f


# ---- l'attaque de base

def wing_tip_angle(ctx, near=True):
    S = ctx['SN'] if near else ctx['SF']
    T = ctx['tipN'] if near else ctx['tipF']
    return S, math.dist(S, T), math.degrees(math.atan2(T[1] - S[1], T[0] - S[0]))


VOLLEY = [  # (départ, décalage de l'arrivée, courbure, retard)
    ((96.0, 40.0), (-2.0, -9.0), -26.0, 0.00), ((100.0, 50.0), (0.0, -3.0), -12.0, 0.05),
    ((98.0, 58.0), (2.0, 3.0), 10.0, 0.02), ((104.0, 46.0), (-1.0, 8.0), 22.0, 0.08), ((92.0, 30.0), (1.0, -14.0), -36.0, 0.10),
]


def volley_at(i, k):
    """La position et la direction de la plume i au temps k (0..1) : une courbe qui s'ouvre en éventail puis se
    referme sur l'ennemi."""
    s, off, bow, dl = VOLLEY[i]
    e = (FOE[0] + off[0], FOE[1] + off[1])
    c = ((s[0] + e[0]) / 2, (s[1] + e[1]) / 2 + bow)
    u = max(0.0, min(1.0, (k - dl) / (1 - dl)))
    u = 1 - (1 - u) ** 1.6
    p = ((1 - u) ** 2 * s[0] + 2 * (1 - u) * u * c[0] + u * u * e[0], (1 - u) ** 2 * s[1] + 2 * (1 - u) * u * c[1] + u * u * e[1])
    dx = 2 * (1 - u) * (c[0] - s[0]) + 2 * u * (e[0] - c[0])
    dy = 2 * (1 - u) * (c[1] - s[1]) + 2 * u * (e[1] - c[1])
    return p, math.degrees(math.atan2(dy, dx)), u


def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        # les pointes des ailes s'embrasent pendant la préparation
        kin = env(tl, 150, 330, 480, 620)
        if kin > 0:
            for near in (True, False):
                tip = ctx['tipN'] if near else ctx['tipF']
                for j, (dx, dy, hh) in enumerate(((0, 0, 7.0), (-3 if near else 3, 4, 5.0), (2 if near else -2, 2, 4.0))):
                    fl = 1 + 0.25 * math.sin(tl / 40.0 + j * 2 + (0 if near else 1))
                    fig.fx_front.append(tongue(fig, (tip[0] + dx, tip[1] + dy + 2), hh * kin * fl, 3.2 * kin, bend=0.5 * math.sin(tl / 60 + j),
                                               lean=-0.2 if near else 0.2, op=kin))
                fig.glow(tip[0], tip[1], 9 * kin, 9 * kin, '#ff8a2a', 0.35 * kin)
        # le battement : des croissants de flamme derrière le bout des ailes
        sm_ = env(tl, A_BEAT - 10, A_BEAT + 40, A_BEAT + 70, A_LAUNCH + 60)
        if sm_ > 0:
            for near in (True, False):
                S, Rr, a = wing_tip_angle(ctx, near)
                a_prev = a + (-1 if near else 1) * 60 * sm_
                a0, a1 = (a_prev, a) if near else (a_prev, a)
                body = arc_band(S, Rr + 1.5, a0, a1, 7.0 * sm_)
                core = arc_band(S, Rr + 0.6, a0, a1, 3.0 * sm_)
                pa = (S[0] + Rr * math.cos(math.radians(a0)), S[1] + Rr * math.sin(math.radians(a0)))
                pb = (S[0] + Rr * math.cos(math.radians(a1)), S[1] + Rr * math.sin(math.radians(a1)))
                g1 = g_lin(fig, pa, pb, [(0, FIRE[3], 0), (0.6, FIRE[2], 0.75 * sm_), (1, FIRE[1], 0.95 * sm_)])
                g2 = g_lin(fig, pa, pb, [(0, FIRE[1], 0), (1, FIRE[0], sm_)])
                fig.fx_back.append('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, core.d(), g2))
        # le jaillissement : une gerbe de flamme devant elle, à l'envol des plumes
        fl = env(tl, A_LAUNCH - 15, A_LAUNCH + 15, A_LAUNCH + 40, A_LAUNCH + 140)
        if fl > 0:
            c = (100.0, 46.0)
            fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(c[0]), fm(c[1]), fm(14 * fl), fm(12 * fl), g_rad(fig, c, 14 * fl, [(0, FIRE[0], 0.9 * fl), (0.4, FIRE[2], 0.6 * fl), (1, FIRE[3], 0)])))
            for j, (ang, hh) in enumerate(((-30, 9), (10, 11), (40, 8), (-70, 6))):
                a = math.radians(ang)
                fig.fx_front.append(tongue(fig, (c[0] - 2 * math.cos(a), c[1] - 2 * math.sin(a)), hh * fl, 3.6 * fl, lean=math.cos(a) * 1.3,
                                           bend=0.4 * (j - 1.5), op=fl))
        # la gerbe de plumes de feu : elles filent en éventail et tirent une traînée de flamme courbe
        k = (tl - A_LAUNCH) / (A_HIT - A_LAUNCH)
        if -0.05 < k < 1.12:
            for i in range(len(VOLLEY)):
                p, ang, u = volley_at(i, k)
                if u <= 0:
                    continue
                if k < 1.0:
                    pts = [volley_at(i, k - 0.26 * j / 8)[0] for j in range(9)]
                    pts = [q for q in pts]
                    ws = [2.6 * (1 - j / 8) ** 0.8 + 0.1 for j in range(9)]
                    tr = ribbon(pts, ws)
                    tr2 = ribbon(pts[:6], [w * 0.45 for w in ws[:6]])
                    fig.fx_front.append('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (
                        tr.d(), g_lin(fig, pts[0], pts[-1], [(0, FIRE[2], 0.85), (0.5, FIRE[3], 0.5), (1, FIRE[4], 0)]),
                        tr2.d(), g_lin(fig, pts[0], pts[5], [(0, FIRE[0], 0.9), (1, FIRE[1], 0)])))
                op = 1.0 if k < 1.0 else max(0.0, 1 - (k - 1.0) / 0.1)
                fig.fx_front.append(feather_fx(fig, p, ang, 10.0, 3.4, op))
        # l'impact : une fleur de flammes et de braises, tenue, puis la fumée monte en volutes
        h = env(tl, A_HIT - 10, A_HIT + 40, A_HIT + 150, A_HIT + 300)
        if h > 0:
            base = (FOE[0], FOE[1] + 10)
            fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(FOE[0]), fm(FOE[1]), fm(26 * h), fm(22 * h), g_rad(fig, FOE, 26 * h, [(0, FIRE[1], 0.7 * h), (0.45, FIRE[3], 0.4 * h), (1, FIRE[4], 0)])))
            for j, (dx, hh, ln) in enumerate(((-10, 14, -0.5), (-4, 22, -0.15), (3, 26, 0.1), (9, 19, 0.35), (14, 12, 0.6), (-15, 9, -0.7))):
                fl_ = 1 + 0.18 * math.sin(tl / 35.0 + j * 1.9)
                fig.fx_front.append(tongue(fig, (base[0] + dx, base[1] + 4), hh * h * fl_, 6.0 * h, bend=0.6 * math.sin(j * 2.1), lean=ln, op=min(1, h * 1.3)))
        if A_HIT <= tl <= A_HIT + 520:
            t = (tl - A_HIT) / 1000
            for j, (vx, vy) in enumerate(((-40, -90), (-12, -120), (18, -110), (44, -80), (-60, -50), (60, -60), (6, -140))):
                p = ballistic(FOE, (vx, vy), 260, t)
                o = max(0.0, 1 - (tl - A_HIT) / 520)
                fig.fx_front.append(ember(fig, p[0], p[1], 0.75 if j % 2 else 0.55, o))
        sk = env(tl, A_HIT + 120, A_HIT + 260, A_HIT + 380, 1200)
        if sk > 0:
            t = (tl - A_HIT - 120) / 1000
            for j, (dx, r0, sp) in enumerate(((-6, 3.4, 26), (5, 2.8, 32), (0, 4.0, 22), (-11, 2.4, 30))):
                cy = FOE[1] + 4 - sp * t - 2 * j
                fig.fx_front.append(smoke(fig, FOE[0] + dx + 3 * math.sin(t * 6 + j), cy, r0 * (0.6 + 1.2 * t), sk * 0.85))
    return f


# ---- l'attaque spéciale

SPECKS = [(58, 66), (64, 82), (78, 84), (71, 88), (44, 62), (102, 60)]


def gold_feather_rain(fig, ctx, tl):
    """La pluie de plumes d'or : elles naissent au-dessus d'elle et pleuvent en cercle tout autour, en s'écartant,
    se posent au sol (une petite lueur) ; celles du côté lointain passent derrière elle."""
    cx = 70.0
    for j in range(14):
        a = math.radians(j * 360 / 14 + 11 * math.sin(j * 2.3))
        t0 = S_HEAL + 40 * (j % 5) + 25 * (j % 3)
        k = (tl - t0) / 620
        if k <= 0 or k > 1.25:
            continue
        R_ = 30 + (28 + 8 * math.sin(j * 1.7)) * ease(min(1, k))
        y0 = -12 - ctx['P']['lift'] * 0.5
        y1 = GR + 2 + 6 * math.sin(a)
        y = y0 + (y1 - y0) * min(1, k) ** 1.4
        x = cx + R_ * math.cos(a)
        y += 0.0
        back = math.sin(a) < 0
        sway = 30 * math.sin(k * 7 + j)
        op = 1.0 if k < 0.9 else max(0.0, 1 - (k - 0.9) / 0.35)
        s = feather_fx(fig, (x, y), (180 if math.cos(a) < 0 else 0) + 25 + sway, 7.4, 3.0, op, gold=True)
        (fig.fx_back if back else fig.fx_front).append(s)
        if k > 0.95:
            fig.fx_back.append(ember(fig, x, y1 - 1, 0.6, op, pal=GOLDL))


def ring(fig, ctx, k, op=1.0):
    """L'anneau de flammes d'or : une ellipse posée (aplatie), la moitié lointaine derrière elle, la moitié proche
    devant ; de petites langues dansent dessus ; il s'éteint en petites langues."""
    lift = ctx['P']['lift']
    yc0 = 74 - lift
    e = ease(k)
    c = (70.0, yc0 + (GR - yc0) * e)
    rx = 14 + 52 * e
    ry = rx * 0.26
    w = 3.2 * (1 - 0.5 * e)
    fade = op * (1.0 if k < 0.7 else max(0.0, 1 - (k - 0.7) / 0.3))
    if fade <= 0.02:
        return
    ph = k * 9
    hmax = (5.0 - 2.0 * e) * (1.25 if k > 0.7 else 1.0)
    for half, lst in ((0, fig.fx_back), (1, fig.fx_front)):
        a0, a1 = (180, 360) if half == 0 else (0, 180)
        top, bot = [], []
        for i in range(0, 61):
            ad = a0 + (a1 - a0) * i / 60
            ar = math.radians(ad)
            x = c[0] + rx * math.cos(ar)
            y = c[1] + ry * math.sin(ar)
            # des flammes douces sur le dessus de l'anneau : des vagues inégales, penchées, qui dansent
            wv = max(0.0, math.sin(ar * 7 + ph + 0.8 * math.sin(ar * 3))) ** 1.6
            h = w * 0.5 + hmax * wv * (0.75 + 0.25 * math.sin(ar * 5 + 1.3))
            top.append((x + 0.35 * h * math.cos(ar + 1.2), y - h))
            bot.append((x, y + w * 0.5))
        band = sm(top + bot[::-1], sharp=(0, 60, 61, 121), t=0.8)
        core = sm([(p[0], (p[1] + q[1]) / 2 + 0.4) for p, q in zip(top, bot)] + bot[::-1], sharp=(0, 60, 61, 121), t=0.8)
        gr = g_lin(fig, (c[0], c[1] - ry - hmax), (c[0], c[1] + ry + w), [(0, GOLDL[3]), (0.4, GOLDL[2]), (1, GOLDL[4])])
        gc = g_lin(fig, (c[0], c[1] - ry), (c[0], c[1] + ry), [(0, GOLDL[0]), (1, GOLDL[1])])
        lst.append(outlined([(band, gr, 1), (core, gc, 0.85)], ink=GINK, w=0.9, op=fade * (0.85 if half == 0 else 1)))


def phoenix(fig, c, open_=1.0, op=1.0, ph=0.0):
    """Le phénix de lumière dorée, DE FACE : corps en goutte au cœur blanc, tête ronde (bec et œil de trois quarts vers
    la droite), huppe de trois petites flammes, deux ailes de longues plumes-flammes grandes ouvertes, une queue de
    rubans qui tombent en éventail. Rend (devant, derrière)."""
    if op <= 0.02:
        return '', ''
    cx, cy = c
    shapes = []
    tails = []
    gw = lambda p0, p3: g_lin(fig, p0, p3, [(0, GOLDL[0]), (0.35, GOLDL[1]), (0.7, GOLDL[2]), (1, GOLDL[3])])
    # les ailes : un bras de lumière qui monte en courbe vers l'extérieur, et dessous des plumes-flammes qui pendent
    # vers l'extérieur (comme ses propres ailes : on lit une aile d'oiseau, pas des rayons)
    from atelier import limb
    for s in (-1, 1):
        o = open_
        sh_ = (cx + s * 2.6, cy - 2.0)
        el = (cx + s * (6 + 9 * o), cy - 4 - 9 * o)
        tp = (cx + s * (10 + 22 * o), cy - 8 - 12 * o + 2 * math.sin(ph))
        arm = [sh_, lerp(sh_, el, 0.5), el, lerp(el, tp, 0.5), tp]
        for j in range(5):
            t = 0.15 + 0.8 * j / 4
            seg = int(t * 4)
            p0 = lerp(arm[min(seg, 3)], arm[min(seg, 3) + 1], t * 4 - min(seg, 3))
            ang = math.radians(90 - s * (20 + 32 * t) * (0.4 + 0.6 * o))
            L = (9 + 9 * t) * (0.6 + 0.4 * o)
            dx, dy = math.cos(ang), math.sin(ang)
            if s < 0:
                dx = -dx if dx > 0 else dx
            else:
                dx = abs(dx)
            p3 = (p0[0] + dx * L, p0[1] + dy * L)
            p1 = lerp(p0, p3, 0.35)
            p2 = lerp(p0, p3, 0.7)
            p2 = (p2[0] + s * 1.2, p2[1])
            p3 = (p3[0] + s * 2.0, p3[1] - 2.2)
            shapes.append((lock(p0, p1, p2, p3, 4.2, n=10, bulge=0.25), gw(p0, p3), 1))
        shapes.append((limb(arm, [3.6, 3.2, 2.8, 2.0, 1.0]), g_lin(fig, sh_, tp, [(0, GOLDL[0]), (1, GOLDL[1])]), 1))
    # la queue : des rubans qui tombent en éventail (derrière elle)
    for j, (a, L) in enumerate(((100, 26), (88, 30), (76, 24), (112, 22), (64, 20))):
        aa = math.radians(a + 5 * math.sin(ph * 1.3 + j))
        p0 = (cx, cy + 4)
        p3 = (cx + L * math.cos(aa), cy + 4 + L * math.sin(aa))
        p1 = (lerp(p0, p3, 0.35)[0] + 3 * math.sin(j + ph), lerp(p0, p3, 0.35)[1])
        p2 = (lerp(p0, p3, 0.7)[0] - 3 * math.sin(j + ph), lerp(p0, p3, 0.7)[1])
        tails.append((lock(p0, p1, p2, p3, 3.6, n=10, bulge=0.2), gw(p0, p3), 1))
    # le corps en goutte, la tête, la huppe, le bec
    body = sm([(cx, cy - 7), (cx + 3.4, cy - 2), (cx + 3.0, cy + 4), (cx, cy + 9), (cx - 3.0, cy + 4), (cx - 3.4, cy - 2)], sharp=(3,), t=0.9)
    head = ellipse(cx + 0.4, cy - 8.4, 2.9, 2.7)
    crest = []
    for j, (dx, hh, ln) in enumerate(((-1.2, 4.6, -0.5), (0.4, 6.0, -0.1), (1.8, 4.4, 0.3))):
        b = (cx + dx, cy - 10.6)
        crest.append((lock(b, (b[0] + ln, b[1] - hh * 0.4), (b[0] + ln * 2, b[1] - hh * 0.7), (b[0] + ln * 3, b[1] - hh), 1.8, n=8), gw(b, (b[0], b[1] - hh)), 1))
    beak = sm([(cx + 2.8, cy - 9.0), (cx + 5.4, cy - 8.2), (cx + 2.8, cy - 7.2)], sharp=(0, 1, 2), t=0.4)
    shapes += crest + [(body, g_rad(fig, (cx + 0.6, cy - 1), 9, [(0, GOLDL[0]), (0.5, GOLDL[1]), (1, GOLDL[3])]), 1),
                       (head, g_rad(fig, (cx + 1, cy - 9), 3.4, [(0, GOLDL[0]), (1, GOLDL[2])]), 1),
                       (beak, GOLDL[3], 1), (ellipse(cx + 1.6, cy - 8.8, 0.5, 0.55), '#a85a1a', 1)]
    glow = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(cx), fm(cy - 2), fm(40 * open_ + 6), fm(22 * open_ + 6),
                                                                    g_rad(fig, (cx, cy - 2), 40 * open_ + 6, [(0, GOLDL[1], 0.55 * op), (0.5, GOLDL[2], 0.22 * op), (1, GOLDL[3], 0)]))
    front = glow + outlined(shapes, ink=GINK, w=1.1, op=op)
    back = outlined(tails, ink=GINK, w=1.0, op=op)
    return front, back


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        feet = ctx['feet']
        lift = P['lift']
        # la flaque de lumière d'or au sol, l'aura dorée
        gl = env(tl, 120, 420, 1500, 1800)
        if gl > 0:
            fig.under.append((70, GR, 46 * gl, 8 * gl, GOLDL[2], 0.5 * gl, None))
            fig.glow(70, 56 - lift, 60, 52, '#ffc84a', 0.22 * gl)
        # l'envol : la flamme d'or roule au sol des deux côtés
        to = env(tl, 400, 440, 520, 720)
        if to > 0:
            k = (tl - 400) / 320
            for s in (-1, 1):
                for j, (dx, hh) in enumerate(((10, 7), (18, 10), (27, 6), (35, 4))):
                    x = 70 + s * (dx + 22 * k)
                    fig.fx_front.append(tongue(fig, (x, GR + 1), hh * to * (1 - 0.3 * j / 3), 4.0, bend=0.5 * s, lean=0.5 * s,
                                               op=to, pal=GOLDL, ink=GINK, iw=1.0))
        # le battement d'or : des croissants derrière le bout des ailes
        sm_ = env(tl, 410, 460, 500, 580)
        if sm_ > 0:
            for near in (True, False):
                S, Rr, a = wing_tip_angle(ctx, near)
                a_prev = a + (-1 if near else 1) * 55 * sm_
                body = arc_band(S, Rr + 1.5, a_prev, a, 6.0 * sm_)
                pa = (S[0] + Rr * math.cos(math.radians(a_prev)), S[1] + Rr * math.sin(math.radians(a_prev)))
                pb = (S[0] + Rr * math.cos(math.radians(a)), S[1] + Rr * math.sin(math.radians(a)))
                fig.fx_back.append('<path d="%s" fill="%s"/>' % (body.d(), g_lin(fig, pa, pb, [(0, GOLDL[3], 0), (1, GOLDL[1], 0.9 * sm_)])))
        # de petites langues d'or dansent sur ses bords (elle s'embrase)
        fi = P['fire']
        if fi > 0.3:
            for key in ('tipN', 'tipF'):
                p = ctx[key]
                fig.glow(p[0], p[1], 12, 12, '#ffd860', 0.35 * min(1, fi / 1.5))
        # la purification : de petites taches sombres sur son plumage, qui se détachent, montent et s'évaporent
        sp = env(tl, 240, 330, 590, 1000)
        if sp > 0:
            for j, p0 in enumerate(SPECKS):
                p = R.mapp(ctx['BODY'], p0)
                k = max(0.0, (tl - S_HEAL - 30 * j) / 380)
                y = p[1] - 30 * ease(k) - 4 * k
                x = p[0] + 4 * math.sin(k * 5 + j)
                r = 0.95 * (1 - 0.4 * k)
                col = '#3a2238' if k < 0.4 else ('#6a5470' if k < 0.75 else '#a898a8')
                sh = sm([(x - r, y), (x - 0.2 * r, y - 1.1 * r), (x + r, y - 0.3 * r), (x + 0.6 * r, y + r), (x - 0.5 * r, y + 0.8 * r)], t=0.9)
                fig.fx_front.append(outlined([(sh, col, 1)], ink='#1f1238', w=0.6, op=sp * (1 - ease((k - 0.5) / 0.5)) if k > 0.5 else sp))
        # l'anneau de flammes d'or (soin) : il naît autour de sa taille et s'étend en descendant se poser au sol
        k = (tl - S_HEAL) / 640
        if 0 <= k <= 1.0:
            ring(fig, ctx, k)
        # la pluie de plumes d'or
        if tl > S_HEAL:
            gold_feather_rain(fig, ctx, tl)
        # le phénix de lumière dorée (résurrection)
        if 1040 <= tl <= 1680:
            hp = ctx['head']
            gather = env(tl, 1040, 1140, 1180, 1260)
            if gather > 0:
                c = (hp[0] - 4, hp[1] - 32)
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(7 * gather), g_rad(fig, c, 7 * gather, [(0, GOLDL[0], gather), (0.5, GOLDL[2], 0.7 * gather), (1, GOLDL[3], 0)])))
            op_ = env(tl, 1150, 1250, 1470, 1640)
            if op_ > 0:
                open_ = ease((tl - 1150) / 100) if tl < 1250 else 1.0 + 0.06 * math.sin((tl - 1250) / 50)
                rise = max(0.0, (tl - 1470) / 1000) * 30
                c = (hp[0] - 4, hp[1] - 34 - rise)
                front, back = phoenix(fig, c, open_, op_, tl / 90.0)
                fig.fx_back.append(back)
                fig.fx_front.append(front)
            # l'anneau d'or qui pulse au sol
            pu = env(tl, 1230, 1270, 1330, 1600)
            if pu > 0:
                r = 30 + 26 * ease((tl - 1230) / 370)
                band = ellipse(70, GR, r, r * 0.24).hole(ellipse(70, GR, r - 2.2, r * 0.24 - 0.8))
                fig.fx_back.append('<path d="%s" fill-rule="evenodd" fill="%s" opacity="%g"/>' % (band.d(), GOLDL[2], 0.8 * pu))
            # il se défait en lueurs qui montent et s'écartent
            if tl > 1440:
                k = (tl - 1440) / 260
                for j in range(8):
                    a = math.radians(j * 45 + 20)
                    p = (hp[0] - 2 + 30 * k * math.cos(a), hp[1] - 26 - 24 * k + 10 * k * math.sin(a))
                    fig.fx_front.append(ember(fig, p[0], p[1], 0.8, max(0.0, 1 - k), pal=GOLDL))
        # elle se pose : une bouffée de lumière d'or au sol
        ld = env(tl, 1640, 1680, 1760, 1960)
        if ld > 0:
            k = (tl - 1640) / 320
            for s in (-1, 1):
                for j in range(3):
                    x = 70 + s * (10 + 12 * k + 6 * j)
                    fig.fx_front.append(ember(fig, x, GR - 1 - 4 * k * (j + 1), 0.7, ld, pal=GOLDL))
            fig.under.append((70, GR, 34 * ld, 5 * ld, GOLDL[2], 0.4 * ld, None))
    return f


# ======================================================================== la vidéo

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
    glow_ = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow_).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow_.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, lift, floor_y=GR):
    """L'ombre douce sous elle (elle rétrécit et pâlit quand elle s'élève)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    cx = (66 - x0) * k
    s = max(0.45, 1 - lift / 40)
    sh = Image.new('RGBA', (w, h))
    ImageDraw.Draw(sh).ellipse([cx - 50 * k * s, fy - 3.0 * k * s, cx + 50 * k * s, fy + 3.0 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    seq = [('idle', 3.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_at(T, segs):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    return act, t0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = frame_at(T, segs)
    P = pose_at(T, act, t0)
    fx = [fx_embers(T, 0.0 if act == 'special' else 1.0)]
    if act:
        tl = (T - t0) * 1000
        fx.append(fx_attack(tl) if act == 'attack' else fx_special(tl))
    return R.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P['lift']


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
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1], best[2]


SPRITE = os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'assassins-5.webp')
SPRITE_FEET = (61, 128)          # les pieds dans l'image pixel de la pose (src/game/hd-figures.ts)


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées
    et la place du dessin de la pose dans ces images."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-rook-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(SPRITE)
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du feu, le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (100, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (64 - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
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
        layer.paste(big, (round(feet[0] - (ox + SPRITE_FEET[0]) * SC), round(feet[1] - (oy + SPRITE_FEET[1]) * SC)), big)
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
        moments = [0.4, 1.2, a_s + 0.3, a_s + 0.44, a_s + 0.5, a_s + 0.6, a_s + 0.72, a_s + 0.95,
                   s_s + 0.3, s_s + 0.48, s_s + 0.62, s_s + 0.8, s_s + 1.1, s_s + 1.3, s_s + 1.55, s_s + 1.75]
        args = [x for x in sys.argv[2:] if not x.startswith('--')]
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r_[0] for r_ in res], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, res[i][1]))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(SCRATCH, exist_ok=True)
        dst = os.path.join(SCRATCH, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r_[0] for r_ in res], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, res[i][1]))
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
    if '--sans-jeu' in sys.argv:
        names2, n2 = [], 0
    else:
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
