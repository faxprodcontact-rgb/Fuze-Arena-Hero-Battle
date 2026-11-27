# Ysolde vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/ysolde/build.py)
# — elle danse sur place, attaque de base « Ruban de feu », attaque spéciale « Pirouette de flammes » — dans le style
# lisse de l'interface, à 24 images par seconde (même méthode que Kael : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/ysolde/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/ysolde/
#   python3 refonte-graphique/ui-moderne/heros/ysolde/anim.py --planche [instants…]   # une planche d'images clés (contrôle)
#
# Méthode : le dessin (ysolde.py) est fait de morceaux ; chaque image le redessine dans une POSE (un squelette) : les
# hanches balancent et descendent quand le genou d'appui plie (le pied d'appui reste à plat, la jambe suit par
# cinématique inverse), le buste suit avec un temps de retard, la tête avec un peu plus ; le genou levé bat la mesure ;
# la crinière ondule (une vague qui court jusqu'aux pointes), le pan de jupe et la longue mèche se balancent à
# contretemps ; la flamme de la torche danse. Les deux bras sont placés par cinématique inverse depuis le poignet (le
# coude tourne autour de la vraie jointure ; rien ne se décroche) ; la torche reste dans le poing.
# Les poses clés et les durées reprennent celles du pixel art (même geste : torche ramenée derrière la tête, fouet,
# jambe en développé ; pirouette de plus en plus vite sur la jambe d'appui, arrêt net torche tendue, retour cambrée).
# Effets du feu (mêmes tons que Kael) : ruban de flammes qui ondule et claque, langues de feu, braises, fumée ;
# tourbillon de rubans en hélice (ceux de devant passent devant elle), étincelles d'or qui retombent sur elle (soutien).
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
import ysolde as Y  # noqa: E402
from atelier import sm, lock, ribbon, ellipse, mchain, mT, mR, mapp, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, rot, ang_of, crpath, taper  # noqa: E402

ROOT = Y.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'ysolde')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-ysolde'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-30.0, -24.0, 264.0, 148.5)  # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = Y.GRD
FOE = (194.0, GR - 40)               # le buste de l'ennemi
AXIS = 60.0                          # l'axe de la pirouette (la jambe d'appui)
LAVA = Y.LAVA
FINK = Y.FINK
GOLDFX = ['#fffbe8', '#fff0b0', '#ffd45c', '#e0962e', '#a8601e']
TAU = 2 * math.pi

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


NUM = ['crouch', 'hip', 'lean', 'headx', 'heady', 'tilt', 'trail', 'lift', 'pan', 'lk', 'footx', 'footy', 'armx', 'army',
       'tang', 'nearx', 'neary', 'flare', 'glow', 'spin', 'hw']
PAIRS = {'head': ('headx', 'heady'), 'foot': ('footx', 'footy'), 'arm': ('armx', 'army'), 'near': ('nearx', 'neary')}


def flat(k):
    d = dict(crouch=0, hip=0, lean=0, headx=0, heady=0, tilt=0, trail=0, lift=0, pan=0, lk=0, footx=Y.AF0[0],
             footy=Y.AF0[1], armx=Y.WF0[0], army=Y.WF0[1], tang=0, nearx=Y.WN0[0], neary=Y.WN0[1], flare=0, glow=0,
             spin=0, hw=1.0)
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


# ======================================================================== les actions (poses clés, comme le pixel art)
WF0, AF0, WN0 = Y.WF0, Y.AF0, Y.WN0
# 2) « Ruban de feu » : elle ramène la torche derrière la tête (le buste se cambre, le genou monte), puis la fouette
# par-dessus la tête vers l'avant en dépliant la jambe levée (grand développé) : un ruban de flammes part de la torche
# en ondulant et vient claquer sur l'ennemi ; elle revient en garde.
ATTACK = [
    (0, {}),
    (90, dict(arm=(93.0, 32.0), lean=-1.5, crouch=1.0, hip=1.0, foot=(89.4, 93.4), pan=1.0, lk=1.0, tang=-12, flare=0.4)),
    (310, dict(arm=(89.6, 30.0), lean=-3.0, crouch=1.4, hip=1.0, head=(-1.0, 0.0), tilt=-4, foot=(89.0, 92.0), flare=1.4,
               glow=1.0, tang=-24, pan=1.4, lk=1.2)),
    (360, dict(arm=(100.0, 23.0), lean=1.0, crouch=0.2, hip=0.0, foot=(101.0, 98.0), trail=1.0, lift=1.0, tang=22, flare=1.0,
               glow=0.6, pan=-1.0, hw=1.6)),
    (420, dict(arm=(108.0, 41.0), lean=3.0, hip=-1.0, head=(1.0, 0.0), tilt=3, foot=(108.0, 92.0), trail=1.5, lift=0.6,
               tang=48, pan=-2.0, lk=-1.0, flare=0.8, hw=1.6)),
    (540, dict(arm=(108.0, 41.6), lean=3.2, hip=-1.0, head=(1.0, 0.2), tilt=3, foot=(108.0, 93.0), trail=0.6, tang=42,
               pan=-1.2, lk=-0.6, flare=0.4)),
    (690, dict(arm=(107.5, 42.4), lean=3.0, hip=-1.0, head=(1.0, 0.4), tilt=2.5, foot=(107.0, 94.0), tang=36, pan=-0.4)),
    (790, dict(arm=(103.0, 38.0), lean=1.5, crouch=1.0, hip=0.0, foot=(99.0, 99.0), tang=14, pan=1.0, lk=0.4)),
    (900, dict(arm=(WF0[0], WF0[1] + 0.6), crouch=1.0, hip=1.0, head=(0.0, 0.8), foot=(AF0[0], AF0[1] - 1.2), pan=0.4, lk=1.0)),
    (1020, {}),
]
A_WHIP, A_OUT, A_SNAP = 330, 360, 540        # le fouet, le ruban qui part, le claquement sur l'ennemi

# 3) « Pirouette de flammes » : plié profond, torche tirée en arrière (la flamme enfle), elle se grandit et tourne sur
# sa jambe d'appui de plus en plus vite, des rubans de feu s'enroulent autour d'elle ; arrêt net, torche tendue : le
# tourbillon se détache, file danser autour de l'ennemi et l'embrase ; elle revient cambrée dans sa pose de danse, et
# des étincelles d'or retombent sur elle.
SPECIAL = [
    (0, {}),
    (90, dict(crouch=0.6)),
    (290, dict(crouch=2.0, lean=-1.5, hip=1.0, head=(0.0, 1.0), arm=(93.0, 33.0), foot=(89.0, 93.0), pan=1.0, lk=1.0,
               flare=2.0, glow=1.2, tang=-8)),
    (340, dict(crouch=-0.8, lean=0.0, hip=0.0, head=(0.0, 0.0), arm=(96.0, 30.0), foot=(88.0, 92.0), lift=1.0, flare=1.6,
               glow=1.0, tang=0, spin=0, hw=1.6)),
    (470, dict(crouch=-1.0, arm=(96.0, 29.0), foot=(87.6, 91.6), lift=1.6, trail=0.6, flare=1.6, glow=1.0, spin=120, hw=2.0)),
    (590, dict(crouch=-1.0, arm=(96.0, 29.0), foot=(87.6, 91.6), lift=2.0, trail=1.0, flare=1.8, glow=1.2, spin=330, hw=2.0)),
    (690, dict(crouch=-1.0, arm=(96.0, 29.0), foot=(87.6, 91.6), lift=2.0, trail=1.2, flare=1.8, glow=1.2, spin=570, hw=2.0)),
    (760, dict(crouch=-0.8, arm=(96.0, 29.5), foot=(88.0, 92.0), lift=1.6, trail=1.0, flare=1.6, glow=1.0, spin=720, hw=1.8)),
    (800, dict(arm=(108.0, 41.0), lean=3.0, hip=-1.0, head=(1.0, 0.0), tilt=3, crouch=0.0, tang=44, foot=(99.0, 97.0), trail=1.2,
               lift=0.8, pan=-2.0, lk=-1.0, flare=1.4, glow=0.8, spin=720, hw=1.8)),
    (950, dict(arm=(108.0, 42.0), lean=3.0, hip=-1.0, head=(1.0, 0.2), tilt=2.5, tang=38, foot=(AF0[0] + 1, AF0[1]), pan=-0.6,
               flare=0.8, glow=0.6, spin=720)),
    (1060, dict(arm=(104.0, 38.0), lean=1.5, hip=0.0, tang=18, near=(36.5, 51.0), pan=1.0, spin=720)),
    (1180, dict(arm=(WF0[0], WF0[1] - 1.6), lean=-1.6, hip=1.0, crouch=-0.6, head=(0.0, -1.0), tilt=-3, near=(40.5, 38.0),
                foot=(89.4, 93.0), pan=1.0, lk=1.0, spin=720)),
    (1420, dict(arm=(WF0[0], WF0[1] - 1.4), lean=-1.6, hip=1.0, crouch=-0.6, head=(0.0, -0.8), tilt=-3, near=(40.5, 37.5),
                foot=(89.4, 93.2), pan=0.4, lk=0.8, spin=720)),
    (1560, dict(near=(37.0, 51.0), head=(0.0, 0.8), foot=(AF0[0], AF0[1] - 1.0), pan=-0.6, spin=720)),
    (1710, dict(spin=720)),
]
S_GATHER, S_SPIN0, S_SPIN1, S_LAUNCH, S_ENGULF, S_GOLD = 90, 340, 760, 800, 960, 1150


# ======================================================================== la danse sur place (en boucle)
PER = 1.5                               # deux temps : deux par boucle du repos (1,2 s avant le 27/11, pixel art : 1,18 s)
IDLE_T = 3.0                            # la boucle du repos (s) : danse et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la flamme de la torche enfle lentement et s'éclaire (son cœur blanchit), puis retombe ; ses langues
    lèchent l'air (une par seconde). Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus
    (heros/repos.py)."""
    u = TAU * T / IDLE_T
    return dict(tf=0.5 - 0.5 * math.cos(u), fl=3 * u)


def idle_offsets(T):
    u = TAU * T / PER
    d = dict(crouch=0.9 * (0.5 - 0.5 * math.cos(2 * u)), hip=1.0 * math.sin(u), lean=0.9 * math.sin(u - 0.7),
             headx=0.35 * math.sin(u - 1.3), heady=0.25 * math.sin(2 * u - 1.0), tilt=1.2 * math.sin(u - 1.2),
             footy=-1.5 * (0.5 - 0.5 * math.cos(2 * u - 0.6)), footx=0.4 * math.sin(u),
             pan=-1.2 * math.sin(u - 1.0), lk=1.0 * math.sin(u - 1.7), army=0.5 * math.sin(2 * u - 1.0),
             tang=3.0 * math.sin(u - 0.8), neary=0.9 * math.sin(u - 1.0), nearx=0.3 * math.cos(u - 1.0))
    return d, 0.5 - 0.5 * math.cos(u)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : danse (pondérée) + action en cours."""
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 280)) / 280))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    out = dict(breath=br * w, crouch=P['crouch'], hip=P['hip'], lean=P['lean'], head=(P['headx'], P['heady']),
               tilt=P['tilt'], trail=P['trail'], lift=P['lift'], pan=P['pan'], lk=P['lk'], foot=(P['footx'], P['footy']),
               arm=(P['armx'], P['army']), tang=P['tang'], near=(P['nearx'], P['neary']), flare=P['flare'],
               glow=P['glow'], spin=P['spin'] % 360, hw=P['hw'])
    # la crinière : la vague court sans arrêt (plus vite quand elle tourne ou fouette)
    out['ph'] = TAU * T / 1.0 + (0.004 * P['spin'] if action == 'special' else 0) + 1.5 * P['trail'] * (T - t0 if action else 0)
    sg = signe(T)                                  # le signe du repos : la flamme de la torche (anim.signe)
    out['tf'] = w * sg['tf']
    out['fl'] = sg['fl']                           # (2,2 langues par s avant le 27/11)
    out['blink'] = 1.0 if (w > 0.95 and 1.70 <= (T % IDLE_T) < 1.79) else 0.0
    return out


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, r if ry is None else ry, stops)


def outlined(shapes_fills, ink=FINK, w=1.4, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


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


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S."""
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
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, LAVA[2], 0.6 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
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


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière claire au sol (le pied qui pivote)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.8 * r, cy + 0.2 * r, 0.7 * r), (cx - 0.7 * r, cy + 0.25 * r, 0.65 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f6e4c0'), (0.6, '#d6b68a'), (1, '#a07c64')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3046" stroke="#4a3046" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def fire_ribbon(fig, pts, w, op=1.0, hot=0.0, head_round=True):
    """Un ruban de flammes le long d'une ligne (de la queue à la tête) : fin et cramoisi à la queue, large et clair
    vers la tête, un cœur jaune pâle ; UN contour."""
    if len(pts) < 3 or op <= 0.02:
        return ''
    c = crpath(pts, 40)
    if math.dist(c[0], c[-1]) < 1.0:
        return ''
    n = len(c) - 1
    ws = [max(0.15, w * (0.18 + 0.82 * math.sin(math.pi * 0.5 * min(1, (i / n) * 1.25)) ** 0.9)) for i in range(n + 1)]
    tip = 'round' if head_round else 'sharp'
    sh = taper(c, ws[0], ws[-1], tip=tip, wmid=w)
    core = taper(c[6:], ws[6] * 0.42, ws[-1] * 0.45, tip=tip, wmid=w * 0.45)
    g1 = g_lin(fig, c[0], c[-1], [(0, LAVA[5]), (0.3, LAVA[4]), (0.65, LAVA[3]), (1, LAVA[2])])
    g2 = g_lin(fig, c[6], c[-1], [(0, LAVA[2]), (0.6, LAVA[1]), (1, LAVA[0] if hot > 0.5 else LAVA[1])])
    return outlined([(sh, g1, 1), (core, g2, 0.95)], w=1.3, op=op)


def sparkle(fig, c, r, op=1.0, rot_=0.0):
    """Une étincelle d'or : un signe à quatre pointes aux côtés creusés (un signe inventé), un cœur blanc."""
    if op <= 0.02 or r < 0.2:
        return ''
    pts = []
    for k in range(8):
        a = math.radians(rot_ + 45 * k)
        rr = r if k % 2 == 0 else r * 0.32
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.7)
    gr = g_rad(fig, (c[0] + r * 0.2, c[1] - r * 0.2), r, [(0, GOLDFX[0]), (0.45, GOLDFX[2]), (1, GOLDFX[3])])
    halo = g_rad(fig, c, r * 2.4, [(0, GOLDFX[2], 0.45 * op), (1, GOLDFX[3], 0)])
    return ('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.4), halo)
            + outlined([(sh, gr, 1), (ellipse(c[0], c[1], r * 0.2, r * 0.2), '#ffffff', 1)], ink='#5c2418', w=0.8, op=op))


def pop(fig, c, r, op=1.0):
    """Un petit éclat d'or là où une étincelle la touche : un anneau qui s'ouvre (pas de rayons)."""
    if op <= 0.02:
        return ''
    ring_ = ellipse(c[0], c[1], r, r * 0.8)
    inner = ellipse(c[0], c[1] - 0.1, r * 0.7, r * 0.52)
    from lib import Shape
    band = Shape(ring_.subs + inner.subs, evenodd=True)
    return '<path d="%s" fill-rule="evenodd" fill="%s" opacity="%g"/>' % (band.d(), GOLDFX[1], op)


# ---- la position de la flamme à un instant (pour la traînée du fouet)

def flame_tip(P, up=27.0):
    U = mchain(mT(P['hip'] * 0.8, P['crouch'] * 0.9), mR(P['lean'] * 1.2, *Y.WAIST))
    S = mapp(U, Y.SF0)
    W = Y.reach(S, mapp(U, P['arm']), Y.LUF + Y.LFF)
    T = Y.torch_frame(W, P['tang'])
    return T(-1.0, -up)


# ---- l'attaque de base : le fouet, le ruban de flammes qui ondule et claque

def fx_attack(tl, T):
    def f(fig, ctx):
        tip = ctx['tip']
        # le fouet : une traînée de feu qui suit la flamme par-dessus la tête (les 90 dernières ms)
        if 300 <= tl <= 440:
            hist = []
            for dt in range(90, -1, -15):
                Pp = pose_at(T - dt / 1000.0, 'attack', T - tl / 1000.0)
                hist.append(flame_tip(Pp))
            hist[-1] = tip
            e = env(tl, 300, 330, 400, 440)
            fig.fx_back.append(fire_ribbon(fig, hist, 4.6 * e + 0.5, op=min(1, e * 1.3)))
        # le ruban : il part de la torche en ondulant, sa tête file vers l'ennemi, puis la queue se détache
        if A_OUT <= tl <= A_SNAP + 120:
            s_head = smooth((tl - A_OUT) / (A_SNAP - A_OUT))
            s_tail = smooth((tl - (A_OUT + 90)) / (A_SNAP + 120 - (A_OUT + 90))) * 0.92
            start = tip
            pts = []
            for i in range(25):
                s = s_tail + (s_head - s_tail) * i / 24
                p = lerp(start, FOE, s)
                d = norm(sub(FOE, start))
                nrm = (-d[1], d[0])
                amp = 7.0 * math.sin(math.pi * min(1, s * 1.1)) * (1 - 0.6 * s_head)
                off = amp * math.sin(TAU * 1.6 * s - tl / 1000 * 26)
                pts.append(add(p, nrm, off))
            e = env(tl, A_OUT, A_OUT + 30, A_SNAP + 40, A_SNAP + 120)
            fig.fx_front.append(fire_ribbon(fig, pts, 6.0, op=e, hot=1.0))
        # le claquement : le ruban s'enroule autour de l'ennemi, une gerbe de langues de feu, des braises, la fumée
        tau = (tl - A_SNAP) / 1000.0
        if 0 <= tau <= 0.5:
            c = FOE
            e = env(tau, 0, 0.04, 0.16, 0.34)
            if e > 0:
                ring_ = [(c[0] + 11 * math.cos(a) * (1 - 0.2 * tau), c[1] + 4 + 4.2 * math.sin(a) - 7 * k)
                         for k, a in [(i / 30, -0.6 + TAU * 1.05 * i / 30) for i in range(31)]]
                back = [p for i, p in enumerate(ring_) if math.sin(-0.6 + TAU * 1.05 * i / 30) < 0]
                fig.fx_back.append(fire_ribbon(fig, ring_[:16], 3.6 * e, op=e))
                fig.fx_front.append(fire_ribbon(fig, ring_[14:], 3.6 * e, op=e, hot=1))
                del back
                fig.fx_front.append(tongue(fig, (c[0] + 1, c[1] + 6), 18 * e, 7.0, bend=1.0, lean=0.2))
                fig.fx_front.append(tongue(fig, (c[0] + 7, c[1] + 7), 11 * e, 4.8, bend=-0.8, lean=0.8))
                fig.fx_back.append(tongue(fig, (c[0] - 6, c[1] + 6), 10 * e, 4.4, bend=-1.0, lean=-0.5))
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                    fm(c[0]), fm(c[1]), fm(16 * e), fm(16 * e), g_rad(fig, c, 16 * e, [(0, LAVA[1], 0.6 * e), (0.5, LAVA[2], 0.25 * e), (1, LAVA[3], 0)])))
            for i, (vx, vy) in enumerate(((60, -80), (85, -25), (20, -100), (70, 20), (-30, -70), (45, -50), (95, -50))):
                if tau < 0.5:
                    x, y = ballistic(add(c, (0, 2)), (vx, vy), 160, tau)
                    fig.fx_front.append(ember(fig, x, y, 0.75 if i % 2 else 0.55, op=max(0, 1 - tau / 0.5)))
        if 0.12 < tau < 0.62:
            k = (tau - 0.12) / 0.5
            fig.fx_back.append(smoke(fig, FOE[0] + 3 + 2 * k, FOE[1] - 6 - 14 * k, 2.2 + 3.5 * k, op=0.8 * (1 - k)))
            fig.fx_back.append(smoke(fig, FOE[0] - 4 - 2 * k, FOE[1] - 1 - 9 * k, 1.6 + 2.4 * k, op=0.65 * (1 - k)))
        # la torche s'embrase avant le coup
        if 60 <= tl <= 360:
            e = env(tl, 60, 200, 300, 360)
            for j in range(3):
                a = tl / 1000 * 9 + j * TAU / 3
                p = add(ctx['flame'], (6 * math.cos(a), -2 + 3 * math.sin(a)))
                fig.fx_front.append(ember(fig, p[0], p[1], 0.5, op=0.8 * e))
    return f


# ---- l'attaque spéciale : la pirouette, le tourbillon de rubans, l'ennemi embrasé, la pluie d'or

def helix(cx, ybot, ytop, R, phase, turns, n=60, lean=0.0, squash=0.32):
    """Les points d'une hélice autour d'un axe vertical : (point, profondeur) ; profondeur > 0 = devant."""
    out = []
    for i in range(n + 1):
        s = i / n
        a = phase + TAU * turns * s
        y = ybot + (ytop - ybot) * s
        r = R(s) if callable(R) else R
        out.append(((cx + r * math.cos(a) + lean * s, y + r * squash * math.sin(a)), math.sin(a)))
    return out


def fire_band(fig, pts, ws, op=1.0, hot=0.0):
    """Un morceau de ruban de flammes (largeurs données en chaque point, bouts effilés), dégradé le long, UN contour."""
    if len(pts) < 3 or op <= 0.02 or max(ws) < 0.3:
        return ''
    sh = ribbon(pts, ws)
    core = ribbon(pts, [w_ * 0.42 for w_ in ws])
    g1 = g_lin(fig, pts[0], pts[-1], [(0, LAVA[4]), (0.5, LAVA[3]), (1, LAVA[2])])
    g2 = g_lin(fig, pts[0], pts[-1], [(0, LAVA[2]), (1, LAVA[1] if hot < 0.5 else LAVA[0])])
    return outlined([(sh, g1, 1), (core, g2, 0.9)], w=1.2, op=op)


def vortex(fig, cx, ybot, ytop, R, phase, n_rib=2, turns=1.0, w=4.0, op=1.0):
    """Le tourbillon : des rubans de flammes en hélice (larges au milieu, effilés aux bouts) ; les morceaux de devant
    passent devant elle, ceux de derrière derrière."""
    for j in range(n_rib):
        tj = turns * (1 - 0.18 * j)
        yb = ybot - 4 * j
        yt = ytop + 6 * j
        pts = helix(cx, yb, yt, R, phase + j * TAU / max(2, n_rib) + 0.7 * j, tj, n=48)
        n = len(pts) - 1
        wj = w * (1 - 0.15 * j)
        ws = [0.15 + wj * math.sin(math.pi * i / n) ** 0.8 for i in range(n + 1)]
        run, rw, side = [], [], None
        for (p, dep), w_ in zip(pts, ws):
            sd = dep > 0
            if side is not None and sd != side:
                run.append(p)
                rw.append(0.2)
                (fig.fx_front if side else fig.fx_back).append(fire_band(fig, run, rw, op=op, hot=1 if side else 0))
                run, rw = [p], [0.2]
            else:
                run.append(p)
                rw.append(w_)
            side = sd
        if len(run) > 2:
            rw[-1] = 0.15
            (fig.fx_front if side else fig.fx_back).append(fire_band(fig, run, rw, op=op, hot=1 if side else 0))


def fx_special(tl, T):
    def f(fig, ctx):
        # la préparation : des braises tournent vers la flamme et s'y fondent
        if S_GATHER <= tl <= S_SPIN0 + 40:
            e = env(tl, S_GATHER, S_GATHER + 80, S_SPIN0 - 40, S_SPIN0 + 40)
            for j in range(5):
                k = ((tl - S_GATHER) / 260 + j / 5) % 1
                a = TAU * (j / 5) + 5 * k
                r = 16 * (1 - k)
                p = add(ctx['flame'], (r * math.cos(a), r * 0.7 * math.sin(a)))
                fig.fx_front.append(ember(fig, p[0], p[1], 0.45 + 0.3 * (1 - k), op=e))
        # le tourbillon autour d'elle, de plus en plus grand et serré
        if S_SPIN0 <= tl <= S_LAUNCH:
            k = smooth((tl - S_SPIN0) / (S_SPIN1 - S_SPIN0))
            ph = -(tl - S_SPIN0) / 1000 * (8 + 18 * k)
            nr = 1 if k < 0.45 else 2
            e = min(1.0, (tl - S_SPIN0) / 80)
            vortex(fig, AXIS + 4, GR - 6, GR - 34 - 60 * k, lambda s: 17 + 6 * k + 5 * s, ph, n_rib=nr, turns=0.9 + 0.3 * k,
                   w=4.0 + 2.2 * k, op=e)
            for i in range(3):
                kk = ((tl - S_SPIN0) / 220 + i / 3) % 1
                fig.fx_back.append(dust(fig, AXIS - 6 - 12 * kk + (24 * kk if i % 2 else 0), GR - 1.2 - 2 * kk, 1.4 + 2.2 * kk, op=0.8 * (1 - kk) * e))
        # le tourbillon se détache et file vers l'ennemi
        if S_LAUNCH <= tl <= S_ENGULF + 60:
            k = smooth((tl - S_LAUNCH) / (S_ENGULF - S_LAUNCH))
            cx = AXIS + 4 + (FOE[0] - AXIS - 4) * k
            ph = -(tl - S_SPIN0) / 1000 * 26
            e = env(tl, S_LAUNCH, S_LAUNCH + 20, S_ENGULF, S_ENGULF + 60)
            vortex(fig, cx, GR - 4, GR - 90 + 30 * k, lambda s: (24 - 10 * k) + 3 * s, ph, n_rib=2, turns=1.1, w=5.6 - 1.2 * k, op=e)
        # l'ennemi pris dans la danse de feu, puis embrasé
        tau = (tl - S_ENGULF) / 1000.0
        if -0.06 <= tau <= 0.5:
            c = FOE
            e = env(tau, -0.06, 0.0, 0.2, 0.42)
            ph = -(tl - S_SPIN0) / 1000 * 26
            if e > 0:
                vortex(fig, c[0], GR - 2, GR - 64, lambda s: 14 + 3 * s - 4 * tau, ph, n_rib=2, turns=1.2, w=4.6, op=e)
                fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                    fm(c[0]), fm(c[1]), fm(22 * e), fm(22 * e), g_rad(fig, c, 22 * e, [(0, LAVA[0], 0.75 * e), (0.35, LAVA[2], 0.4 * e), (1, LAVA[3], 0)])))
            g = env(tau, 0.05, 0.14, 0.3, 0.5)
            for x, h, w_, b, l in ((-9, 13, 5.0, 1.0, -0.3), (-3, 22, 7.2, -0.8, 0.2), (4, 17, 6.0, 1.0, 0.4), (10, 11, 4.4, -0.6, 0.7)):
                fig.fx_front.append(tongue(fig, (c[0] + x, GR + 0.5), h * g, w_, bend=b, lean=l))
            for i, (vx, vy) in enumerate(((50, -90), (80, -40), (10, -110), (-40, -80), (100, -10), (-60, -30), (30, -60))):
                if 0.05 < tau < 0.5:
                    x, y = ballistic((c[0], c[1] - 4), (vx, vy), 150, tau - 0.05)
                    fig.fx_front.append(ember(fig, x, y, 0.7 if i % 2 else 0.5, op=max(0, 1 - (tau - 0.05) / 0.45)))
        if 0.25 < tau < 0.85:
            k = (tau - 0.25) / 0.6
            fig.fx_back.append(smoke(fig, FOE[0] + 2 + 3 * k, FOE[1] - 10 - 16 * k, 2.6 + 3.8 * k, op=0.75 * (1 - k)))
            fig.fx_back.append(smoke(fig, FOE[0] - 6 - 2 * k, FOE[1] - 2 - 10 * k, 2.0 + 2.6 * k, op=0.6 * (1 - k)))
        # les étincelles d'or qui retombent sur elle en se balançant (elle reçoit la bénédiction du feu)
        if S_GOLD <= tl <= 1700:
            k = (tl - S_GOLD) / 550
            seeds = [(-30, 0.0, 0), (-14, 1.3, 9), (2, 2.1, 3), (18, 0.7, 12), (-40, 2.8, 6), (10, 3.5, 15), (-4, 4.4, 1),
                     (30, 5.0, 8), (-22, 5.6, 13)]
            for j, (dx, ph, dy) in enumerate(seeds):
                y = -14 + k * 90 + dy
                x = AXIS + 10 + dx + 3 * math.sin(ph + k * 5)
                op = min(1, (1 - k) * 2.2) * (0 if y > 92 else 1)
                if 60 <= x <= 92 and 18 <= y <= 50:
                    op *= 0.0                          # jamais devant le visage
                fig.fx_front.append(sparkle(fig, (x, y), 1.6 if j % 3 == 0 else 1.1, op=op, rot_=20 * k * (1 if j % 2 else -1)))
            for (hx, hy, t0) in ((44, 56, 0.25), (97, 28, 0.3), (32, 60, 0.5), (70, 70, 0.55), (99, 46, 0.7), (76, 88, 0.82)):
                e = env(k, t0, t0 + 0.05, t0 + 0.08, t0 + 0.2)
                if e > 0:
                    fig.fx_front.append(pop(fig, (hx, hy), 1.2 + 1.8 * (k - t0) * 4, op=e))
    return f


def fx_idle(T):
    """Au repos, une braise s'envole de la torche de temps en temps (comme le pixel art)."""
    def f(fig, ctx):
        for j in range(2):
            k = ((T + j * 0.75) / 1.5) % 1          # (1,9 s avant le 27/11 : deux braises par boucle de 3 s)
            base = ctx['flame']
            x = base[0] - 2 - 8 * k + 1.6 * math.sin(k * 9 + j)
            y = base[1] - 8 - 22 * k
            fig.fx_back.append(ember(fig, x, y, 0.55 * (1 - 0.5 * k), op=min(1, (1 - k) * 1.6)))
    return f


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
    """L'ombre au sol sous elle."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 24 * k, fy - 2.6 * k, cx + 24 * k, fy + 2.6 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    seq = [('idle', 2.4), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.2)]
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
    if act:
        tl = (T - t0) * 1000
        fx = [fx_attack(tl, T) if act == 'attack' else fx_special(tl, T)]
    else:
        fx = [fx_idle(T)]
    return Y.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
    """Où le dessin pixel art (image 128 × 120, pieds en (64, 116)) est posé dans une image d'animation."""
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
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-ysolde-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (abs(a[:, :, 0].astype(int) - 232) <= 1) & (abs(a[:, :, 1].astype(int) - 236) <= 1) & (abs(a[:, :, 2].astype(int) - 242) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('ysolde'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du feu (le volcan), le pixel art à gauche et
    le vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (110, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (Y.FEET[0] - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)], PW, PH, 'b')
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
        moments = [0.3, 0.6, a_s + 0.09, a_s + 0.31, a_s + 0.35, a_s + 0.42, a_s + 0.5, a_s + 0.58,
                   s_s + 0.29, s_s + 0.45, s_s + 0.6, s_s + 0.74, s_s + 0.85, s_s + 0.98, s_s + 1.2, s_s + 1.45]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
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
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
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
