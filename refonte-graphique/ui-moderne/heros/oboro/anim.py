# Oboro vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/sorcier-oni/build.py)
# — respiration, attaque de base « Feu follet », attaque spéciale « La lanterne aux âmes » — dans le style lisse de
# l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/oboro/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/oboro/
#   python3 refonte-graphique/ui-moderne/heros/oboro/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael, ../kael/anim.py) : le dessin (oboro.py) est fait de morceaux ; chaque image le redessine dans
# une POSE (le buste qui respire et se penche depuis les hanches, la tête qui suit avec retard, le bâton qui pivote
# autour de son bout planté, le poing lointain qui le tient, la manche lointaine qui suit, le chapelet et le bas de la
# barbe qui se balancent). C'est un VIEUX sorcier : rien de brusque au repos ; ses sorts partent de la LANTERNE, pas de
# ses mains. La lanterne PEND toujours : son balancement est calculé comme un vrai pendule accroché au crochet (elle
# traîne derrière quand il pousse le bâton, puis revient). Les poses clés reprennent celles du pixel art (mêmes gestes,
# même rythme) et sont reliées par des courbes douces sans dépassement. Les effets (feux follets, langues de flamme,
# braises, fumée, poussière) sont dessinés dans le même style : dégradés, un seul contour, aucun flou SVG ; jamais de
# rayons droits répétés.
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
import oboro as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, resample, mapp, f as fm  # noqa: E402
from outils import crpath, taper  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'oboro')
# les images de travail : dans le brouillon de la session si on le donne (OBORO_TMP), sinon à côté du script
TMP = os.environ.get('OBORO_TMP') or os.path.join(HERE, '_images')
LAVA = K.LAVA
FPS = 24
VIEW = (20, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes (comme la crinière de Kael)
SINK = '#4a3656'                     # le contour doux de la fumée
GR = K.GRD
HIT = (222.0, 82.0)                  # l'ennemi (le milieu de son corps), où les sorts éclatent

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


NUM = ['crouch', 'lean', 'tilt', 's', 'sdy', 'glow', 'ro', 'bs', 'hs', 'hem', 'eyes', 'headx', 'heady']


def flat(k):
    d = {n: 0.0 for n in NUM}
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


# ======================================================================== les actions (poses clés)
# 2) L'attaque de base « Feu follet » (pixel : ATTAQUE). Il ramène son bâton contre lui en se redressant un peu, la
# tête levée : la lanterne s'allume plus fort, des braises montent vers elle en tournant (anticipation tenue). Puis il
# pousse le bâton vers l'ennemi d'un coup de reins, la tête en avant : la lanterne, laissée en arrière, crache un feu
# follet qui file en ondulant ; il éclate sur l'ennemi en flamme et fumée ; il se renfonce dans sa bosse.
ATTACK = [
    (0, {}),
    (130, dict(lean=-1.0, head=(-1, -1), s=-1.3, glow=1.0, ro=-2, bs=1.0, hs=0.6)),
    (320, dict(lean=-2.0, head=(-1, -2), tilt=-2, s=-2.6, glow=2.0, ro=-3, bs=2.0, hs=1.0, eyes=1)),
    (430, dict(lean=-2.2, head=(-1.1, -2.2), tilt=-2.4, s=-2.8, glow=2.3, ro=-3, bs=2.2, hs=1.1, eyes=1)),
    (500, dict(lean=2.4, head=(2, 1), tilt=2, s=2.8, glow=3.0, ro=3, bs=-1.6, hs=-1.0, hem=1, eyes=1)),
    (560, dict(lean=2.2, head=(2, 1), tilt=2, s=2.8, glow=2.4, ro=3, bs=-1.2, hs=-0.8, hem=0.8, eyes=1)),
    (660, dict(lean=1.2, head=(1, 0.2), tilt=1, s=2.0, glow=1.4, ro=1, bs=0.4, hem=0.2)),
    (800, dict(lean=0.8, head=(0.4, 0.2), s=1.3, glow=1.0, ro=-1, bs=1.0, hem=-0.3)),
    (960, dict(lean=0.2, head=(0, 0.6), s=0.5, glow=0.4, ro=-1, bs=0.3)),
    (1150, {}),
]
AT_LAUNCH, AT_HIT = 500, 700           # le feu follet part de la lanterne / éclate sur l'ennemi (ms)

# 3) L'attaque spéciale « La lanterne aux âmes » (pixel : SPECIALE). Il soulève son bâton et le replante d'un coup sec
# (poussière) : la lanterne sursaute et s'embrase, des langues de flamme lèchent son chapeau, ses yeux s'allument. Trois
# feux follets sortent de la lanterne l'un après l'autre et tournent AUTOUR DE SA TÊTE (ceux du fond passent derrière
# ses cornes) ; il se redresse, penché en arrière, la barbe soulevée par le souffle chaud. Le grand moment (arrêt
# bref) : il pousse le bâton de tout son poids, éclair ; les trois feux follets partent ensemble en trois courbes qui
# se rejoignent sur l'ennemi : une gerbe de flammes qui monte, se recourbe et s'éteint en fumée et en braises.
SPECIAL = [
    (0, {}),
    (170, dict(sdy=4.0, lean=-1.0, head=(0, -1), s=-0.6, glow=1.0, ro=-2, bs=1.0, hs=0.6)),
    (250, dict(sdy=0.0, crouch=1.0, head=(0, 1), glow=2.0, ro=2, bs=-0.6, hem=0.8, eyes=1)),
    (340, dict(crouch=0.9, head=(0, 0.6), glow=3.0, ro=1, bs=0, eyes=1)),
    (520, dict(lean=-1.0, head=(-1, -1), tilt=-1.5, s=-1.3, glow=3.0, ro=0, bs=1.2, hs=0.8, eyes=1)),
    (900, dict(lean=-2.2, head=(-1, -2), tilt=-3, s=-2.6, glow=3.0, ro=-1, bs=2.4, hs=1.4, eyes=1)),
    (1040, dict(lean=-2.5, head=(-1.2, -2.3), tilt=-3.4, s=-3.0, glow=3.0, ro=-1, bs=2.6, hs=1.5, eyes=1)),
    (1100, dict(lean=3.0, head=(2.2, 1), tilt=2.4, s=4.0, glow=3.0, ro=3, bs=-1.8, hs=-1.2, hem=1.2, eyes=1)),
    (1260, dict(lean=2.8, head=(1.8, 0.8), tilt=2, s=4.0, glow=2.6, ro=2.4, bs=-1.4, hs=-1.0, hem=1.0, eyes=1)),
    (1380, dict(lean=2.0, head=(1, 0), tilt=1, s=3.2, glow=2.0, ro=0, bs=0.2, eyes=1)),
    (1560, dict(lean=1.2, head=(1, 0), s=2.4, glow=1.2, ro=-1, bs=1.0, hem=-0.4)),
    (1780, dict(lean=0.8, head=(0.4, 0.3), s=1.4, glow=1.0, ro=0.5, bs=0.4)),
    (1980, dict(lean=0.3, head=(0, 0.6), s=0.5, glow=0.4, ro=1, bs=-0.4)),
    (2250, {}),
]
SP_TAP = 250                           # le bâton replanté (poussière)
BORN = (330.0, 440.0, 550.0)           # chaque feu follet sort de la lanterne
RELEASE, ARRIVE = 1100.0, 1380.0       # lâchés / arrivés sur l'ennemi
ORBIT_C = (86.0, 40.0)                 # le centre de la ronde autour de la tête (pixels du dessin)
ORBIT_R = (30.0, 13.0)
ORBIT_SPEED = 0.62                     # degrés par ms
A0 = 90.0                              # l'angle où ils entrent dans la ronde (en haut)
CURVES = ((22, -44), (40, -14), (36, 26))   # le premier point de contrôle de chaque courbe vers l'ennemi

# ======================================================================== la respiration (en boucle) et la lanterne


def idle_offsets(T):
    """Le repos d'un vieillard : souffle lent qui soulève la bosse, la tête suit avec retard, la barbe et le chapelet
    se balancent en retard."""
    u = 2 * math.pi * T / 2.3
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, heady=0.35 * math.sin(u - 0.9) - 0.15, headx=0.12 * math.sin(u - 1.2), tilt=0.5 * math.sin(u - 1.0),
                bs=0.7 * math.sin(u - 1.6), hs=0.5 * math.sin(u - 1.2), hem=0.35 * math.sin(u - 2.0),
                ro=2.2 * math.sin(2 * math.pi * T / 1.9 + 0.8), glow=0.12 * math.sin(2 * math.pi * T / 0.9))


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours (sans la lanterne)."""
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
    P['flick'] = T * 11.0
    P['blink'] = 1.0 if (w > 0.95 and 1.3 <= (T % 3.7) < 1.4) else 0.0
    return P, tl


def hook_of(P):
    ST = K.mchain(K.mT(0, -P['sdy']), K.mR(P['s'], *K.STAFF_FOOT))
    return mapp(ST, K.HOOK)


def lantern_track(segs, n, sub=10):
    """Le balancement de la lanterne à chaque image : un pendule accroché au crochet (qui bouge avec le bâton), plus
    un léger balancement entretenu au repos. Renvoie l'angle (degrés, + : le bas part en arrière)."""
    Lp, g, c = 11.0, 340.0, 2.2
    th, om = 0.0, 0.0
    dt = 1.0 / (FPS * sub)
    prev = None
    vprev = None
    out = []
    for i in range(n * sub + 1):
        T = i * dt
        act, t0 = which(segs, T)
        P, _ = pose_at(T, act, t0)
        h = hook_of(P)
        if prev is None:
            v = (0.0, 0.0)
        else:
            v = ((h[0] - prev[0]) / dt, (h[1] - prev[1]) / dt)
        a = (0.0, 0.0) if vprev is None else ((v[0] - vprev[0]) / dt, (v[1] - vprev[1]) / dt)
        prev, vprev = h, v
        # le repos entretient un petit balancement (la lanterne n'est jamais tout à fait immobile)
        drive = 9.0 * math.sin(2 * math.pi * T / 1.55)
        # (le crochet est mené par des poses clés : ses à-coups sont adoucis de moitié, et le balancement reste
        # mesuré — jamais la lanterne ne vient heurter sa tête)
        acc = (-(g - 0.5 * a[1]) * math.sin(th) + 0.5 * a[0] * math.cos(th)) / Lp - c * om + drive * math.pi / 180
        om += acc * dt
        th += om * dt
        if i % sub == 0:
            d = math.degrees(th)
            out.append(16.0 * math.tanh(d / 16.0))
    return out


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True, hot=False):
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
    if hot:        # une grande flamme vive : le bout reste orange (lisible sur le fond sombre)
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.45, LAVA[2]), (0.8, LAVA[3]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3 if ink else 0, op=op)


def ember(fig, x, y, r=0.7, op=1.0, hot=True):
    if op <= 0.02:
        return ''
    c1, c2, c3 = (LAVA[0], LAVA[1], LAVA[3]) if hot else (LAVA[2], LAVA[3], LAVA[5])
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, c1, op), (0.6, c2, op), (1, c3, op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0, dust=False):
    """Une bouffée de fumée (gris chaud un peu rosé, le feu du clan) ou de poussière (brun-gris) : quelques boules sous
    un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    stops = [(0, '#efe0d2'), (0.5, '#bba494'), (1, '#7e6676')] if dust else [(0, '#f4e8e6'), (0.5, '#c8b0b8'), (1, '#8a6c84')]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0, fire=False):
    """Une volute (fumée, ou feu) qui s'enroule : un ruban courbe qui s'affine, sous un contour doux."""
    if op <= 0.02 or r < 0.5:
        return ''
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    if fire:
        gr = g_lin(fig, pts[0], pts[-1], [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
        return outlined([(sh, gr, 1)], ink=FINK, w=1.1, op=op)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f4e8e6'), (0.6, '#c8b0b8'), (1, '#8a6c84')])
    return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0):
    """Un éclat de feu : un coeur et des lobes arrondis (plus gros vers « facing », degrés), coeur blanc, bord orange
    puis rouge ; un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    stops = [(0, LAVA[0]), (0.35, LAVA[1]), (0.65, LAVA[2]), (0.88, LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, stops)
    return outlined([(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes], w=1.4, op=op)


def follet(fig, trail, r, wob=0.0, op=1.0):
    """Un feu follet (une âme de feu) : une boule au coeur blanc et sa flamme qui traîne derrière elle en ondulant, le
    long du chemin parcouru (trail : du plus ancien au plus récent). Un seul contour, aucun flou."""
    if op <= 0.02:
        return ''
    head = trail[-1]
    pts = [p for i, p in enumerate(trail) if i == 0 or math.dist(p, trail[i - 1]) > 0.05]
    out = []
    # la lueur autour (dégradé rond)
    out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(head[0]), fm(head[1]), fm(r * 3.0), g_rad(
        fig, head, r * 3.0, [(0, LAVA[2], 0.45 * op), (0.5, LAVA[3], 0.16 * op), (1, LAVA[3], 0)])))
    shapes = []
    L = sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts))) if len(pts) > 1 else 0
    if L > 1.0:
        c = resample(pts[::-1], 16)
        # la flamme ondule (une vague qui court le long de la traînée)
        cc = []
        for i, p in enumerate(c):
            t = i / 16
            a = c[max(0, i - 1)]
            b = c[min(16, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ll = math.hypot(dx, dy) or 1
            amp = r * 0.45 * t * math.sin(wob + t * 7.0)
            cc.append((p[0] - dy / ll * amp, p[1] + dx / ll * amp))
        tail = taper(cc, r * 1.9, 0.2, tip='sharp', wmid=r * 1.3)
        tl = cc[-1]
        shapes.append((tail, g_lin(fig, head, tl, [(0, LAVA[1]), (0.35, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])]), 1))
        core = taper(cc[:9], r * 1.0, 0.15, tip='sharp')
        shapes.append((core, g_lin(fig, head, cc[8], [(0, LAVA[0]), (1, LAVA[1])]), 0.9))
    ball = ellipse(head[0], head[1], r, r)
    shapes.append((ball, g_rad(fig, (head[0] + 0.25 * r, head[1] - 0.25 * r), r * 1.25,
                               [(0, '#ffffff'), (0.35, LAVA[0]), (0.6, LAVA[1]), (0.85, LAVA[2]), (1, LAVA[3])]), 1))
    out.append(outlined(shapes, w=1.4, op=op))
    return ''.join(out)


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


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def along(pts, s):
    """Le point à la fraction s (0..1) d'une ligne brisée (par l'indice, les points sont réguliers)."""
    s = max(0.0, min(1.0, s))
    x = s * (len(pts) - 1)
    i = min(len(pts) - 2, int(x))
    t = x - i
    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)


# ---- la lanterne : elle s'allume (braises qui montent vers elle), elle flambe (langues de flamme sur son chapeau)

def blaze(fig, ctx, level, t):
    """Des langues de flamme lèchent le chapeau de la lanterne et se recourbent ; des braises montent."""
    if level <= 0.05:
        return
    top = ctx['lant_top']
    c = ctx['lantern']
    ph = t / 90.0
    h1 = (6 + 6 * level) * (0.85 + 0.15 * math.sin(ph))
    h2 = (5 + 5 * level) * (0.85 + 0.15 * math.sin(ph + 2.1))
    op = min(1.0, level * 1.4)
    fig.fx_back.append(tongue(fig, (top[0] - 1.6, top[1] + 1.2), h1, 4.2, bend=-0.8 + 0.4 * math.sin(ph * 0.7), lean=-0.12, op=op, hot=True))
    fig.fx_back.append(tongue(fig, (top[0] + 2.4, top[1] + 1.4), h2, 3.6, bend=0.9 - 0.3 * math.sin(ph * 0.9), lean=0.16, op=op, hot=True))
    for k, (dx, dy, sp) in enumerate(((-6, -16, 1.0), (5, -20, 1.3), (-1, -26, 0.8), (8, -13, 1.1))[:int(1 + level * 1.4)]):
        rise = (t * 0.018 * sp + k * 7) % 14
        fig.fx_front.append(ember(fig, c[0] + dx + 1.2 * math.sin(t / 140 + k), c[1] + dy - rise, 0.55 + 0.15 * (k == 0),
                                  op=min(1, level) * (1 - rise / 14)))


def gather(fig, ctx, k, t):
    """L'anticipation : des braises montent vers la lanterne en spirale, une petite volute de feu s'enroule autour."""
    if k <= 0.02:
        return
    c = ctx['lantern']
    for j, a in enumerate((200, 255, 320, 30, 120)):
        aa = math.radians(a + 0.35 * t)
        rr = (17 - 8 * k) * (1 + 0.18 * (j % 2))
        lay = fig.fx_front if j % 2 else fig.fx_back
        lay.append(ember(fig, c[0] + rr * math.cos(aa), c[1] - rr * math.sin(aa) * 0.85, 0.6 + 0.2 * (j == 2), op=k))
    fig.fx_back.append(curl(fig, (c[0] - 0.5, c[1] - 0.5), 12 - 3 * k, 150 + 0.3 * t, 160, 1.9, op=k * 0.9, fire=True))


def attack_path(p0, n=80):
    """Le chemin du feu follet : du devant de la lanterne jusqu'à l'ennemi, en onde (pas en ligne droite)."""
    return bezier(p0, (p0[0] + 40, p0[1] - 34), (HIT[0] - 52, HIT[1] + 22), HIT, n)


def impact(fig, t, big=1.0):
    """L'éclatement sur l'ennemi : un éclat de feu, des bouffées de fumée, des braises (t en ms depuis l'impact)."""
    x, y = HIT
    e0 = env(t, -1, 0, 70, 220)
    if e0 > 0:
        for dx, dy, r in ((-9, -6, 4.0), (8, -8, 3.6), (-7, 7, 3.2), (9, 6, 3.2)):
            k = min(1, t / 160 + 0.3)
            fig.fx_back.append(smoke(fig, x + dx * (0.8 + 0.5 * k), y + dy * (0.8 + 0.5 * k) - 4 * k, r * big * (0.7 + 0.5 * k), op=e0))
        fig.fx_front.append(pop(fig, (x, y), 10 * big * (0.6 + 0.5 * min(1, t / 60)), facing=180, op=e0))
    # le nuage de fumée qui monte et se défait
    e1 = env(t, 60, 160, 260, 560)
    if e1 > 0:
        k = (t - 60) / 500
        fig.fx_back.append(smoke(fig, x + 1 + 2 * k, y - 3 - 12 * k, 8 * big * (0.8 + 0.4 * k), op=e1 * 0.95))
        fig.fx_back.append(curl(fig, (x + 4, y - 8 - 10 * k), 6 + 4 * k, 200 + 120 * k, 220, 2.2, op=e1 * 0.8))
    e2 = env(t, 40, 90, 160, 260)
    if e2 > 0:
        fig.fx_front.append(pop(fig, (x - 1, y + 1), 4.5 * big, facing=180, op=e2))
    # les braises
    for j, (vx, vy, big_) in enumerate(((-0.06, -0.01, True), (0.055, 0.02, False), (0.012, -0.07, True),
                                        (-0.045, -0.055, False), (0.07, -0.03, False))):
        e3 = env(t, 30, 60, 300, 520)
        if e3 > 0:
            tt = t - 30
            fig.fx_front.append(ember(fig, x + vx * tt, y + vy * tt + 0.00009 * tt * tt, 0.75 if big_ else 0.55,
                                      op=e3, hot=tt < 260))


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        # l'anticipation : la lanterne s'allume, des braises montent vers elle
        gather(fig, ctx, env(t, 20, 200, 430, 520), t)
        blaze(fig, ctx, 0.9 * env(t, 200, 330, 470, 640), t)
        # le départ : la lanterne crache le feu follet (un éclat de flamme devant elle, une bouffée de fumée)
        c = ctx['lantern']
        p0 = START.get('a') or (c[0] + 9, c[1] - 1)
        el = env(t, AT_LAUNCH - 20, AT_LAUNCH, AT_LAUNCH + 30, AT_LAUNCH + 140)
        if el > 0:
            fig.fx_back.append(pop(fig, (p0[0] - 1, p0[1]), 5.5 * (0.7 + 0.3 * el), facing=0, op=el))
            fig.fx_back.append(smoke(fig, c[0] + 3, c[1] - 12 - 6 * (1 - el), 2.6, op=el * 0.85))
        # le vol : il file en ondulant, sa flamme traîne, de petites bouffées de fumée s'en détachent
        if AT_LAUNCH <= t < AT_HIT:
            pts = attack_path(p0)
            s = ((t - AT_LAUNCH) / (AT_HIT - AT_LAUNCH)) ** 1.15
            tail = [along(pts, max(0.0, s - 0.26 * (1 - j / 12))) for j in range(13)]
            fig.fx_front.append(follet(fig, tail, 3.6, wob=t / 30.0))
            for k, ds in enumerate((0.16, 0.3)):
                if s - ds > 0.04:
                    x, y = along(pts, s - ds)
                    fig.fx_back.append(smoke(fig, x - 1, y - 5 - 2 * k, 2.6 - 0.5 * k, op=0.7 - 0.25 * k))
        if t >= AT_HIT:
            impact(fig, t - AT_HIT)
    return f


# ---- la spéciale

def orbit_pt(a):
    ar = math.radians(a)
    return (ORBIT_C[0] + ORBIT_R[0] * math.cos(ar), ORBIT_C[1] - ORBIT_R[1] * math.sin(ar)), math.sin(ar) <= 0.12


def follet_pos(i, u):
    """(x, y, devant ?, taille) du feu follet i au temps u (ms de la spéciale) ; None s'il n'existe pas."""
    b = BORN[i]
    if u < b or u >= ARRIVE:
        return None
    lc = START['lantern']
    if u < b + 110:                                  # il jaillit par le chapeau de la lanterne et rejoint la ronde
        t = (u - b) / 110
        (ox, oy), near = orbit_pt(A0)
        sx, sy = lc[0] + 1, lc[1] - 12
        x = sx + (ox - sx) * t
        y = sy + (oy - sy) * t - 7 * math.sin(math.pi * t)
        return x, y, True, 0.6 + 0.4 * t
    if u < RELEASE:                                  # la ronde autour de la tête
        a = A0 + ORBIT_SPEED * (u - b - 110)
        (x, y), near = orbit_pt(a)
        return x, y, near, 1.0
    a = A0 + ORBIT_SPEED * (RELEASE - b - 110)       # lâchés : ils filent vers l'ennemi en trois courbes
    (x0, y0), near = orbit_pt(a)
    t = ((u - RELEASE) / (ARRIVE - RELEASE)) ** 1.25
    cx, cy = CURVES[i]
    pts = bezier((x0, y0), (x0 + cx, y0 + cy), (HIT[0] - 40, HIT[1] + cy * 0.4), HIT, 40)
    x, y = along(pts, t)
    return x, y, (near or u - RELEASE > 90), 1.0


def follets(fig, u, tail_ms=110):
    for i in range(3):
        p = follet_pos(i, u)
        if p is None:
            continue
        x, y, near, size = p
        lay = fig.fx_front if near else fig.fx_back
        r = (3.3 if near else 2.8) * size
        pts = []
        for j in range(13):
            q = follet_pos(i, u - tail_ms * (1 - j / 12))
            if q is not None:
                pts.append(q[:2])
        if not pts or pts[-1] != (x, y):
            pts.append((x, y))
        lay.append(follet(fig, pts, r, wob=u / 30.0 + i * 2))


def fire_burst(fig, t):
    """La gerbe de flammes sur l'ennemi (t en ms depuis l'arrivée) : de grandes langues de feu montent, se recourbent,
    puis s'éteignent en volutes de fumée et en braises."""
    x, y = HIT
    base = y + 7
    grow = min(1.0, t / 140)
    sink = 1.0 - env(t, 300, 700, 2000, 2001) if t > 300 else 1.0       # les flammes retombent
    op = 1.0 - env(t, 520, 760, 2000, 2001) if t > 520 else 1.0
    if t < 760:
        # quatre grandes langues, de hauteurs, largeurs et penchés inégaux, qui montent et se recourbent
        LICKS = [(-6.5, 0.72, 8.0, -0.9, -0.24), (-1.0, 1.0, 10.5, 0.7, -0.06), (5.0, 0.86, 9.0, -0.6, 0.16),
                 (9.5, 0.5, 6.5, 0.9, 0.34)]
        for j, (dx, hk, w, bend, lean) in enumerate(LICKS):
            wob = math.sin(t / 70 + j * 1.7)
            h = 36 * hk * grow * sink * (1 + 0.07 * wob)
            fig.fx_back.append(tongue(fig, (x + dx * (0.7 + 0.3 * grow), base), h, w * (0.6 + 0.4 * sink),
                                      bend=bend + 0.3 * wob, lean=lean + 0.1 * math.sin(t / 110 + j), op=op, hot=True))
        # le coeur du brasier, rond, au pied des flammes
        fig.fx_front.append(pop(fig, (x + 1, base - 3), 8 * (0.5 + 0.5 * grow) * (0.4 + 0.6 * sink), facing=-90, op=op))
    # le premier éclat (les trois âmes se rejoignent)
    e0 = env(t, -1, 0, 50, 200)
    if e0 > 0:
        fig.fx_front.append(pop(fig, (x, y), 12 * (0.7 + 0.4 * min(1, t / 60)), facing=180, op=e0))
        fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(40), g_rad(
            fig, (x, y), 40, [(0, '#fffbe4', 0.7 * e0), (0.3, '#ffb43a', 0.25 * e0), (1, '#ff7a1e', 0)])))
    # la fumée qui monte en volutes
    for j, (dx, st, r) in enumerate(((-6, 260, 5.0), (5, 330, 6.0), (0, 420, 4.4))):
        e = env(t, st, st + 120, st + 260, st + 560)
        if e > 0:
            k = (t - st) / 560
            fig.fx_back.append(smoke(fig, x + dx + 3 * k, base - 22 - 18 * k, r * (0.8 + 0.5 * k), op=e * 0.9))
            fig.fx_back.append(curl(fig, (x + dx + 4, base - 30 - 16 * k), 5 + 3 * k, 180 + 90 * k + 60 * j, 230, 2.0, op=e * 0.75))
    # les braises
    for j in range(7):
        a = math.radians(-160 + j * 23 + 7 * math.sin(j * 3.1))
        sp = 0.045 + 0.012 * ((j * 5) % 3)
        e = env(t, 80, 120, 520, 860)
        if e > 0:
            tt = t - 80
            fig.fx_front.append(ember(fig, x + math.cos(a) * sp * tt, y + math.sin(a) * sp * tt + 0.00006 * tt * tt - 4,
                                      0.7 if j % 2 else 0.55, op=e, hot=tt < 420))


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        if 'lantern' not in START:
            START['lantern'] = ctx['lantern']
        # le bâton replanté : un peu de poussière au pied, la lanterne sursaute
        e = env(t, SP_TAP - 10, SP_TAP + 10, SP_TAP + 60, SP_TAP + 300)
        if e > 0:
            foot = ctx['staff_foot']
            k = (t - SP_TAP) / 300
            for dx, r in ((-5, 2.4), (5, 2.8), (-2, 1.8), (8, 1.6)):
                fig.fx_back.append(smoke(fig, foot[0] + dx * (0.5 + 0.9 * k), GR - 1.5 - 3 * k * (1 + (dx > 0)), r * (0.6 + 0.6 * k), op=e * 0.9, dust=True))
        # la lanterne s'embrase et flambe pendant toute la charge ; les yeux sont allumés (dans la pose)
        blaze(fig, ctx, 1.6 * env(t, SP_TAP, SP_TAP + 100, RELEASE, RELEASE + 260), t)
        # les trois feux follets : la ronde autour de la tête, puis le vol vers l'ennemi
        if BORN[0] <= t < ARRIVE:
            follets(fig, t, 70 if t < RELEASE else 50)
        # le grand moment : l'éclair, chaud, qui part de la lanterne (un dégradé rond, pas un voile plat)
        fl = env(t, RELEASE - 10, RELEASE, RELEASE + 30, RELEASE + 140)
        if fl > 0:
            c = ctx['lantern']
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(140), g_rad(
                fig, c, 140, [(0, '#fffbe4', 0.85 * fl), (0.12, '#ffe68a', 0.55 * fl), (0.45, '#ffb43a', 0.16 * fl), (1, '#ff7a1e', 0)])))
            fig.fx_back.append(pop(fig, (c[0] + 7, c[1] - 2), 7 * fl, facing=0, op=fl))
        if t >= ARRIVE:
            fire_burst(fig, t - ARRIVE)
    return f


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael et Lenore)."""
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
    # l'ombre douce au sol sous lui (robe, pieds et bout du bâton)
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (77 - x0) * k
    sd.ellipse([cx - 34 * k, fy - 2.8 * k, cx + 34 * k, fy + 2.8 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 4.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.2),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.8)]
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


def frame_svg(T, segs, la, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    P['la'] = la
    fx = []
    if act == 'attack':
        if 'a' not in START:
            Ph, _ = pose_at(t0 + AT_LAUNCH / 1000.0, act, t0)
            c = K.build(pose=Ph).ctx['lantern']
            START['a'] = (c[0] + 9, c[1] - 1)
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'lantern' not in START:
            Ph, _ = pose_at(t0 + BORN[0] / 1000.0, act, t0)
            START['lantern'] = K.build(pose=Ph).ctx['lantern']
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
    n = int(round(total * FPS))
    LA = lantern_track(segs, n)
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.3, a_s + 0.45, a_s + 0.52, a_s + 0.6, a_s + 0.72, a_s + 0.85, a_s + 1.0,
                            s_s + 0.17, s_s + 0.26, s_s + 0.45, s_s + 0.7, s_s + 0.95, s_s + 1.11, s_s + 1.25,
                            s_s + 1.42, s_s + 1.55, s_s + 1.7, s_s + 1.9, s_s + 2.1]
        fr = [frame_svg(T, segs, LA[min(n, int(round(T * FPS)))]) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs, LA[i]) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
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


if __name__ == '__main__':
    main()
