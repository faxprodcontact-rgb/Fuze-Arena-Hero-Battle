# Elvyn vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/elyon/build.py) —
# respiration, attaque de base « l'orbe de la perle », attaque spéciale « Dragon des marées » — dans le style lisse de
# l'interface (même méthode que Kael : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/elvyn/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/elvyn/)
#   python3 refonte-graphique/ui-moderne/heros/elvyn/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (elvyn.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui respire et se
# penche depuis les hanches, tête, crinière et houppe qui ondulent, queue en crosse, manches, barbillon ; le bras du fond
# suit le poignet, qui tient la perle). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps :
# il ramène la perle contre lui, la charge, la tend d'un coup) et sont reliées par des courbes douces sans dépassement
# (24 images par seconde). Les effets d'eau (bras d'eau qui tournent, orbe à traîne torsadée, éclaboussures, gouttes,
# bulles, écume, le dragon d'eau qui serpente) sont dessinés dans le même style : dégradés, un seul contour, aucun flou.
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
import elvyn as E  # noqa: E402
from atelier import Mat, lock, sm, ribbon, limb, ellipse, xf, resample, sides, f as fm  # noqa: E402

ROOT = E.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'elvyn')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-elvyn') + '/_images'
FPS = 24
GR = E.GRD
VIEW = (-41, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9) : mêmes écarts que Kael
VW, VH = 1280, 720
WINK = '#16205a'                     # le contour des effets d'eau (indigo, comme les creux des écailles)
WA = E.WATER                         # blanc, écume, lumière, eau, ombre, profond, creux
FOE = (177.0, 77.0)                  # l'ennemi (milieu du corps), là où frappent l'orbe et le dragon
WMAT = Mat('#ffffff', '#8ae2f8', '#3eb0e8', '#2276ce', '#1a469c', glint='#ffffff')
FOAM = Mat('#ffffff', '#f4fdff', '#d2f2fc', '#94cfee', '#5a96d6')

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


NUM = ['crouch', 'lean', 'tilt', 'mane', 'tail', 'tuft', 'sn', 'sf', 'barb', 'glow', 'hrot', 'jaw', 'wx', 'wy',
       'headx', 'heady']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, mane=0, tail=0, tuft=0, sn=0, sf=0, barb=0, glow=0, hrot=0, jaw=0,
             wx=E.W0[0], wy=E.W0[1], headx=0, heady=0)
    for key, v in k.items():
        if key == 'wrist':
            d['wx'], d['wy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# 2) L'attaque de base « l'orbe de la perle » (pixel : ATTAQUE) : il ramène la perle contre lui (le bras se replie, il
# recule le buste, la tête se baisse) ; des bras d'eau tournent autour de la perle et une boule d'eau s'y forme. Il tend
# le bras d'un coup : l'orbe part avec sa traîne torsadée et éclate sur l'ennemi en éventail d'eau et en gouttes. Le
# bras revient, la queue et les manches finissent leur balancement.
ATTACK = [
    (0, {}),
    (130, dict(wrist=(76.4, 53.0), hrot=-8, lean=-1, head=(-0.8, 0.8), tail=1, tuft=1, sn=1, sf=1, mane=0.6, barb=1, glow=1)),
    (340, dict(wrist=(74.6, 53.8), hrot=-12, lean=-2.2, crouch=1, head=(-1, 1), tilt=-2, tail=2, tuft=2, sn=1, sf=1.5, mane=1, barb=1, glow=2)),
    (395, dict(wrist=(84.2, 48.4), hrot=6, lean=2, crouch=0, head=(1, 0), tilt=1.5, tail=-1, tuft=1, sn=-1, sf=-1.6, mane=-1, barb=-1.5, glow=1)),
    (470, dict(wrist=(84.6, 48.2), hrot=7, lean=2.2, head=(1.1, 0), tilt=1.8, tail=-2, tuft=-1, sn=-1, sf=-1.2, mane=-1, barb=-2, glow=0.6)),
    (640, dict(wrist=(83.8, 48.8), hrot=5, lean=2, head=(1, 0), tilt=1.2, tail=-1, tuft=-2, sn=0.4, sf=-0.6, mane=-0.6, barb=-1)),
    (800, dict(wrist=(82.0, 50.0), hrot=2, lean=1, head=(0.4, 0), tail=0.6, tuft=-1, sn=1, sf=0.6, mane=0.3, barb=0.5)),
    (960, dict(wrist=(80.6, 51.0), crouch=0.7, tail=1, tuft=0.6, sn=0.3, sf=0.8, mane=0.6, barb=1)),
    (1150, dict(tuft=0.5, sf=0.2, mane=0.2)),
    (1300, {}),
]
ATT_CHARGE = (60, 395)          # les bras d'eau tournent autour de la perle
ATT_FORM = (150, 395)           # la boule d'eau se forme
ATT_FIRE, ATT_HIT = 395, 545    # l'orbe part, l'orbe éclate

# 3) L'attaque spéciale « Dragon des marées » (pixel : SPECIALE) : il se dresse, ramène la perle et l'éveille (des bras
# d'eau tournent autour d'elle, des bulles montent du sol vers la perle). Il la tend vers le ciel : un dragon d'eau en
# jaillit (gueule ouverte, yeux d'or comme les siens, crinière d'écume), serpente dans les airs, plonge sur l'ennemi.
# Éclat d'écume et arrêt sur l'image, puis le dragon se défait de la queue vers la tête en gouttes et en bulles, l'écume
# roule au sol en volutes. Pas de vague, pas de coup : c'est l'esprit de la perle qui frappe.
SPECIAL = [
    (0, {}),
    (160, dict(wrist=(76.4, 53.0), hrot=-8, crouch=1, lean=-1, head=(0, 1), tail=1, tuft=1, sn=1, sf=1, mane=0.6, barb=1, glow=1)),
    (400, dict(wrist=(74.6, 52.0), hrot=-10, crouch=-1.2, lean=-2, head=(-1, -1), tilt=-2, tail=2, tuft=1, sn=1, sf=1, mane=1, barb=1, glow=2)),
    (700, dict(wrist=(74.2, 51.6), hrot=-12, crouch=-2, lean=-2.2, head=(-1, -1.2), tilt=-2.5, tail=2, tuft=2, sn=0.5, sf=1.2, mane=1, barb=0.6, glow=2.4)),
    (790, dict(wrist=(82.6, 39.4), hrot=-28, crouch=-2, lean=1, head=(1, -1), tilt=3, jaw=0.35, tail=-1, tuft=1, sn=-1, sf=-1.5, mane=-1, barb=-1.5, glow=2.4)),
    (900, dict(wrist=(83.4, 38.6), hrot=-30, crouch=-2.2, lean=1.2, head=(1, -1.2), tilt=3.5, jaw=0.3, tail=-2, tuft=-1, sn=-1, sf=-1.2, mane=-1, barb=-2, glow=2)),
    (1180, dict(wrist=(83.0, 39.4), hrot=-26, crouch=-1.4, lean=2, head=(1, -0.6), tilt=2.5, jaw=0.15, tail=-1, tuft=-2, sf=-0.8, mane=-0.8, barb=-1, glow=1.6)),
    (1300, dict(wrist=(83.2, 40.6), hrot=-22, crouch=-0.8, lean=2.2, head=(1.1, 0), tilt=2, tail=0, tuft=-1, sn=1, sf=-0.4, mane=-0.5, glow=1.2)),
    (1520, dict(wrist=(82.6, 44.2), hrot=-14, crouch=0, lean=1.6, head=(1, 0), tilt=1, tail=1, tuft=0, sn=1, sf=0.6, mane=0.4, barb=1, glow=0.6)),
    (1760, dict(wrist=(81.4, 48.6), hrot=-5, lean=0.8, head=(0.4, 0), tail=0.6, tuft=1, sn=-0.6, sf=0.8, mane=0.6, barb=0.6)),
    (1980, dict(crouch=0.8, tail=-0.6, tuft=0.6, sn=-0.5, sf=0.2, mane=-0.3, barb=-0.4)),
    (2200, dict(tuft=-0.3)),
    (2400, {}),
]
SP_GATHER = (60, 760)           # bras d'eau autour de la perle, bulles qui montent
SP_EMERGE = 760                 # le dragon jaillit de la perle
SP_HIT = 1260                   # il plonge sur l'ennemi (éclat d'écume, arrêt sur l'image)


# ======================================================================== la respiration (en boucle, 3 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la perle d'eau s'éveille lentement dans sa paume (elle s'éclaire, sa lueur grandit) et la houppe
    blanche au bout de la queue se balance (ses mèches ondulent). La crinière, trop grande pour les menus (mémoire
    graphique), garde sa petite ondulation au combat seulement (pose_at).
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(glow=1.4 * (0.5 - 0.5 * math.cos(u)), tuft=2.4 * math.sin(u - 0.5), pt=3 * u)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.35 * (0.5 - 0.5 * math.cos(u - 1.4)), heady=0.3 * math.sin(u - 0.6),
                tilt=0.6 * math.sin(u - 0.9), mane=0.5 * math.sin(u - 1.2), tail=0.9 * math.sin(u),
                tuft=0.9 * math.sin(u - 0.9), sn=0.6 * math.sin(u - 1.9), sf=0.7 * math.sin(u - 2.8),
                barb=0.8 * math.sin(u - 1.6), glow=0.25 * (0.5 - 0.5 * math.cos(u - 2.2)), wy=0.25 * math.sin(u - 1.0))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    P = {}
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['wrist'] = (P.pop('wx'), P.pop('wy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    sg = signe(T)
    P['glow'] += w * sg['glow']
    P['tuft'] += w * sg['tuft']
    P['ph'] = 2 * 2 * math.pi * T / IDLE_T          # la crinière : deux vagues par boucle du repos
    P['pt'] = sg['pt']
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return P


# ======================================================================== les effets d'eau (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, o in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl, '' if o == 1 else ' opacity="%g"' % o)
                  for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def under(sh, dx=0.6, dy=-1.6):
    from lib import Shape
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def wdrop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte d'eau : ronde devant, effilée derrière (dans le sens de sa course), un éclat blanc."""
    if op <= 0.02:
        return ''
    a = math.atan2(vy, vx) if (vx or vy) else math.pi / 2
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, WA[1]), (0.45, WA[2]), (1, WA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.3, y - r * 0.3, r * 0.36, r * 0.26), '#ffffff', 0.95)], w=1.0, op=op)


def bubble(fig, x, y, r=1.4, op=1.0):
    """Une bulle : un rond d'eau claire, le bord plus soutenu, un reflet blanc en haut à droite."""
    if op <= 0.02 or r < 0.2:
        return ''
    c = ellipse(x, y, r, r)
    gr = g_rad(fig, (x - r * 0.25, y + r * 0.25), r * 1.1, [(0, WA[1], 0.25), (0.65, WA[2], 0.55), (1, WA[3], 0.95)])
    return outlined([(c, gr, 1), (ellipse(x + r * 0.38, y - r * 0.38, r * 0.34, r * 0.22, -40), '#ffffff', 1),
                     (ellipse(x - r * 0.42, y + r * 0.45, r * 0.14, r * 0.1, -40), '#ffffff', 0.7)], w=0.8, op=op)


def foam(fig, cx, cy, r, op=1.0):
    """Une bouffée d'écume : quelques boules réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.8 * r, cy + 0.25 * r, 0.72 * r), (cx - 0.82 * r, cy + 0.3 * r, 0.68 * r), (cx + 0.12 * r, cy - 0.55 * r, 0.6 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#ffffff'), (0.5, WA[1]), (1, '#8fc8ec')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), WINK, WINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def jet(fig, base, h, w, ang, bend=0.0, op=1.0):
    """Un jet d'eau qui part de `base` dans la direction `ang` (degrés, y vers le bas) : large et sombre au pied, fin et
    blanc d'écume au bout, en S."""
    if h < 0.6 or op <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    P_ = lambda s, o: (base[0] + u[0] * s + n[0] * o, base[1] + u[1] * s + n[1] * o)   # noqa: E731
    p0, p1, p2, p3 = P_(0, 0), P_(h * 0.33, bend * w * 0.6), P_(h * 0.68, -bend * w * 0.5), P_(h, bend * w * 0.2)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (p0[0] + (p[0] - p0[0]) * k, p0[1] + (p[1] - p0[1]) * k)            # noqa: E731
    core = lock(q(p0, 1), q(p1, 0.9), q(p2, 0.9), q(p3, 0.92), w * 0.42, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, WA[4]), (0.4, WA[3]), (0.8, WA[2]), (1, WA[1])])
    gin = g_lin(fig, p0, p3, [(0, WA[2]), (0.6, WA[1]), (1, '#ffffff')])
    return outlined([(sh, gout, 1), (core.move(0.3, -0.4), gin, 0.85)], w=1.2, op=op)


def arc_band(c, R0, R1, a0, a1, w, tilt, n=28):
    """Un bras d'eau en spirale autour d'un cercle penché : de a0 (fin, rayon R0) à a1 (plein, rayon R1). Renvoie la
    forme entière et ses morceaux devant (bas du cercle) et derrière (haut)."""
    rows = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        R = R0 + (R1 - R0) * t
        ww = w * math.sin(math.pi * min(1.0, 0.15 + 0.85 * t)) ** 0.6 * (0.25 + 0.75 * t)
        rows.append((math.sin(a) > 0, (c[0] + (R + ww / 2) * math.cos(a), c[1] + (R + ww / 2) * math.sin(a) * tilt),
                     (c[0] + (R - ww / 2) * math.cos(a), c[1] + (R - ww / 2) * math.sin(a) * tilt)))

    def shape(rr):
        o = [r[1] for r in rr]
        i_ = [r[2] for r in rr]
        return sm(o + i_[::-1], sharp=(0, len(o) - 1, len(o), 2 * len(o) - 1), t=0.6)
    whole = shape(rows)
    fronts, cur = [], []
    for k, r in enumerate(rows):
        if r[0]:
            cur.append(r)
        elif cur:
            cur.append(r)                 # un pas de plus : les morceaux se recouvrent (pas de joint)
            fronts.append(cur)
            cur = []
    if len(cur) > 1:
        fronts.append(cur)
    return whole, [shape(f_) for f_ in fronts if len(f_) > 1]


def vortex(fig, c, R, arms, w, rot, op=1.0, tilt=0.55, span=150):
    """Des bras d'eau qui tournent en spirale autour de la perle et s'y enroulent : le bras entier (et son contour) passe
    derrière la main, ses morceaux du bas repassent devant (sans contour : pas de joint visible)."""
    if op <= 0.02:
        return
    gr = g_lin(fig, (c[0] + R, c[1] - R), (c[0] - R, c[1] + R), [(0, '#ffffff'), (0.35, WA[1]), (0.7, WA[2]), (1, WA[3])])
    for j in range(arms):
        a0 = rot + 360.0 / arms * j
        whole, fronts = arc_band(c, R + 3.5, R - 1.5, a0, a0 + span, w, tilt)
        fig.fx_back.append(outlined([(whole, gr, 1)], w=1.1, op=op))
        for sh in fronts:
            fig.fx_front.append('<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op))
            fig.fx_front.append('<path d="%s" fill="#ffffff" opacity="%g"/>' % (sh.move(0.3, -0.35).d(), 0.0))


def water_ball(fig, c, r, op=1.0, glint=True):
    """Une boule d'eau : dégradé (claire en haut à droite), un reflet blanc, un liseré d'écume."""
    if r < 0.3:
        return ''
    b = ellipse(c[0], c[1], r, r)
    gr = g_rad(fig, (c[0] + r * 0.35, c[1] - r * 0.35), r * 1.5, [(0, '#ffffff'), (0.25, WA[1]), (0.6, WA[2]), (1, WA[4])])
    parts = [(b, gr, 1)]
    if glint:
        parts.append((ellipse(c[0] + r * 0.35, c[1] - r * 0.4, r * 0.32, r * 0.2, -35), '#ffffff', 1))
    return outlined(parts, w=1.1, op=op)


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


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---- l'attaque de base : l'orbe de la perle

ORB = {}


def orb_course(p0):
    """La course de l'orbe : de la perle à l'ennemi, un peu bombée."""
    p1 = FOE
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 12)

    def at(s):
        return ((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * mid[0] + s * s * p1[0], (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * mid[1] + s * s * p1[1])
    return at


def fx_attack(tl):
    def f(fig, ctx):
        pc, pr = ctx['pearl'], ctx['pr']
        # la charge : des bras d'eau qui tournent autour de la perle, de plus en plus serrés
        ch = env(tl, ATT_CHARGE[0], ATT_CHARGE[0] + 120, ATT_FIRE - 40, ATT_FIRE + 30)
        if ch > 0:
            k = (tl - ATT_CHARGE[0]) / (ATT_FIRE - ATT_CHARGE[0])
            vortex(fig, pc, pr + 6 - 2.5 * k, 2 if k < 0.5 else 3, 3.2 + 0.8 * k, -tl * 0.9, op=ch)
        # la boule d'eau se forme contre la perle
        if ATT_FORM[0] <= tl < ATT_FIRE:
            k = smooth((tl - ATT_FORM[0]) / (ATT_FIRE - ATT_FORM[0]))
            fig.fx_front.append(water_ball(fig, (pc[0] + 3 + 3 * k, pc[1] - 3 - 1.5 * k), 1.0 + 3.6 * k))
        # l'orbe file vers l'ennemi, avec sa traîne torsadée
        if ATT_FIRE <= tl < ATT_HIT:
            if 'at' not in ORB:
                ORB['at'] = orb_course((pc[0] + 6, pc[1] - 4.5))
            at = ORB['at']
            s = smooth((tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)) * 0.92 + 0.08 * (tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)
            c = at(s)
            a, b = at(min(1, s + 0.02)), at(max(0, s - 0.02))
            u = ((a[0] - b[0]), (a[1] - b[1]))
            L_ = math.hypot(*u) or 1
            u = (u[0] / L_, u[1] / L_)
            nrm = (-u[1], u[0])
            size = 4.6
            L = 34 * min(1, (tl - ATT_FIRE) / 60)
            cen = [(c[0] - u[0] * L * i / 12 + nrm[0] * 1.2 * (i / 12) * math.sin(i * 0.9 + tl / 40),
                    c[1] - u[1] * L * i / 12 + nrm[1] * 1.2 * (i / 12) * math.sin(i * 0.9 + tl / 40)) for i in range(13)]
            ws = [2 * size * (1 - i / 12) ** 1.3 + 0.3 for i in range(13)]
            trail = limb(cen, ws)
            gtr = g_lin(fig, cen[-1], c, [(0, WA[3], 0.0), (0.5, WA[2], 0.9), (1, WA[1], 1)])
            # le filet d'écume qui s'enroule autour de la traîne (on ne voit que les passages devant)
            spir = []
            for i in range(40):
                t_ = i / 39
                ph = t_ * 3 * 2 * math.pi + tl / 30
                r_ = (2 * size * (1 - t_) ** 1.3) / 2
                p = (c[0] - u[0] * L * t_ + nrm[0] * r_ * math.cos(ph), c[1] - u[1] * L * t_ + nrm[1] * r_ * math.cos(ph))
                spir.append((p, math.sin(ph) > 0, t_))
            sp_sh = []
            run = []
            for p, vis, t_ in spir:
                if vis and 0.1 < t_ < 0.9:
                    run.append(p)
                elif len(run) > 2:
                    sp_sh.append(ribbon(run, [0.1] + [0.7] * (len(run) - 2) + [0.1]))
                    run = []
                else:
                    run = []
            fig.fx_front.append(outlined([(trail, gtr, 1)], w=1.1))
            fig.fx_front.append(water_ball(fig, c, size))
            for sh in sp_sh:
                fig.fx_front.append('<path d="%s" fill="#ffffff" opacity="0.9"/>' % sh.d())
            for kk, sd in ((0.5, 4.6), (0.9, -3.8)):
                q = (c[0] - u[0] * L * kk + nrm[0] * sd, c[1] - u[1] * L * kk + nrm[1] * sd)
                fig.fx_front.append(wdrop(fig, q[0], q[1], u[0], u[1], 0.9))
        # l'éclatement sur l'ennemi : un éventail d'eau qui rebondit vers l'arrière, puis des gouttes et des bulles
        tau = (tl - ATT_HIT) / 1000.0
        if tau >= 0:
            c = FOE
            e = env(tau, 0, 0.05, 0.12, 0.34)
            if e > 0:
                for j, (ang, h, w, bd) in enumerate(((200, 17, 4.4, 0.6), (232, 15, 3.8, -0.5), (162, 13, 3.6, 0.5),
                                                     (262, 11, 3.0, 0.4), (128, 10, 3.0, -0.4), (292, 9, 2.6, -0.3))):
                    (fig.fx_front if j % 2 == 0 else fig.fx_back).append(jet(fig, c, h * e, w, ang, bend=bd))
            fl = env(tau, 0, 0.02, 0.05, 0.16)
            if fl > 0:
                fig.fx_front.append(water_ball(fig, (c[0] + 1, c[1]), 6.5 * (0.6 + 0.4 * fl), op=fl))
                fig.fx_front.append('<circle cx="%s" cy="%s" r="22" fill="%s"/>' % (fm(c[0]), fm(c[1]), g_rad(
                    fig, c, 22, [(0, '#ffffff', 0.8 * fl), (0.3, WA[1], 0.45 * fl), (1, WA[2], 0)])))
            if 0.04 < tau < 0.45:
                k = (tau - 0.04) / 0.41
                fig.fx_back.append(foam(fig, c[0] + 1, c[1] + 1 - 4 * k, 4.6 * (1 - 0.5 * k), op=1 - k))
            for i, (vx, vy, r) in enumerate(((-70, -60, 1.2), (-95, -15, 1.0), (-40, -95, 1.3), (-85, 35, 1.0), (-20, -70, 0.9),
                                             (30, -80, 1.0), (-110, -45, 0.8), (15, 40, 0.9))):
                if 0.03 < tau < 0.75:
                    x, y = ballistic(c, (vx, vy), 190, tau)
                    if y < GR - 1:
                        fig.fx_front.append(wdrop(fig, x, y, vx, vy + 190 * tau, r, op=min(1, (0.75 - tau) * 4)))
            for i, (dx, sp, r) in enumerate(((-6, 30, 1.6), (5, 40, 1.2), (-12, 22, 1.0))):
                if 0.1 < tau < 0.8:
                    k = tau - 0.1
                    fig.fx_front.append(bubble(fig, c[0] + dx + 1.5 * math.sin(k * 12 + i), c[1] - 8 - sp * k, r, op=min(1, (0.8 - tau) * 4)))
    return f


# ---- l'attaque spéciale : le dragon d'eau

class Path:
    """Le chemin du dragon d'eau (de la perle à l'ennemi), mesuré le long de la courbe."""

    def __init__(self, points):
        self.p = E.catmull(points, 16)
        self.s = [0.0]
        for i in range(1, len(self.p)):
            self.s.append(self.s[-1] + math.dist(self.p[i - 1], self.p[i]))
        self.L = self.s[-1]

    def at(self, s):
        s = min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.s[mid] <= s:
                lo = mid
            else:
                hi = mid
        t = (s - self.s[lo]) / max(self.s[hi] - self.s[lo], 1e-9)
        a, b = self.p[lo], self.p[hi]
        q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        L = math.dist(a, b) or 1
        return q, ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


DR = {}


def dragon_path(pc):
    """Le chemin : il monte en S au-dessus de la perle, passe haut au-dessus du champ de bataille, plonge sur l'ennemi."""
    x, y = pc
    return Path([(x + 1, y - 1), (x + 6, y - 12), (x + 8, y - 26), (x + 18, y - 40), (x + 36, y - 50), (x + 58, y - 49),
                 (x + 74, y - 38), (FOE[0] - 6, FOE[1] - 42), (FOE[0] - 1, FOE[1] - 20), (FOE[0] + 1, FOE[1] + 6)])


def head_s(tl, path):
    """Où est la tête du dragon le long du chemin à l'instant tl (ms)."""
    if tl < SP_EMERGE:
        return 0.0
    k = (tl - SP_EMERGE) / (SP_HIT - SP_EMERGE)
    if k <= 1:
        # il jaillit vite, ralentit au sommet de sa course, puis plonge en accélérant
        return path.L * min(1.0, 0.62 * smooth(min(1, k / 0.55)) + 0.38 * max(0.0, (k - 0.45) / 0.55) ** 1.6)
    return path.L + (tl - SP_HIT) * 0.12


BODY_L = 118.0


def body_points(path, sh, tl, cut=0.0):
    """Les points du corps (de la tête vers la queue), avec l'ondulation qui court de la tête vers la queue."""
    n = 46
    length = min(BODY_L, sh)
    out = []
    for i in range(n + 1):
        t = i / n
        if t > 1 - cut + 1e-9:
            break
        s = sh - t * length
        if s > path.L:          # cette partie a déjà plongé dans l'éclaboussure
            continue
        q, u = path.at(s)
        nv = (u[1], -u[0])      # le côté du dos (vers le haut quand il file vers la droite)
        envl = smooth(t / 0.2) * (1 - 0.4 * smooth((t - 0.8) / 0.2))
        off = 4.6 * envl * math.sin(2 * math.pi * (t * length) / 58.0 + tl / 95.0)
        out.append(((q[0] + nv[0] * off, q[1] + nv[1] * off), u, nv, t))
    return out


def water_dragon(fig, path, sh, tl, cut=0.0, jaw=1.0):
    """Le dragon d'eau : un long corps qui ondule, une crête d'écume, une tête de dragon (gueule ouverte, œil d'or,
    crinière d'écume, deux cornes), une houppe d'écume au bout de la queue (comme la sienne). Ajouté au dessin comme des
    morceaux : un seul contour, ombres et lumières comme le héros."""
    pts = body_points(path, sh, tl, cut)
    if len(pts) < 3:
        return
    cen = [p for p, u, nv, t in pts]
    ws = [(2.4 + 12.4 * (1 - t) ** 1.1) * (0.78 + 0.22 * smooth(t / 0.12)) for p, u, nv, t in pts]
    body = limb(cen, ws)
    left, right = sides(cen, ws)
    # le ventre plus clair (côté opposé au dos), un reflet le long du dos
    bel = [(p[0] - nv[0] * w * 0.22, p[1] - nv[1] * w * 0.22) for (p, u, nv, t), w in zip(pts, ws)]
    shine = [(p[0] + nv[0] * w * 0.22, p[1] + nv[1] * w * 0.22) for (p, u, nv, t), w in zip(pts, ws)]
    det = [(ribbon(bel, [0.2] + [w * 0.34 for w in ws[1:-1]] + [0.2]), WA[1], 0.55),
           (ribbon(shine, [0.2] + [w * 0.16 for w in ws[1:-1]] + [0.2]), '#ffffff', 0.7)]
    # les anneaux du ventre : de courts plis doux, inégaux
    for i in range(4, len(pts) - 3, 5):
        p, u, nv, t = pts[i]
        w = ws[i]
        a = (p[0] - nv[0] * w * 0.48, p[1] - nv[1] * w * 0.48)
        b = (p[0] - nv[0] * w * 0.05 + u[0] * 0.6, p[1] - nv[1] * w * 0.05 + u[1] * 0.6)
        det.append((ribbon([a, ((a[0] + b[0]) / 2 + u[0] * 0.5, (a[1] + b[1]) / 2 + u[1] * 0.5), b], [0.1, 0.6, 0.1]), WA[4], 0.45))
    # la crête d'écume du dos : des mèches qui se couchent vers l'arrière (derrière le corps)
    crest = []
    for k, i in enumerate(range(6, len(pts) - 4, 7)):
        p, u, nv, t = pts[i]
        w = ws[i]
        r0 = (p[0] + nv[0] * w * 0.35, p[1] + nv[1] * w * 0.35)
        L = 5 + 4.5 * (1 - t)
        d = (-u[0] * 0.8 + nv[0] * 0.6, -u[1] * 0.8 + nv[1] * 0.6)
        p1 = (r0[0] + d[0] * L * 0.4 + nv[0] * 1.0, r0[1] + d[1] * L * 0.4 + nv[1] * 1.0)
        p2 = (r0[0] + d[0] * L * 0.8 + nv[0] * 0.8, r0[1] + d[1] * L * 0.8 + nv[1] * 0.8)
        p3 = (r0[0] + d[0] * L - u[0] * 0.4 - nv[0] * 1.2, r0[1] + d[1] * L - u[1] * 0.4 - nv[1] * 1.2)
        crest.append(('wdc%d' % k, lock(r0, p1, p2, p3, 2.6 + 2.6 * (1 - t), n=10, bulge=0.35)))
    if cut < 0.02 and len(pts) > 4:
        p, u, nv, t = pts[-1]
        for k, sgn in enumerate((1, -1)):
            d = (-u[0] * 0.75 + nv[0] * 0.65 * sgn, -u[1] * 0.75 + nv[1] * 0.65 * sgn)
            L = 8 - 2 * k
            crest.append(('wdt%d' % k, lock(p, (p[0] + d[0] * L * 0.4, p[1] + d[1] * L * 0.4),
                                            (p[0] + d[0] * L * 0.8 + nv[0] * sgn, p[1] + d[1] * L * 0.8 + nv[1] * sgn),
                                            (p[0] + d[0] * L - u[0], p[1] + d[1] * L - u[1]), 3.4 - 0.6 * k, n=10, bulge=0.35)))
    for name, s_ in crest:
        fig.part(name, s_, FOAM, cel=0.6, rim=0.5, cast=0, details=[(under(s_), FOAM.shadow, 0.6)])
    fig.part('wdb', body, WMAT, cel=1.4, rim=0.8, cast=0.9, cast_on=[c[0] for c in crest], details=det)
    if cut > 0.98 or pts[0][3] > 0.01:
        return
    # la tête : orientée le long de la course (sans se retourner : entre 45° vers le haut et 40° vers le bas)
    (hq, hu, hn, _) = pts[0]
    ang = math.degrees(math.atan2(hu[1], hu[0]))
    ang = max(-45.0, min(40.0, ang))
    a = math.radians(ang)
    hu = (math.cos(a), math.sin(a))
    hd = (-hu[1], hu[0])          # « vers le bas » de la tête (côté de la gorge)
    c0 = (hq[0] + hu[0] * 1.5, hq[1] + hu[1] * 1.5)

    def H(x, y):
        return (c0[0] + hu[0] * x + hd[0] * y, c0[1] + hu[1] * x + hd[1] * y)

    def HS(pts_):
        return [H(*p) for p in pts_]
    # la crinière d'écume derrière la tête, et deux cornes
    for k, (r0, p1, p2, p3, w) in enumerate((((-4, -3), (-10, -8), (-17, -9), (-21, -5.6), 5.4),
                                            ((-3, 1), (-10, -1), (-17, 1), (-20, 4.6), 4.6),
                                            ((-1, -5), (-6, -11), (-12, -14), (-16, -12.4), 4.0))):
        s_ = lock(*HS([r0, p1, p2, p3]), w, n=10, bulge=0.35)
        fig.part('wdm%d' % k, s_, FOAM, cel=0.7, rim=0.5, cast=0, details=[(under(s_), FOAM.shadow, 0.6)])
    for k, (r0, p1, p2, w) in enumerate((((-1, -4.6), (-6, -9.4), (-11.6, -10.2), 2.4), ((2.6, -5.0), (-1.2, -10.6), (-6.4, -12.8), 2.2))):
        hp = HS([r0, p1, p2])
        s_ = limb(E.catmull(hp, 4), [w * (1 - 0.7 * i / 8) for i in range(9)])
        fig.part('wdh%d' % k, s_, FOAM, cel=0.5, rim=0.4, cast=0)
    # la mâchoire du bas (ouverte), le creux de la gueule, le crâne et le museau
    jw = jaw
    hinge = (1.0, 2.2)

    def J(p):
        r = math.radians(26 * jw)
        x, y = p[0] - hinge[0], p[1] - hinge[1]
        return (hinge[0] + x * math.cos(r) - y * math.sin(r), hinge[1] + x * math.sin(r) + y * math.cos(r))
    lowj = sm(HS([J(p) for p in ((-2.6, 1.8), (6, 2.4), (14, 3.0), (16.4, 3.8), (15.6, 5.4), (8, 6.4), (-1, 6.0))]))
    hollow = sm(HS([(0, 0.8), (15, 1.4), J((15.6, 3.6)), J((6, 4.0)), (0, 3.6)]))
    fig.part('wdj', lowj, WMAT, cel=0.8, rim=0.5, cast=0, details=[(lowj, ('lin', H(8, 2)[0], H(8, 2)[1], H(8, 7)[0], H(8, 7)[1], [(0, WA[2]), (1, WA[4])]), 0.9)])
    fig.part('wdg', hollow, Mat('#3a5ab0', '#2a3a86', '#1c2462', '#141a45', '#0e1032'), cel=0, rim=0, cast=0,
             details=[(ribbon(HS([(2, 3.4), (8, 3.8), J((14, 3.8))]), [0.2, 1.2, 0.2]), '#4a6ad0', 0.8)])
    skull = sm(HS([(-6, 1.6), (-6.4, -2.6), (-2, -5.8), (4, -6.2), (9, -4.4), (14, -2.8), (19.0, -2.4), (20.6, -0.8), (19.6, 1.2), (12, 1.2), (4, 1.6), (-2, 3.2)]))
    sdet = [(sm(HS([(4, -5.6), (9, -4.0), (14, -2.4), (19, -2.0), (19.6, -1.0), (12, -1.2), (5, -2.6), (0, -3.8)])), '#ffffff', 0.45),
            (ellipse(*H(18.0, -1.0), 0.8, 0.5), WA[5], 0.85),
            # l'œil d'or, comme le sien ; l'arcade au-dessus
            (sm(HS([(3.0, -3.4), (6.6, -4.2), (8.4, -3.0), (6.2, -2.0), (3.6, -2.2)])), '#140a1c', 0.95),
            (sm(HS([(3.6, -3.2), (6.6, -3.9), (7.8, -3.0), (6.0, -2.4), (4.0, -2.5)])), ('rad', H(5.8, -3)[0], H(5.8, -3)[1], 2.4, 2.4, [(0, '#fff4a0'), (0.5, '#ffd63a'), (1, '#e2761c')]), 1),
            (ellipse(*H(5.8, -3.0), 0.4, 0.7), '#140a1c', 1),
            (ribbon(HS([(2.4, -4.6), (5.6, -5.4), (9.2, -4.4)]), [0.1, 0.9, 0.1]), '#ffffff', 0.8)]
    fig.part('wds', skull, WMAT, cel=1.0, rim=0.8, cast=0.8, cast_on=['wdj', 'wdg', 'wdb'], details=sdet)
    # les crocs d'écume
    for k, (x, y, h) in enumerate(((15.4, 1.0, 1.8), (10.4, 1.4, 1.5))):
        fang = sm(HS([(x - 0.6, y - 0.2), (x + 0.6, y - 0.2), (x, y + h)]), sharp=(0, 1, 2), t=0.6)
        fig.part('wdf%d' % k, fang, FOAM, cel=0, rim=0, cast=0, outline=False)
    # le barbillon d'écume qui flotte de la truffe
    wh = HS([(19, 0.4), (16, 4.4), (11, 6.8), (6, 9.6 + 0.6 * math.sin(tl / 60))])
    fig.part('wdw', limb(E.catmull(wh, 4), [1.3 - 0.9 * i / 12 for i in range(13)]), FOAM, cel=0, rim=0.3, cast=0)


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        pc, pr = ctx['pearl'], ctx['pr']
        g = P['glow']
        # la charge : des bras d'eau qui tournent autour de la perle, des bulles montent du sol vers elle
        ch = env(tl, SP_GATHER[0], SP_GATHER[0] + 160, SP_GATHER[1] - 60, SP_GATHER[1] + 60)
        if ch > 0:
            k = (tl - SP_GATHER[0]) / (SP_GATHER[1] - SP_GATHER[0])
            vortex(fig, pc, pr + 8 - 3 * k, 3, 3.2 + 1.0 * k, -tl * (0.6 + 0.6 * k), op=ch)
            vortex(fig, pc, pr + 13 - 4 * k, 2, 2.4 + 0.6 * k, tl * 0.5 + 40, op=ch * 0.8, tilt=0.4, span=110)
            for i in range(0, 11, 2):
                st = SP_GATHER[0] + (i * 61) % 420
                dur = 420 + (i * 37) % 160
                u = (tl - st) / dur
                if 0 <= u <= 1:
                    x0 = 14 + (i * 0.618 % 1) * 70
                    y0 = GR - 2
                    tx, ty = pc
                    e_ = smooth(u)
                    x = x0 + (tx - x0) * e_ ** 1.6 + 2.6 * math.sin(u * 9 + i)
                    y = y0 + (ty - y0) * e_
                    fig.fx_front.append(bubble(fig, x, y, (0.9 + 0.5 * (i % 3)) * (1 - 0.6 * e_ ** 3), op=min(1, u * 6) * ch))
        # la lueur de la perle qui s'éveille
        if g > 0.3:
            fig.under.append((pc[0], pc[1], 18 + 5 * g, 18 + 5 * g, '#6ee2ff', 0.1 * g, None))
        # le dragon d'eau jaillit de la perle, serpente, plonge
        if tl >= SP_EMERGE:
            if 'path' not in DR:
                Pe = pose_at(0, 'special', -SP_EMERGE / 1000.0 - 0.03)
                cx = E.build(pose=Pe).ctx
                DR['path'] = dragon_path(cx['pearl'])
            path = DR['path']
            sh = head_s(tl, path)
            cut = 0.0
            if tl > SP_HIT + 60:
                cut = min(1.0, (tl - SP_HIT - 60) / 380.0)
            jaw = 0.6 + 0.4 * math.sin(tl / 70.0) if tl < SP_HIT else 1.0
            if cut < 1:
                water_dragon(fig, path, sh, tl, cut=cut, jaw=jaw)
            # l'eau qui sort encore de la perle au début (le dragon y prend sa source)
            e0 = env(tl, SP_EMERGE, SP_EMERGE + 30, SP_EMERGE + 160, SP_EMERGE + 300)
            if e0 > 0:
                fig.fx_front.append(water_ball(fig, (pc[0] + 0.6, pc[1] - 0.6), pr * (1.0 + 0.35 * e0), op=0.8 * e0))
            # la queue se défait en gouttes et en bulles
            if tl > SP_HIT + 60:
                for i in range(0, 14, 2):
                    fr = 1 - (i + 0.5) / 14            # du bout de la queue vers la tête
                    t_cut = SP_HIT + 60 + (1 - fr) * 380
                    tau = (tl - t_cut) / 1000.0
                    if 0 <= tau < 0.7:
                        if ('bead', i) not in DR:
                            pts = body_points(path, head_s(t_cut, path), t_cut, 0.0)
                            j = min(len(pts) - 1, max(0, int(round(fr * (len(pts) - 1)))))
                            DR[('bead', i)] = pts[j][0] if pts else FOE
                        p0 = DR[('bead', i)]
                        vx, vy = (-20 + (i * 17) % 40, -15 - (i * 13) % 25)
                        x, y = ballistic(p0, (vx, vy), 150, tau)
                        if y < GR - 1:
                            if i % 3 == 0:
                                fig.fx_front.append(bubble(fig, p0[0] + 2 * math.sin(tau * 9 + i), p0[1] - 22 * tau, 1.2, op=1 - tau / 0.7))
                            else:
                                fig.fx_front.append(wdrop(fig, x, y, vx, vy + 150 * tau, 1.1 if i % 2 else 0.85, op=1 - tau / 0.7))
        # l'éclat d'écume sur l'ennemi (arrêt sur l'image), la couronne de jets, l'écume qui roule au sol
        if tl >= SP_HIT - 20:
            tg = tl - SP_HIT
            X = FOE[0]
            fl = env(tg, -20, 0, 30, 140)
            if fl > 0:
                fig.fx_front.append(EP.lumiere(fig, (X, FOE[1] + 10), 90, fl, 'eau'))
            sc = env(tg, 0, 90, 260, 560)
            if sc > 0:
                # l'eau enveloppe l'ennemi : UNE colonne d'eau et sa gerbe, une bosse au pied (effets_pro, 28/11)
                fig.fx_back.append(EP.bosse(fig, X, GR, 7 * sc, 40, 'eau', op=min(1, sc * 1.5)))
                fig.fx_back.append(EP.colonne(fig, X, GR - 50 * sc, GR, 22 * (0.6 + 0.4 * sc), 14 * (0.6 + 0.4 * sc), 2 * math.sin(tl / 40), tg / 1000,
                                              op=min(1, sc * 1.6), lips=sc))
                fig.fx_front.append(EP.gerbe(fig, X, GR, min(0.95, 0.1 + tg / 700), 1.8, seed=3))
            for j, (vx, vy) in enumerate(((-70, -150), (60, -170), (-110, -80), (115, -95), (-25, -210))):
                tau = (tg - 20 * (j % 3)) / 1000.0
                if 0 <= tau < 0.8:
                    x, y = ballistic((X, GR - 8), (vx, vy), 300, tau)
                    if y < GR - 0.5:
                        fig.fx_front.append(wdrop(fig, x, y, vx, vy + 300 * tau, 1.5 if j % 2 else 1.1))
            # l'écume qui roule au sol en volutes, des bulles qui montent
            fk = (tg - 120) / 1000.0
            if 0 < fk < 1.1:
                o = env(fk, 0, 0.12, 0.6, 1.1)
                for j, (dx, rr, sp) in enumerate(((-16, 5.4, -18), (14, 5.8, 14))):
                    fig.fx_back.append(foam(fig, X + dx + sp * fk, GR - 3 - 4 * fk, rr * (0.75 + 0.5 * fk), op=0.95 * o))
                for j, (dx, sp, rr) in enumerate(((-10, 36, 1.8), (6, 46, 2.2), (18, 30, 1.4))):
                    fig.fx_front.append(bubble(fig, X + dx + 2 * math.sin(fk * 8 + j), GR - 14 - sp * fk, rr, op=o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros (comme la vidéo de Kael)."""
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
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (44 - x0) * k
    sd.ellipse([cx - 40 * k, fy - 3.0 * k, cx + 40 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : repos ×2, attaque ×2, spéciale ×1 (comme Kael)."""
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
        if tl < 5:
            ORB.clear()
            for k in list(DR.keys()):
                if k != 'path':
                    del DR[k]
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    return E.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        arg = sys.argv[sys.argv.index('--planche') + 1] if len(sys.argv) > sys.argv.index('--planche') + 1 else ''
        if arg:
            moments = [float(v) for v in arg.split(',')]
        else:
            moments = [1.0, a_s + 0.2, a_s + 0.36, a_s + 0.45, a_s + 0.56, a_s + 0.68,
                       s_s + 0.4, s_s + 0.7, s_s + 0.85, s_s + 1.0, s_s + 1.15, s_s + 1.28, s_s + 1.45, s_s + 1.7]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(out)
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
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : le tourbillon autour de la perle en rubans d'un seul tenant, la perle et les bulles des boules
# d'eau sans contour sombre, les gouttes étirées par leur course, l'écume fondue, l'impact en colonne et gerbe d'une
# forme ; le dragon d'eau (dessiné comme le héros) et l'attaque gardent leur dessin.
import effets_pro as EP  # noqa: E402


def _vortex(fig, c, R, arms, w, rot, op=1.0, tilt=0.55, span=150):
    if op <= 0.02:
        return
    for j in range(arms):
        a0 = rot + 360.0 / arms * j
        bk, fr, _ = EP.spirale(fig, c, R + 1, R + 1, a0, span, w * 1.8, tilt=tilt, p='eau', n=24, stops=EP.spirale_feu('eau'))
        fig.fx_back.append(EP.group(bk, op * 0.8))
        fig.fx_front.append(EP.group(fr, op))


EP.accrocher(sys.modules[__name__], {
    'vortex': _vortex,
    'bubble': lambda fig, x, y, r=1.4, op=1.0: EP.boule(fig, (x, y), r * 1.1, 0, 'eau', op=op * 0.9),
    'water_ball': lambda fig, c, r, op=1.0, glint=True: EP.boule(fig, c, r, 0, 'eau', op=op),
    'wdrop': lambda fig, x, y, vx, vy, r=1.0, op=1.0: EP.goutte(fig, x, y, vx, vy, r, 'eau', op=op),
    'foam': lambda fig, cx, cy, r, op=1.0: EP.nuage(fig, cx, cy, r * 1.15, 'eau', op=op, seed=int(cx) % 3),
})


if __name__ == '__main__':
    main()
