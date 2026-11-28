# Nyrra vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/araignee-tisseuse/
# build.py) — respiration, attaque de base « Crachat de soie », attaque spéciale « Filet de pierre » — dans le style
# lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/nyrra/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/nyrra/
#   python3 refonte-graphique/ui-moderne/heros/nyrra/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et d'Oboro) : le dessin (nyrra.py) est fait de morceaux ; chaque image le redessine dans une
# POSE. Le corps monte et descend, les pointes des pattes posées restent plantées (les genoux suivent) ; les pattes
# levées tournent autour de leur hanche et se plient au genou ; c'est l'ABDOMEN qui tire (il se replie, se gonfle, puis
# se détend comme un ressort et crache la soie par les filières). Une tisseuse : gestes posés et précis. Les deux
# cocons PENDENT : leur balancement est calculé comme un vrai pendule accroché à leur fil (ils traînent derrière quand
# le corps bouge, puis reviennent). Les poses clés reprennent celles du pixel art (mêmes gestes, même rythme) et sont
# reliées par des courbes douces sans dépassement. Les effets (soie, toile, pierre, poussière, venin) sont dessinés dans
# le même style : dégradés, un seul contour, aucun flou SVG ; la toile est faite de courbes qui pendent, jamais d'une
# grille de traits droits, jamais de rayons droits répétés.
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
import nyrra as N  # noqa: E402
from atelier import sm, ribbon, ellipse, rpoly, f as fm  # noqa: E402
from outils import fil  # noqa: E402

ROOT = N.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'nyrra')
TMP = os.environ.get('NYRRA_TMP') or os.path.join(HERE, '_images')
FPS = 24
VIEW = (-2, -26, 267, 150)           # la scène de la vidéo, en pixels du dessin (16/9), même échelle que Kael
VW, VH = 1280, 720
INK = '#1f1238'
SINK = '#4a3656'                     # le contour doux de la poussière
GR = N.GRD
HIT = (206.0, 93.0)                  # l'ennemi (le milieu de son corps), où la soie frappe
SILKC = ['#ffffff', '#f6f2f4', '#d6d4ec', '#9a96c4', '#5e5888']
STONE = ['#f0dcc4', '#d6bea8', '#927268', '#60484e', '#3c2a38']
VENOM = ['#f0ffb0', '#a8e650', '#3c9a52', '#1c544c']
K = 1.15                             # le rythme du pixel art, un peu étiré (plus fluide)

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


NUM = ['spx', 'spy', 'rot', 'abx', 'aby', 'abr', 'sw', 'eyes', 'fang',
       'raA', 'raB', 'rbA', 'rbB', 'rcA', 'rcB', 'rdA', 'rdB', 'twx', 'twy',
       'rcLow', 'rcLow2', 'rcHigh', 'rcFling', 'rdHigh', 'rdFling', 'rdOut']


def keyed(keys, t):
    ts = [k[0] * K for k in keys]
    return {n: monotone(ts, [k[1].get(n, 0.0) for k in keys], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) « Crachat de soie » : elle se tasse, l'abdomen se replie vers l'arrière et se gonfle (les pattes levées se
# dressent, une goutte de soie perle aux filières) ; puis il se détend d'un coup : une boule de soie gluante part vers
# l'ennemi en ondulant ; recul ; la boule s'écrase en éclaboussure de soie, avec deux gouttes de venin ; retour en garde.
ATTACK = [
    (0, {}),
    (90, dict(spy=1.0, rcA=-2, raA=-2, rbA=-1, fang=0.2)),
    (240, dict(spx=-2.0, spy=1.6, abx=-3.0, aby=-1.4, abr=-8, sw=1.0, rcA=-6, rcB=-6, raA=-5, rbA=-4, rdA=-3,
               eyes=0.5, fang=0.5)),
    (410, dict(spx=-3.0, spy=1.8, abx=-4.0, aby=-2.0, abr=-11, sw=2.0, rcA=-7, rcB=-8, raA=-6, rbA=-5, rdA=-4,
               eyes=1.0, fang=0.8)),
    (455, dict(spx=1.0, spy=0.0, abx=2.4, aby=-0.6, abr=6, sw=0.0, rcA=2, rcB=4, raA=-1, rbA=0, rdA=0, eyes=1.0,
               fang=1.0)),
    (520, dict(spx=-2.0, spy=0.0, abx=0.4, abr=1, rcA=3, rcB=3, raA=2.5, rbA=2, rdA=1.5, eyes=0.9, fang=0.6)),
    (600, dict(spx=-1.4, rcA=2, rcB=1, raA=1.5, rbA=1.5, rdA=1, eyes=0.7, fang=0.4)),
    (760, dict(spx=-0.8, rcA=0.6, raA=0.4, eyes=0.4, fang=0.2)),
    (900, dict(spx=-0.2, rcA=-0.4, raA=-0.3)),
    (1070, {}),
]
AT_BEAD, AT_LAUNCH, AT_HIT, AT_END = 240 * K, 425 * K, 575 * K, 960 * K

# 3) « Filet de pierre » : elle se cabre et TISSE : sa patte avant proche descend devant les filières et enroule la
# soie en une pelote où se prennent des cailloux ; l'abdomen pompe deux fois. Elle recule pour prendre son élan (patte
# dressée), puis détend tout le corps et lance la pelote en cloche ; la pelote éclate sur l'ennemi et s'ouvre en un
# grand filet en dôme (arrêt sur image, éclair), dont les bords se plantent dans le sol (pierre, poussière) ; le venin
# brille dans les fils, puis le filet se défait. Elle se remet en garde.
SPECIAL = [
    (0, {}),
    (100, dict(sw=0.6, raA=-2, rbA=-2, fang=0.3)),
    (230, dict(spx=-2, spy=-2.4, rot=-4, abx=0.8, aby=0.8, sw=1.0, rcLow=1, rdOut=1, raA=-4, rbA=-4, eyes=0.6, fang=0.4)),
    (340, dict(spx=-2, spy=-2.4, rot=-4, abx=-0.6, aby=0.8, sw=2.0, rcLow2=1, rdOut=1, raA=-4, rbA=-4, eyes=0.6, fang=0.4)),
    (450, dict(spx=-2, spy=-2.4, rot=-4, abx=0.8, aby=0.8, sw=1.0, rcLow=1, rdOut=1, raA=-4, rbA=-4, eyes=0.7, fang=0.4)),
    (560, dict(spx=-2, spy=-2.4, rot=-4, abx=-0.6, aby=0.8, sw=2.0, rcLow2=1, rdOut=1, raA=-4, rbA=-4, eyes=0.8, fang=0.4)),
    (740, dict(spx=-4, spy=0.0, rot=-2, abx=-2.0, sw=1.0, rcHigh=1, rdHigh=1, raA=-8, raB=-4, rbA=-6, eyes=1.0,
               fang=0.7)),
    (800, dict(spx=3, spy=-1.0, rot=2, abx=2.5, abr=5, rcFling=1, rdFling=1, raA=2, rbA=2, eyes=1.0, fang=1.0)),
    (880, dict(spx=0.5, spy=0.0, rot=0.5, abx=0.6, abr=1, rcFling=0.35, rdOut=0.6, raA=2.5, rbA=1.5, eyes=1.0,
               fang=0.7)),
    (960, dict(spx=0.4, rcA=1.5, rcB=2, raA=1, rbA=1, eyes=1.0, fang=0.6)),
    (1150, dict(spx=1.0, rcA=1, rcB=1, eyes=0.9, fang=0.5)),
    (1270, dict(spx=1.0, rcA=0.5, eyes=0.7, fang=0.3)),
    (1420, dict(spx=0.4, sw=0.5, eyes=0.4)),
    (1530, dict(sw=0.6, rcA=-0.5)),
    (1780, {}),
]
SP_BALL0, SP_HOLD, SP_LAUNCH, SP_HIT = 200 * K, 740 * K, 800 * K, 935 * K
SP_OPEN, SP_PLANT, SP_VENOM, SP_UNDO, SP_END = 1000 * K, 1160 * K, 1290 * K, 1420 * K, 1560 * K
BALL_G = (108.0, 84.0)                # où se forme la pelote (repère du corps), devant les filières

# ======================================================================== la respiration (en boucle)


IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2,2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : ses deux cocons de soie se balancent lentement au bout de leur fil (en sens contraire), et ses yeux
    rouge braise s'allument doucement. Une pose partielle pour build() ; jouée au combat (pose_at, ajoutée au
    balancement calculé des cocons) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(c1=17.0 * math.sin(u), c2=-14.0 * math.sin(u - 0.8), eyes=0.9 * (0.5 - 0.5 * math.cos(u)))


def idle_offsets(T):
    """Elle respire lentement : le corps monte (les pointes restent plantées), l'abdomen suit avec retard et gonfle ;
    les pattes levées flottent avec retard ; la pointe de la patte avant proche « goûte l'air » (un petit cercle)."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    v = 2 * u                 # deux petits cercles par boucle
    return dict(breath=br, aby=0.35 * math.sin(u - 1.0), sw=0.25 * (0.5 - 0.5 * math.cos(u - 0.8)),
                raA=1.2 * math.sin(u - 0.9), rbA=0.9 * math.sin(u - 1.3), rcA=0.6 * math.sin(u - 0.7),
                rdA=0.7 * math.sin(u - 1.5), twx=0.7 * math.cos(v), twy=0.6 * math.sin(v))


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours (sans les cocons)."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0] * K
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or {n: 0.0 for n in NUM}
    Q = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P = dict(breath=w * idl['breath'], sp=(Q['spx'], Q['spy']), rot=Q['rot'], ab=(Q['abx'], Q['aby']), abr=Q['abr'],
             sw=max(0.0, Q['sw']), eyes=max(0.0, min(1.0, Q['eyes'])), fang=max(0.0, Q['fang']),
             la={'RA': (Q['raA'], Q['raB']), 'RB': (Q['rbA'], Q['rbB']), 'RC': (Q['rcA'], Q['rcB']),
                 'RD': (Q['rdA'], Q['rdB'])},
             tw={'RC': (Q['twx'] * w, Q['twy'] * w)},
             alt={'RC': {'low': Q['rcLow'], 'low2': Q['rcLow2'], 'high': Q['rcHigh'], 'fling': Q['rcFling']},
                  'RD': {'high': Q['rdHigh'], 'fling': Q['rdFling'], 'out': Q['rdOut']}})
    sg = signe(T)                         # le signe du repos ; les cocons s'ajoutent à leur pendule (frame_svg)
    P['eyes'] = max(P['eyes'], w * sg['eyes'])
    P['c1'], P['c2'] = w * sg['c1'], w * sg['c2']
    P['blink'] = 1.0 if (w > 0.95 and 1.6 <= (T % IDLE_T) < 1.72) else 0.0
    return P, tl


# ======================================================================== les cocons : de vrais pendules


def cocoon_track(segs, n, sub=10):
    """L'angle des deux cocons à chaque image : chacun pend au bout de son fil, poussé par le mouvement de son point
    d'attache (ils traînent derrière, puis reviennent en se balançant)."""
    dt = 1.0 / FPS / sub
    g = 420.0
    out = []
    st = [[0.0, 0.0], [0.0, 0.0]]          # angle (radians), vitesse
    Ls = (8.6, 17.6)                       # longueur jusqu'au centre du cocon
    prev = None
    pv = None
    for i in range(n):
        T = i / FPS
        a, s = which(segs, T)
        P, _ = pose_at(T, a, s)
        anc = N.anchors(P)
        if prev is None:
            prev, pv = anc, [(0.0, 0.0), (0.0, 0.0)]
        vel = [((anc[k][0] - prev[k][0]) * FPS, (anc[k][1] - prev[k][1]) * FPS) for k in range(2)]
        acc = [((vel[k][0] - pv[k][0]) * FPS, (vel[k][1] - pv[k][1]) * FPS) for k in range(2)]
        for k in range(2):
            ax, ay = max(-900, min(900, acc[k][0])), max(-900, min(900, acc[k][1]))
            for _ in range(sub):
                th, om = st[k]
                # L θ'' = Ẍ cos θ − (g − Ÿ) sin θ (le cocon pend vers le bas ; θ > 0 : il part vers la gauche)
                al = (ax * math.cos(th) - (g - ay) * math.sin(th)) / Ls[k] - 2.4 * om
                om += al * dt
                th += om * dt
                st[k] = [th, om]
        out.append((math.degrees(st[0][0]), math.degrees(st[1][0])))
        prev, pv = anc, vel
    return out


# ======================================================================== outils des effets


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=INK, w=1.5, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def circ(cx, cy, r, n=16):
    return sm([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, 1 jusqu'à c, redescend jusqu'à d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        u = (t - a) / (b - a)
    elif t <= c:
        return 1.0
    else:
        u = 1 - (t - c) / (d - c)
    return u * u * (3 - 2 * u)


def stone(fig, x, y, r, k=0, op=1.0, rot=0.0):
    """Un éclat de pierre : un caillou anguleux mais adouci, éclairé en haut à droite, un seul contour."""
    if op <= 0.02 or r < 0.2:
        return ''
    shapes = [[(-1, -0.7), (0.3, -1.0), (1.0, -0.2), (0.7, 0.8), (-0.6, 0.9), (-1.1, 0.1)],
              [(-0.8, -0.9), (0.9, -0.7), (1.0, 0.5), (-0.2, 1.0), (-1.0, 0.3)],
              [(-1.0, -0.4), (-0.1, -1.0), (1.1, -0.5), (0.8, 0.7), (-0.5, 0.8)]][k % 3]
    a = math.radians(rot)
    pts = [(x + r * (p[0] * math.cos(a) - p[1] * math.sin(a)), y + r * (p[0] * math.sin(a) + p[1] * math.cos(a))) for p in shapes]
    sh = rpoly(pts, r * 0.3)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, STONE[0]), (0.45, STONE[1]), (1, STONE[3])])
    top = rpoly([pts[0], pts[1], pts[2], (x + r * 0.1, y - r * 0.1)], r * 0.2)
    return outlined([(sh, gr, 1), (top, STONE[0], 0.45)], w=1.1, op=op)


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière brun-gris : quelques boules sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#efe0d2'), (0.5, '#bba494'), (1, '#7e6676')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def drop(fig, x, y, r=1.0, op=1.0, ang=0.0):
    """Une goutte de venin vert, pointe en haut, un éclat."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    pts = [(0, -2.2 * r), (0.75 * r, -0.4 * r), (0.9 * r, 0.5 * r), (0, 1.0 * r), (-0.9 * r, 0.5 * r), (-0.75 * r, -0.4 * r)]
    pts = [(x + p[0] * math.cos(a) - p[1] * math.sin(a), y + p[0] * math.sin(a) + p[1] * math.cos(a)) for p in pts]
    sh = sm(pts, sharp=(0,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, VENOM[0]), (0.4, VENOM[1]), (1, VENOM[2])])
    return outlined([(sh, gr, 1), (ellipse(x + 0.3 * r, y - 0.1 * r, 0.28 * r, 0.22 * r), '#ffffff', 0.9)], ink='#16302c', w=1.0, op=op)


def puff(fig, c, r, op=1.0):
    """Une petite bouffée de soie (boules douces)."""
    if r < 0.2 or op <= 0.02:
        return ''
    balls = [(c[0], c[1], r), (c[0] + 0.7 * r, c[1] + 0.3 * r, 0.7 * r), (c[0] - 0.6 * r, c[1] + 0.4 * r, 0.65 * r)]
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, SILKC[0]), (0.5, SILKC[2]), (1, SILKC[3])])
    return outlined([(circ(x, y, rr, 12), gr, 1) for x, y, rr in balls], w=1.1, op=op)


def silk_ball(fig, c, r, spin=0.0, pebbles=0, op=1.0):
    """Une boule de soie gluante : ronde, deux tours de fil courbes qui tournent avec elle, des cailloux pris dedans."""
    if r < 0.3 or op <= 0.02:
        return ''
    cx, cy = c
    items = []
    for k in range(pebbles):
        a = math.radians(spin * 1.0 + k * 125 + 30)
        items.append((cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.86, k))
    out = ''
    # les cailloux du fond (derrière la boule)
    for x, y, k in items:
        if (y - cy) < -r * 0.2:
            out += stone(fig, x, y, r * 0.32, k, op, rot=spin + k * 40)
    body = circ(cx, cy, r, 18)
    gr = fig.rad(cx + r * 0.35, cy - r * 0.4, r * 1.5, r * 1.5, [(0, SILKC[0]), (0.45, SILKC[2]), (1, SILKC[3])])
    wraps = []
    for j, (tilt, w0) in enumerate(((spin * 0.8 + 20, 0.55), (spin * 0.8 + 110, 0.4))):
        t = math.radians(tilt)
        pts = []
        for i in range(13):
            u = math.radians(-70 + 140 * i / 12)
            ex, ey = r * 0.92 * math.cos(u) * 0.35, r * 0.92 * math.sin(u)
            pts.append((cx + ex * math.cos(t) - ey * math.sin(t), cy + ex * math.sin(t) + ey * math.cos(t)))
        wraps.append((ribbon(pts, [0.1] + [w0 * r * 0.35] * 11 + [0.1]), SILKC[3] if j == 0 else SILKC[1], 0.6))
    out += outlined([(body, gr, 1)] + wraps + [(ellipse(cx + r * 0.38, cy - r * 0.42, r * 0.22, r * 0.15, -30), '#ffffff', 0.95)],
                    w=1.4, op=op)
    for x, y, k in items:
        if (y - cy) >= -r * 0.2:
            out += stone(fig, x, y, r * 0.32, k, op, rot=spin + k * 40)
    return out


def _bz(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def shot(fig, p0, p3, s, r, arc=10.0, tail=0.22, wave=1.0, pebbles=0, spin=0.0):
    """La boule de soie en vol (abscisse s de 0 à 1 sur la trajectoire) et sa traînée ondulante qui s'effile."""
    s0 = max(0.0, s - tail)
    pts = []
    for i in range(19):
        u = s0 + (s - s0) * i / 18
        p = _bz(*_ctrl(p0, p3, arc), u)
        q = _bz(*_ctrl(p0, p3, arc), min(1, u + 0.01))
        d = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*d) or 1
        nv = (d[1] / L, -d[0] / L)
        amp = wave * 2.2 * (1 - i / 18) ** 0.7
        k = amp * math.sin(i / 18 * math.pi * 3 + s * 9)
        pts.append((p[0] + nv[0] * k, p[1] + nv[1] * k))
    out = ''
    if s - s0 > 0.01:
        w = [0.1] + [r * 0.9 * (i / 18) ** 0.8 for i in range(1, 18)] + [r * 0.9]
        tr = ribbon(pts, w, sharp_ends=False)
        out += outlined([(tr, g_lin(fig, pts[0], pts[-1], [(0, SILKC[3]), (1, SILKC[1])]), 1)], w=1.2, op=0.95)
    return out + silk_ball(fig, pts[-1], r, spin, pebbles)


def _ctrl(p0, p3, arc):
    p1 = (p0[0] + (p3[0] - p0[0]) * 0.33, p0[1] + (p3[1] - p0[1]) * 0.33 - arc)
    p2 = (p0[0] + (p3[0] - p0[0]) * 0.66, p0[1] + (p3[1] - p0[1]) * 0.66 - arc * 0.8)
    return p0, p1, p2, p3


def flash(fig, c, r, op):
    if op <= 0.02:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(c[0]), fm(c[1]), fm(r), fm(r * 0.9), g_rad(fig, c, r, [(0, '#ffffff', 0.9 * op), (0.35, '#fff6e0', 0.55 * op), (1, '#f0e6ff', 0)]))


def splat(fig, c, level, op=1.0):
    """La boule s'écrase sur l'ennemi : une galette gluante en lobes, des fils qui s'enroulent autour de lui (arcs
    d'ellipses inclinées), des coulures qui pendent (courbes, jamais une étoile de rayons). level 0..2 (continu)."""
    cx, cy = c
    out = ''
    sag = level * 4.0
    k = max(0.0, 1 - level * 0.38)
    # les fils enroulés
    for (dy, rx, ry, tilt, a0, a1) in ((-1, 12, 4, -18, 150, 350), (3, 11, 3.5, 14, -20, 170)):
        t = math.radians(tilt)
        pts = []
        span = (a1 - a0) * (1 - 0.35 * max(0, level - 1))
        for i in range(25):
            a = math.radians(a0 + span * i / 24)
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + ex * math.cos(t) - ey * math.sin(t), cy + dy + sag * 0.4 + ex * math.sin(t) + ey * math.cos(t)))
        out += fil(pts, 0.55, SILKC[1], op=op * min(1, 2.2 - level))
    # les coulures
    for (x0, ln, bend) in ((-2, 7 + sag * 1.6, -1.5), (3, 4 + sag, 1.2)):
        p0 = (cx + x0, cy + 4)
        p3 = (cx + x0 + bend, cy + 4 + ln)
        pts = bezier(p0, (p0[0] + bend * 0.2, p0[1] + ln * 0.4), (p3[0], p3[1] - ln * 0.3), p3, 16)
        out += fil(pts, 0.9, SILKC[1], op=op)
        out += puff(fig, (p3[0], p3[1] + 0.4), 1.2, op)
    lobes = [(cx, cy + sag * 0.3, 6.0 * k + 1), (cx + 4 * k, cy - 4 * k + sag * 0.5, 4.0 * k), (cx - 4, cy + 3 + sag * 0.4, 4.4 * k),
             (cx + 3, cy + 4 + sag * 0.6, 3.4 * k), (cx - 5 * k, cy - 3 + sag * 0.3, 3.0 * k)]
    lobes = [l for l in lobes if l[2] > 0.4]
    gr = fig.rad(cx + 3, cy - 4, 10, 10, [(0, SILKC[0]), (0.5, SILKC[2]), (1, SILKC[3])])
    out += outlined([(circ(x, y, r, 14), gr, 1) for x, y, r in lobes] + [(ellipse(cx + 2, cy - 2, 1.6, 1.0, -25), '#ffffff', 0.9)],
                    w=1.4, op=op)
    return out


RADIALS = [(98, 1.0, 1.2), (142, 0.92, -1.0), (182, 1.05, 1.4), (218, 1.0, -1.2), (262, 1.0, 0.8),
           (316, 1.0, -1.0), (0, 1.02, 1.3), (48, 0.95, -1.1)]


def web(hub, R, droop=0.0, rings=(0.28, 0.5, 0.72, 0.93), open_=1.0):
    """Une toile jetée sur l'ennemi, vue de face : des fils rayonnants COURBES (ils ploient sous leur poids) et des
    festons qui pendent entre deux fils (jamais une grille). Rend (fils, festons, ancres au sol)."""
    hx, hy = hub
    rad, ends = [], []
    for (ang, ln, bulge) in RADIALS:
        u = (math.cos(math.radians(ang)), -math.sin(math.radians(ang)) * 0.9)
        nv = (u[1], -u[0])
        L = R * ln * open_
        pts = []
        for i in range(31):
            t = i / 30
            pts.append((hx + u[0] * L * t + nv[0] * bulge * 3.0 * math.sin(math.pi * t),
                        hy + u[1] * L * t + nv[1] * bulge * 3.0 * math.sin(math.pi * t) + droop * 6 * t * t))
        cut = next((i for i, p in enumerate(pts) if p[1] >= GR), None)
        if cut is not None:
            pts = pts[:cut + 1]
            pts[-1] = (pts[-1][0], GR)
            ends.append(pts[-1])
        rad.append(pts)
    fest = []
    order = sorted(range(len(rad)), key=lambda i: RADIALS[i][0])
    for j, fr in enumerate(rings):
        for a_i in range(len(order)):
            i1, i2 = order[a_i], order[(a_i + 1) % len(order)]
            k1 = int(fr * 30 * (1 + 0.06 * math.sin(j * 2.1 + a_i)))
            k2 = int(fr * 30 * (1 + 0.06 * math.sin(j * 2.1 + a_i + 1)))
            if k1 >= len(rad[i1]) or k2 >= len(rad[i2]):
                continue
            p1, p2 = rad[i1][k1], rad[i2][k2]
            d = math.dist(p1, p2)
            sag = 0.16 * d + 0.6
            mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            o = (mid[0] - hx, mid[1] - hy)
            L = math.hypot(*o) or 1
            ctrl = (mid[0] - o[0] / L * sag * 0.8, mid[1] - o[1] / L * sag * 0.8 + sag * 0.9)
            pts = [((1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * ctrl[0] + t * t * p2[0],
                    (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * ctrl[1] + t * t * p2[1]) for t in [i / 14 for i in range(15)]]
            pts = [(x, min(y, GR)) for x, y in pts]
            fest.append(pts)
    return rad, fest, ends


# ======================================================================== les effets de chaque action


def fx_attack(tl):
    def f(fig, ctx):
        spin = ctx['spin']
        # la goutte de soie qui perle aux filières (pendant que l'abdomen se gonfle)
        if AT_BEAD <= tl < AT_LAUNCH:
            u = (tl - AT_BEAD) / (AT_LAUNCH - AT_BEAD)
            fig.fx_front.append(silk_ball(fig, (spin[0] + 1.0 + 1.2 * u, spin[1] + 0.2), 0.6 + 1.3 * u, spin=u * 40))
        # le départ : une bouffée de soie aux filières
        if AT_LAUNCH <= tl < AT_LAUNCH + 140:
            u = (tl - AT_LAUNCH) / 140
            for (dx, dy, r) in ((1.5, 0, 2.4), (3.5, -2.6, 1.5), (3.2, 2.4, 1.4)):
                fig.fx_front.append(puff(fig, (spin[0] + dx + 2 * u, spin[1] + dy * (1 + u)), r * (1 - 0.6 * u), op=1 - u))
        if AT_LAUNCH <= tl < AT_HIT:
            if 'a0' not in START:
                START['a0'] = (spin[0] + 2.0, spin[1])
            s = (tl - AT_LAUNCH) / (AT_HIT - AT_LAUNCH)
            s = 1 - (1 - s) ** 1.4
            fig.fx_front.append(shot(fig, START['a0'], HIT, s, 2.6 + 1.0 * min(1, s * 3), arc=10, tail=0.18 + 0.1 * s,
                                     spin=s * 300))
        else:
            START.pop('a0', None)
        if AT_HIT <= tl < AT_END:
            u = (tl - AT_HIT) / (AT_END - AT_HIT)
            fig.fx_back.append(flash(fig, (HIT[0] - 2, HIT[1]), 12, max(0.0, 1 - u * 4)))
            fig.fx_front.append(splat(fig, (HIT[0] - 2, HIT[1]), 2.2 * u, op=min(1.0, (1 - u) * 3)))
            for (dx, dy, vx, vy, a) in ((7, -9, 10, -16, 20), (-9, 2, -12, -8, -30), (9, -6, 8, -4, 35)):
                t = u * 0.9
                fig.fx_front.append(drop(fig, HIT[0] + dx + vx * t, HIT[1] + dy + vy * t + 30 * t * t, 0.9,
                                         op=min(1.0, (1 - u) * 2.5), ang=a + 60 * t))
    return f


def fx_special(tl):
    def f(fig, ctx):
        spin = ctx['spin']
        BODY = ctx['BODY']
        # la pelote qui se forme devant les filières (la patte avant proche l'enroule), reliée par deux fils
        if SP_BALL0 <= tl < SP_LAUNCH:
            u = min(1.0, (tl - SP_BALL0) / (SP_HOLD - 30 - SP_BALL0))
            r = 2.0 + 4.0 * u
            c = N.mapp(BODY, (BALL_G[0] + (-3.0 if tl > SP_HOLD - 100 else 0.0) * min(1, max(0, (tl - SP_HOLD + 100) / 100)), BALL_G[1]))
            for (dy0, dy1, bend) in ((-0.6, -r * 0.6, -3), (0.6, r * 0.5, 3)):
                a = (spin[0], spin[1] + dy0)
                b = (c[0] - r * 0.7, c[1] + dy1)
                fig.fx_front.append(fil(bezier(a, (a[0] + (b[0] - a[0]) * 0.35, a[1] + bend), (a[0] + (b[0] - a[0]) * 0.7, b[1] + bend * 0.6), b, 14), 0.4, SILKC[1]))
            fig.fx_front.append(silk_ball(fig, c, r, spin=tl * 0.35, pebbles=min(3, int(u * 4))))
            START['ball'] = c
        if SP_LAUNCH <= tl < SP_HIT:
            s = (tl - SP_LAUNCH) / (SP_HIT - SP_LAUNCH)
            p0 = START.get('ball', (112.0, 82.0))
            fig.fx_front.append(shot(fig, p0, (HIT[0], HIT[1] - 2), s, 6.0, arc=30, tail=0.2, wave=0.8, pebbles=3,
                                     spin=220 + s * 400))
        # elle éclate sur l'ennemi : soie, cailloux arrachés
        if SP_HIT <= tl < SP_OPEN + 60:
            u = (tl - SP_HIT) / (SP_OPEN + 60 - SP_HIT)
            cx, cy = HIT
            fig.fx_back.append(flash(fig, HIT, 14 + 6 * u, 1 - u))
            for k, (ex, ey) in enumerate(((13, -7), (-9, -11), (8, 13), (-13, 7), (6, -12))):
                p0 = (cx + ex * 0.4, cy + ey * 0.4)
                p3 = (cx + ex * (0.6 + 0.6 * u), cy + ey * (0.6 + 0.6 * u))
                fig.fx_front.append(fil(bezier(p0, (p0[0] + ex * 0.3, p0[1] + ey * 0.2), (p3[0], p3[1] - 2), p3, 10), 0.9, SILKC[1], op=1 - u * 0.5))
                fig.fx_front.append(puff(fig, p3, 1.3, 1 - u * 0.5))
            fig.fx_front.append(E.nuage(fig, cx, cy, 7.5 * (1 - 0.3 * u), _SOIE, seed=2))   # la tache de soie : UNE forme (28/11)
            for k, (dx, dy) in enumerate(((-15, -12), (13, -14), (16, 6), (-16, 8))):
                fig.fx_front.append(stone(fig, cx + dx * (0.6 + 0.8 * u), cy + dy * (0.6 + 0.8 * u) + 8 * u * u, 1.6, k, rot=200 * u))
        # le filet s'ouvre (éclair), retombe, se plante, colle, se défait
        if SP_OPEN <= tl < SP_END:
            cx, cy = HIT
            op_ = min(1.0, (tl - SP_OPEN) / 60)
            if tl < SP_PLANT:
                u = (tl - SP_OPEN) / (SP_PLANT - SP_OPEN)
                hub, R, droop, o = (cx, cy - 4 + 4 * u), 34 - 4 * u, 0.6 * u, min(1.0, 0.55 + u * 1.5)
            elif tl < SP_UNDO:
                u = (tl - SP_PLANT) / (SP_UNDO - SP_PLANT)
                hub, R, droop, o = (cx, cy), 30.0, 0.6 + 0.3 * u, 1.0
            else:
                u = (tl - SP_UNDO) / (SP_END - SP_UNDO)
                hub, R, droop, o = (cx, cy), 30 - 2 * u, 0.9 + 1.8 * u, 1.0
            fade = 1.0 if tl < SP_UNDO else max(0.0, 1 - (tl - SP_UNDO) / (SP_END - SP_UNDO))
            rad, fest, ends = web(hub, R, droop, open_=o)
            flash_on = SP_OPEN <= tl < SP_OPEN + 150
            if flash_on:
                fig.fx_back.append(flash(fig, hub, 26, 1 - (tl - SP_OPEN) / 150))
            col = '#ffffff' if flash_on else SILKC[1]
            if tl >= SP_UNDO:                              # il se défait : il n'en reste que des bouts
                rad = [p[len(p) // 3:] for p in rad[1::2]]
                fest = [p for i, p in enumerate(fest) if i % 8 in (1, 4, 6)]
            for pts in fest:
                fig.fx_front.append(fil(pts, 0.42, col, op=op_ * fade))
            for pts in rad:
                fig.fx_front.append(fil(pts, 0.55, col, op=op_ * fade))
            if tl < SP_UNDO:
                fig.fx_front.append(E.boule(fig, hub, 4.0, 0, _SOIE, op=op_))
            # les cailloux arrachés volent encore, puis retombent
            if tl < SP_PLANT + 60:
                u = (tl - SP_OPEN) / (SP_PLANT + 60 - SP_OPEN)
                for (dx, dy, k) in ((-40, -14, 0), (38, -16, 1), (-28, -28, 2), (30, -30, 0)):
                    fig.fx_front.append(stone(fig, cx + dx * (0.7 + 0.3 * u), cy + dy * (1 - u) + 20 * u * u, 1.7, k, rot=160 * u + dx))
            # les fils plantés : la terre éclate à leur pied
            if SP_PLANT - 40 <= tl < SP_UNDO + 80:
                u = (tl - SP_PLANT + 40) / (SP_UNDO + 120 - SP_PLANT)
                for i, p in enumerate(ends):
                    side = 1 if p[0] > cx else -1
                    fig.fx_back.append(dust(fig, p[0] + side * 3 * u, GR - 2.5 - 2 * u, 3.4 * (0.6 + 0.6 * u), op=max(0.0, 1 - u)))
                    if u < 0.6:
                        fig.fx_front.append(stone(fig, p[0] + side * (2 + 5 * u), GR - 3 - 10 * u + 18 * u * u, 1.2, i, op=1 - u / 0.6, rot=300 * u))
            # le venin : des gouttes vertes prises dans les festons
            if SP_PLANT <= tl < SP_UNDO + 60:
                v = env(tl, SP_PLANT, SP_VENOM, SP_UNDO - 40, SP_UNDO + 60)
                for k, i in enumerate((2, 7, 11, 17, 22)):
                    if i < len(fest):
                        p = fest[i][len(fest[i]) // 2]
                        fig.fx_front.append(drop(fig, p[0], p[1] + 0.6 + (tl - SP_PLANT) * 0.004, 0.75, op=v))
    return f


START = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael et Oboro)."""
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
    # l'ombre douce au sol sous elle (entre les pointes des pattes)
    sh = Image.new('RGBA', (w, h))
    cx = (67 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 58 * k, fy - 3.0 * k, cx + 58 * k, fy + 3.0 * k], fill=(10, 4, 24, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 4.4), ('attack', ATTACK[-1][0] * K / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] * K / 1000),
           ('idle', 1.2), ('special', SPECIAL[-1][0] * K / 1000), ('idle', 1.8)]
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


def frame_svg(T, segs, cc, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    P['c1'], P['c2'] = P['c1'] + cc[0], P['c2'] + cc[1]      # le pendule + le balancement du repos (signe)
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return N.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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
    n = int(round(total * FPS))
    CC = cocoon_track(segs, n)
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.27, a_s + 0.46, a_s + 0.52, a_s + 0.58, a_s + 0.64, a_s + 0.72, a_s + 0.9,
                            s_s + 0.3, s_s + 0.5, s_s + 0.8, s_s + 0.88, s_s + 0.96, s_s + 1.05, s_s + 1.12,
                            s_s + 1.2, s_s + 1.38, s_s + 1.55, s_s + 1.7, s_s + 1.9]
        fr = []
        for T in moments:
            i = min(n - 1, int(round(T * FPS)))
            # les effets qui retiennent un point de départ : rejouer l'image d'avant
            fr.append(frame_svg(T, segs, CC[i]))
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
    fr = [frame_svg(i / FPS, segs, CC[i]) for i in range(n)]
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



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : la tache de soie à l'impact et le nœud de la toile d'UNE forme sans contour sombre, les
# cailloux en galets, la poussière et les flocons de soie en bouffées fondues, les gouttes de venin étirées, les
# éclats en lumières ; la pelote, la toile (fils) et l'attaque gardent leur dessin.
import effets_pro as E  # noqa: E402

_SOIE = dict(bord=(SILKC[3], SILKC[4], SILKC[4]), milieu=(SILKC[2], SILKC[1]), coeur=(SILKC[0], SILKC[1]), halo=SILKC[2], clair='#ffffff',
             fonce=SILKC[4], fumee=(SILKC[0], SILKC[2], SILKC[3]))
_VENIN = dict(bord=(VENOM[2], VENOM[3], VENOM[3]), milieu=(VENOM[1], VENOM[1]), coeur=('#ffffff', VENOM[0]), halo=VENOM[2], clair='#ffffff',
              fonce=VENOM[3], fumee=(VENOM[0], VENOM[1], VENOM[2]))
_PIERRE = (STONE[0], STONE[1], STONE[2], STONE[3], STONE[4], '#24142e')

E.accrocher(sys.modules[__name__], {
    'stone': lambda fig, x, y, r, k=0, op=1.0, rot=0.0: E.caillou(fig, x, y, r * 1.2, rot, seed=k, op=op, pierre=_PIERRE),
    'dust': lambda fig, cx, cy, r, op=1.0: E.nuage(fig, cx, cy, r * 1.15, 'terre', op=op, seed=int(cx) % 3, flat=0.75),
    'drop': lambda fig, x, y, r=1.0, op=1.0, ang=0.0: E.goutte(fig, x, y, 0, 40, r * 1.1, _VENIN, op=op),
    'puff': lambda fig, c, r, op=1.0: E.nuage(fig, c[0], c[1], r * 1.4, _SOIE, op=op, seed=int(c[0]) % 3),
    'flash': lambda fig, c, r, op: E.lumiere(fig, c, r * 1.3, op, _SOIE),
})


if __name__ == '__main__':
    main()
