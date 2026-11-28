# Venthys vectoriel ANIMÉ : mêmes durées et mêmes moments que les animations d'Elvyn (../elvyn/anim.py) — respiration,
# attaque de base « lame de vent », attaque spéciale « cyclone » — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/venthys/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/venthys/)
#   python3 refonte-graphique/ui-moderne/heros/venthys/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode (comme Elvyn) : le dessin (venthys.py) est fait de morceaux ; chaque image le redessine dans une POSE (le bassin
# monte et descend, les genoux plient — les pieds ne glissent pas —, le buste se penche depuis le bassin, la tête, les
# bras suivent les poignets, les lames tournent dans les poings ; crinière, écharpe, queue et houppe flottent au vent).
# Les poses clés sont reliées par des courbes douces sans dépassement (24 images par seconde). Les effets de vent (rubans
# de vent en spirale, lame de vent en croissant, feuilles, bouffées d'air, cyclone) sont dessinés dans le même style :
# dégradés, un seul contour, aucun flou, aucune rayure.
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
import venthys as V  # noqa: E402
from atelier import Mat, lock, sm, ribbon, limb, ellipse, resample, sides, f as fm  # noqa: E402

ROOT = V.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'venthys')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-venthys') + '/_images'
FPS = 24
GR = V.GRD
VIEW = tuple(float(v) for v in os.environ["VIEWV"].split(",")) if os.environ.get("VIEWV") else (-41, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9) : la même que celle d'Elvyn
VW, VH = 1280, 720
WINK = '#174a58'                     # le contour des effets de vent (bleu-vert profond)
WA = V.WIND                          # blanc, écume, clair, menthe, vert d'eau, ombre, creux
FOE = (177.0, 77.0)                  # l'ennemi (milieu du corps)
LEAF = Mat('#e6ffc8', '#9ee27e', '#5cbc5e', '#2f8a5a', '#1c5a4a')

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


NUM = ['hipx', 'hipy', 'lean', 'headx', 'heady', 'tilt', 'mane', 'scarf', 'tail', 'tuft', 'nwx', 'nwy', 'fwx', 'fwy',
       'nb', 'fb', 'jaw']
PAIRS = {'hip': ('hipx', 'hipy'), 'head': ('headx', 'heady'), 'nw': ('nwx', 'nwy'), 'fw': ('fwx', 'fwy')}


def flat(k):
    d = dict(hipx=0, hipy=0, lean=0, headx=0, heady=0, tilt=0, mane=0, scarf=0, tail=0, tuft=0,
             nwx=V.NW0[0], nwy=V.NW0[1], fwx=V.FW0[0], fwy=V.FW0[1], nb=0, fb=0, jaw=0)
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
# 2) L'attaque de base « lame de vent » : il se ramasse (le bassin descend, le buste recule), la lame du fond descend en
# arrière contre la hanche pendant que le vent s'enroule autour d'elle ; il tranche d'un coup vers l'avant et vers
# le haut (le buste plonge, la lame proche part en balancier derrière) : une lame de vent en croissant file vers l'ennemi
# et l'entaille (croissant de lumière, rubans de vent, feuilles, bouffées d'air). Il revient en garde.
ATTACK = [
    (0, {}),
    (130, dict(fw=(80.0, 66.0), fb=-22, hip=(-0.6, 0.8), lean=-2, head=(-0.6, 0.4), nw=(37.6, 83.0), tail=1, tuft=1, mane=0.5, scarf=0.5)),
    (340, dict(fw=(76.4, 71.0), fb=-48, hip=(-1.2, 1.8), lean=-4, head=(-1.0, 0.8), tilt=-2, nw=(39.0, 84.0), nb=8, tail=2, tuft=2, mane=1, scarf=1)),
    (395, dict(fw=(89.6, 66.4), fb=40, hip=(1.6, 0.6), lean=6, head=(1.4, 1.0), tilt=3, nw=(34.4, 80.0), nb=-16, tail=-1.5, tuft=1, mane=-1, scarf=-1, jaw=0.3)),
    (470, dict(fw=(90.0, 66.0), fb=46, hip=(1.8, 0.8), lean=6.6, head=(1.6, 1.2), tilt=3.4, nw=(34.0, 79.6), nb=-20, tail=-2, tuft=-1, mane=-1.2, scarf=-1.2, jaw=0.25)),
    (640, dict(fw=(88.0, 64.0), fb=36, hip=(1.4, 0.6), lean=5.4, head=(1.2, 0.8), tilt=2.4, nw=(34.6, 80.4), nb=-14, tail=-1, tuft=-2, mane=-0.6, scarf=-0.6)),
    (800, dict(fw=(85.6, 62.4), fb=18, hip=(0.8, 0.3), lean=3, head=(0.6, 0.4), tilt=1, nw=(35.8, 81.6), nb=-6, tail=0.6, tuft=-1, mane=0.3, scarf=0.4)),
    (960, dict(fw=(84.2, 63.4), fb=6, hip=(0.0, 0.5), lean=0.6, tail=1, tuft=0.6, mane=0.5, scarf=0.6)),
    (1150, dict(tuft=0.5, mane=0.2, scarf=0.2)),
    (1300, {}),
]
ATT_CHARGE = (60, 395)          # le vent s'enroule autour de la lame
ATT_FIRE, ATT_HIT = 395, 545    # la lame de vent part, elle entaille l'ennemi

# 3) L'attaque spéciale « cyclone » : il se ramasse très bas, les deux lames ramenées contre lui ; le vent se lève autour
# de lui (rubans de vent qui montent en spirale du sol, feuilles qui tournent). Il se détend d'un coup : les deux lames
# tranchent vers l'avant en croix, un cyclone en naît, file sur le champ de bataille en grandissant et engloutit
# l'ennemi (éclat, trois entailles en croissant dans le tourbillon). Le cyclone se défait en montant, les feuilles et les
# bouffées d'air retombent.
SPECIAL = [
    (0, {}),
    (160, dict(fw=(80.0, 66.4), fb=-20, hip=(-0.8, 1.2), lean=-2, head=(-0.4, 0.6), nw=(39.4, 82.0), nb=10, tail=1, tuft=1, mane=0.6, scarf=0.6)),
    (400, dict(fw=(76.8, 70.6), fb=-46, hip=(-1.6, 2.6), lean=-5, head=(-1.0, 1.4), tilt=-2, nw=(42.0, 82.6), nb=26, tail=2, tuft=2, mane=1, scarf=1)),
    (700, dict(fw=(76.2, 71.4), fb=-52, hip=(-1.8, 3.0), lean=-5.6, head=(-1.2, 1.6), tilt=-2.6, nw=(42.6, 82.4), nb=30, tail=2.4, tuft=2, mane=1.2, scarf=1.2)),
    (790, dict(fw=(89.4, 66.6), fb=40, hip=(1.8, 0.0), lean=7, head=(1.6, 0.4), tilt=3, nw=(55.0, 79.0), nb=-40, tail=-2, tuft=1, mane=-1.2, scarf=-1.4, jaw=0.35)),
    (900, dict(fw=(89.8, 66.4), fb=46, hip=(2.0, 0.2), lean=7.4, head=(1.8, 0.6), tilt=3.4, nw=(55.6, 79.4), nb=-44, tail=-2.4, tuft=-1, mane=-1.3, scarf=-1.5, jaw=0.3)),
    (1180, dict(fw=(88.8, 66.0), fb=40, hip=(1.6, 0.2), lean=6.4, head=(1.6, 0.6), tilt=2.6, nw=(53.6, 79.6), nb=-36, tail=-1.2, tuft=-2, mane=-1.0, scarf=-1.2, jaw=0.15)),
    (1300, dict(fw=(87.4, 64.4), fb=34, hip=(1.4, 0.2), lean=5.6, head=(1.4, 0.4), tilt=2, nw=(50.0, 80.4), nb=-28, tail=0, tuft=-1, mane=-0.6, scarf=-0.8)),
    (1520, dict(fw=(86.0, 64.0), fb=20, hip=(0.8, 0.2), lean=3.6, head=(1.0, 0.2), tilt=1, nw=(44.0, 81.6), nb=-14, tail=1, mane=0.4, scarf=0.5)),
    (1760, dict(fw=(84.8, 63.0), fb=6, hip=(0.3, 0.3), lean=1.4, head=(0.4, 0.0), nw=(39.0, 82.4), nb=-4, tail=0.6, tuft=1, mane=0.6, scarf=0.6)),
    (1980, dict(hip=(0.0, 0.6), tail=-0.6, tuft=0.6, mane=-0.3, scarf=-0.3)),
    (2200, dict(tuft=-0.3)),
    (2400, {}),
]
SP_GATHER = (60, 760)           # le vent se lève autour de lui
SP_EMERGE = 760                 # le cyclone naît des deux lames
SP_HIT = 1260                   # il engloutit l'ennemi
SP_END = 1700                   # il se défait


# ======================================================================== la respiration (en boucle, 2 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : l'écharpe safran ondule plus fort dans le vent (deux grandes vagues par boucle) et ses pans montent
    puis retombent lentement. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus
    (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(wf=0.8, sph=2 * u, scarf=-1.4 * math.sin(u))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, hipy=0.5 * (0.5 - 0.5 * math.cos(u - 1.2)), heady=0.35 * math.sin(u - 0.6),
                tilt=0.7 * math.sin(u - 0.9), mane=0.4 * math.sin(u - 1.2), scarf=0.5 * math.sin(u - 0.4), tail=1.0 * math.sin(u),
                tuft=1.0 * math.sin(u - 0.9), fwy=0.45 * math.sin(u - 1.0), nwy=0.35 * math.sin(u - 1.6),
                fb=2.4 * math.sin(u - 1.3), nb=-2.0 * math.sin(u - 1.9))


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
    for key, (a, b) in PAIRS.items():
        P[key] = (P.pop(a), P.pop(b))
    P['ph'] = 2 * math.pi * T * 3 / IDLE_T         # la crinière : 3 ondes par boucle (0,9 par s avant le 27/11)
    sg = signe(T)                                  # le signe du repos : l'écharpe (anim.signe)
    P['wf'], P['scarf'] = w * sg['wf'], P['scarf'] + w * sg['scarf']
    P['sph'] = sg['sph']
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return P


# ======================================================================== les effets de vent (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, o in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl, '' if o == 1 else ' opacity="%g"' % o)
                  for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


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


def leaf(fig, x, y, ang, s=1.0, op=1.0):
    """Une feuille : une amande pointue aux deux bouts, une nervure, claire en haut à droite."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    P = lambda t, o: (x + u[0] * t * s + n[0] * o * s, y + u[1] * t * s + n[1] * o * s)   # noqa: E731
    sh = sm([P(-2.6, 0), P(-1.0, -1.25), P(1.2, -1.2), P(2.8, 0), P(1.0, 1.2), P(-1.2, 1.15)], sharp=(0, 3), t=0.9)
    gr = g_lin(fig, (x + 2 * s, y - 2 * s), (x - 2 * s, y + 2 * s), [(0, LEAF.light), (0.55, LEAF.base), (1, LEAF.shadow)])
    rib = ribbon([P(-2.2, 0.05), P(0, -0.1), P(2.3, 0.0)], [0.1, 0.3 * s, 0.1])
    return outlined([(sh, gr, 1), (rib, LEAF.shadow, 0.8)], w=0.8, op=op)


def puff(fig, cx, cy, r, op=1.0):
    """Une bouffée d'air : quelques boules claires réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.85 * r, cy + 0.2 * r, 0.7 * r), (cx - 0.8 * r, cy + 0.28 * r, 0.66 * r), (cx + 0.1 * r, cy - 0.5 * r, 0.6 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#ffffff'), (0.5, WA[1]), (1, WA[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), WINK, WINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def gust(fig, pts, w, op=1.0, ink=True):
    """Un ruban de vent : large et clair à la tête, effilé à la queue (le long d'une ligne, de la queue à la tête)."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = resample(pts, 12)
    ws = [0.15 + w * (i / 12) ** 0.8 * (1 - 0.35 * max(0, (i - 9) / 3)) for i in range(13)]
    left, right = sides(c, ws)
    sh = sm([c[0]] + left[1:] + right[1:][::-1], sharp=(0,), t=0.85)
    gr = g_lin(fig, c[0], c[-1], [(0, WA[3], 0.7), (0.6, WA[1]), (1, '#ffffff')])
    hl = ribbon([(p[0] + 0.25, p[1] - 0.35) for p in c[4:]], [0.1] + [w * 0.22] * 7 + [0.1])
    return outlined([(sh, gr, 1), (hl, '#ffffff', 0.8)], w=1.0 if ink else 0, op=op)


def spiral_runs(c, R0, R1, a0, a1, w, tilt, n=30, y_rise=0.0):
    """Un ruban en spirale autour d'un cercle penché (de a0 à a1, rayon R0 → R1, qui monte de y_rise) : la forme
    entière, et ses morceaux qui passent DEVANT (bas du cercle)."""
    rows = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        R = R0 + (R1 - R0) * t
        ww = w * math.sin(math.pi * min(1.0, 0.1 + 0.9 * t)) ** 0.5 * (0.25 + 0.75 * t)
        yy = c[1] - y_rise * t
        rows.append((math.sin(a) > 0, (c[0] + (R + ww / 2) * math.cos(a), yy + (R + ww / 2) * math.sin(a) * tilt),
                     (c[0] + (R - ww / 2) * math.cos(a), yy + (R - ww / 2) * math.sin(a) * tilt)))

    def shape(rr):
        o = [r[1] for r in rr]
        i_ = [r[2] for r in rr]
        return sm(o + i_[::-1], sharp=(0, len(o) - 1, len(o), 2 * len(o) - 1), t=0.6)
    whole = shape(rows)
    fronts, cur = [], []
    for r in rows:
        if r[0]:
            cur.append(r)
        elif cur:
            cur.append(r)
            fronts.append(cur)
            cur = []
    if len(cur) > 1:
        fronts.append(cur)
    return whole, [shape(f_) for f_ in fronts if len(f_) > 1]


def whirl(fig, c, R, arms, w, rot, op=1.0, tilt=0.5, span=160, rise=0.0):
    """Des rubans de vent qui tournent autour d'un point (la lame, l'ennemi) : le ruban entier (et son contour) passe
    derrière, ses morceaux du bas repassent devant (sans contour : pas de joint visible)."""
    if op <= 0.02:
        return
    gr = g_lin(fig, (c[0] + R, c[1] - R), (c[0] - R, c[1] + R), [(0, '#ffffff'), (0.4, WA[1]), (0.75, WA[2]), (1, WA[3])])
    for j in range(arms):
        a0 = rot + 360.0 / arms * j
        whole, fronts = spiral_runs(c, R + 3.0, R - 1.2, a0, a0 + span, w, tilt, y_rise=rise)
        fig.fx_back.append(outlined([(whole, gr, 1)], w=1.0, op=op))
        for sh in fronts:
            fig.fx_front.append('<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op))


def wind_crescent(fig, c, ang, size, op=1.0, trail=0.0):
    """La lame de vent : un grand croissant (le dos bombé vers l'avant), blanc au cœur, menthe au bord, sous un contour ;
    derrière lui deux sillages qui s'effilent."""
    if op <= 0.02:
        return ''
    grip, blade, edge, hollow = V.crescent_shapes(size)
    out = []
    from atelier import xf
    b = xf(blade, c[0], c[1], ang)
    e = xf(edge, c[0], c[1], ang)
    bx0, by0, bx1, by1 = b.bbox()
    gr = g_lin(fig, (bx1, by0), (bx0, by1), [(0, '#ffffff'), (0.45, WA[1]), (1, WA[3])])
    parts = [(b, gr, 1), (e, '#ffffff', 0.9)]
    if trail > 0:
        a = math.radians(ang)
        u = (math.cos(a), math.sin(a))
        n = (-u[1], u[0])
        for sgn, k in ((1, 1.0), (-1, 0.8)):
            p0 = (c[0] + n[0] * 6.6 * size * sgn, c[1] + n[1] * 6.6 * size * sgn)
            pts = [(p0[0] - u[0] * trail * k * (1 - i / 8) + n[0] * 0.8 * sgn * math.sin(i), p0[1] - u[1] * trail * k * (1 - i / 8) + n[1] * 0.8 * sgn * math.sin(i)) for i in range(9)]
            out.append(gust(fig, pts, 2.4 * size, op=op))
    out.append(outlined(parts, w=1.2, op=op))
    return ''.join(out)


def slash_mark(fig, c, ang, L, k, op=1.0):
    """Une entaille de lumière : un croissant très fin qui s'ouvre d'un coup (k : 0 → 1) puis s'efface."""
    if op <= 0.02 or k <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    pts = []
    for i in range(13):
        t = -1 + 2 * i / 12
        pts.append((c[0] + u[0] * t * L * k / 2 + n[0] * (1 - t * t) * L * 0.16, c[1] + u[1] * t * L * k / 2 + n[1] * (1 - t * t) * L * 0.16))
    ws = [0.1] + [2.6 * (1 - abs(-1 + 2 * i / 12)) ** 0.7 + 0.2 for i in range(1, 12)] + [0.1]
    sh = ribbon(pts, ws)
    core = ribbon(pts, [w_ * 0.45 for w_ in ws])
    return outlined([(sh, WA[2], 1), (core, '#ffffff', 1)], w=1.0, op=op)


# ---- l'attaque de base : la lame de vent

def blade_center(ctx, which='f'):
    """Le milieu du croissant de la lame (dans le dessin), d'après la poignée et son angle."""
    W, a = ctx['fb'] if which == 'f' else ctx['nb']
    r = math.radians(a)
    d = 9.6 * V.BK
    return (W[0] + math.cos(r) * d, W[1] + math.sin(r) * d)


SHOT = {}


def fx_attack(tl):
    def f(fig, ctx):
        bc = blade_center(ctx)
        # la charge : le vent s'enroule autour de la lame armée contre la hanche
        ch = env(tl, ATT_CHARGE[0], ATT_CHARGE[0] + 120, ATT_FIRE - 40, ATT_FIRE + 30)
        if ch > 0:
            k = (tl - ATT_CHARGE[0]) / (ATT_FIRE - ATT_CHARGE[0])
            whirl(fig, bc, 12 - 3 * k, 2 if k < 0.5 else 3, 2.6 + 0.8 * k, -tl * 1.1, op=ch, tilt=0.45)
            for i in range(4):
                u = ((tl - ATT_CHARGE[0]) / 300.0 + i * 0.25) % 1.0
                a = i * 1.7 + u * 4.0
                fig.fx_front.append(leaf(fig, bc[0] + 13 * (1 - u) * math.cos(a), bc[1] + 8 * (1 - u) * math.sin(a), math.degrees(a) + 90, 0.9, op=ch * min(1, u * 5) * (1 - u)))
        # le coup : l'arc de la lame (un croissant de vent qui suit le geste), puis la lame de vent qui file
        if ATT_FIRE - 30 <= tl < ATT_FIRE + 90:
            e = env(tl, ATT_FIRE - 30, ATT_FIRE, ATT_FIRE + 20, ATT_FIRE + 90)
            p0 = ctx['fw']
            arc = [(p0[0] - 4 + 15 * math.cos(math.radians(a)), p0[1] + 2 + 15 * math.sin(math.radians(a))) for a in range(110, -41, -10)]
            fig.fx_back.append(gust(fig, arc, 4.0, op=e))
        if ATT_FIRE <= tl < ATT_HIT:
            if 'p0' not in SHOT:
                SHOT['p0'] = (bc[0] + 4, bc[1])
            p0 = SHOT['p0']
            s = smooth((tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)) * 0.85 + 0.15 * (tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)
            mid = ((p0[0] + FOE[0]) / 2, min(p0[1], FOE[1]) - 8)
            c = ((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * mid[0] + s * s * FOE[0], (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * mid[1] + s * s * FOE[1])
            tan = (2 * (1 - s) * (mid[0] - p0[0]) + 2 * s * (FOE[0] - mid[0]), 2 * (1 - s) * (mid[1] - p0[1]) + 2 * s * (FOE[1] - mid[1]))
            ang = math.degrees(math.atan2(tan[1], tan[0]))
            fig.fx_front.append(wind_crescent(fig, c, ang, 1.35 + 0.25 * s, trail=10 + 18 * min(1, (tl - ATT_FIRE) / 80)))
        # l'entaille sur l'ennemi : un croissant de lumière, des rubans de vent qui s'ouvrent, feuilles et bouffées
        tau = (tl - ATT_HIT) / 1000.0
        if tau >= 0:
            c = FOE
            fl = env(tau, 0, 0.02, 0.05, 0.16)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="20" fill="%s"/>' % (fm(c[0]), fm(c[1]), g_rad(
                    fig, c, 20, [(0, '#ffffff', 0.8 * fl), (0.3, WA[1], 0.45 * fl), (1, WA[2], 0)])))
            k = smooth(tau / 0.06)
            fig.fx_front.append(slash_mark(fig, c, -35, 30, k, op=env(tau, 0, 0.01, 0.12, 0.3)))
            e = env(tau, 0, 0.06, 0.16, 0.42)
            if e > 0:
                for j, (a0, R) in enumerate(((200, 9), (20, 11), (110, 7))):
                    rr = R + 10 * tau
                    pts = [(c[0] + rr * math.cos(math.radians(a0 + d)), c[1] + rr * 0.7 * math.sin(math.radians(a0 + d))) for d in range(0, 121, 12)]
                    (fig.fx_back if j == 1 else fig.fx_front).append(gust(fig, pts, 3.2, op=e))
            if 0.04 < tau < 0.5:
                kk = (tau - 0.04) / 0.46
                fig.fx_back.append(puff(fig, c[0] - 2 - 6 * kk, c[1] + 2 - 3 * kk, 4.4 * (1 - 0.4 * kk), op=1 - kk))
                fig.fx_back.append(puff(fig, c[0] + 4 + 7 * kk, c[1] - 3 - 4 * kk, 3.4 * (1 - 0.4 * kk), op=1 - kk))
            for i, (vx, vy, sp) in enumerate(((-60, -70, 500), (40, -90, -600), (-90, -20, 420), (70, -40, -380), (-20, -110, 700), (90, -80, 520))):
                if 0.02 < tau < 0.8:
                    x = c[0] + vx * tau * (1 - 0.5 * tau)
                    y = c[1] + vy * tau + 60 * tau * tau
                    if y < GR - 1:
                        fig.fx_front.append(leaf(fig, x, y, sp * tau + i * 50, 0.95, op=min(1, (0.8 - tau) * 4)))
    return f


# ---- l'attaque spéciale : le cyclone

# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : cyclone d'UNE silhouette, rubans de vent d'un seul
# tenant, sans contour sombre, moins de feuilles et de bouffées ; même rythme, mêmes instants qu'avant)

import effets_pro as E  # noqa: E402


def tornado(fig, base, h, top_r, rot, op=1.0, lean=0.0):
    """Le cyclone posé au sol (effets_pro.tourbillon) : le voile et les rubans de derrière derrière, ceux de devant
    devant (ce qu'il engloutit passe entre les deux)."""
    if op <= 0.02 or h < 2:
        return
    b, f_ = E.tourbillon(fig, base, h, top_r, rot, 'vent', op=op, lean=lean, split=True)
    fig.fx_back.append(b)
    fig.fx_front.append(f_)


def _whirl(fig, c, R, w, rot, op, tilt=0.45, span=160, rise=0.0, arms=1):
    """Des rubans de vent qui tournent autour d'un point : chacun d'un seul tenant, derrière puis devant."""
    if op <= 0.02:
        return
    for j in range(arms):
        back, front, _ = E.spirale(fig, c, R + 3.0, R - 1.2, rot + 360.0 / arms * j, span, w, tilt, rise)
        fig.fx_back.append(E.group(back, op))
        fig.fx_front.append(E.group(front, op))


TW = {}


def fx_special(tl):
    def f(fig, ctx):
        fc = blade_center(ctx, 'f')
        nc = blade_center(ctx, 'n')
        # la charge : le vent se lève autour de lui (rubans qui montent du sol en spirale), quelques feuilles tournent
        ch = env(tl, SP_GATHER[0], SP_GATHER[0] + 160, SP_GATHER[1] - 60, SP_GATHER[1] + 60)
        if ch > 0:
            k = (tl - SP_GATHER[0]) / (SP_GATHER[1] - SP_GATHER[0])
            for j in range(3):
                rise = ((tl / 650.0) + j / 3.0) % 1.0
                o = ch * env(rise, 0, 0.2, 0.7, 1.0)
                _whirl(fig, (50, GR - 4 - 58 * rise), 30 - 8 * rise, 3.4 + 1.6 * k, -tl * 0.8 + j * 120, o, tilt=0.26, span=200)
            for i in range(5):
                u = ((tl / 900.0) + i / 5.0) % 1.0
                a = tl / 160.0 + i * 1.3
                x = 50 + (26 - 10 * u) * math.cos(a)
                y = GR - 3 - 64 * u + 7 * math.sin(a)
                (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(
                    E.feuille(fig, x, y, math.degrees(a) * 2 + i * 40, 0.95, op=ch * env(u, 0, 0.15, 0.8, 1.0)))
            _whirl(fig, fc, 9, 2.6, -tl * 1.3, ch * smooth(k * 2), span=150, arms=2)
            _whirl(fig, nc, 8, 2.4, tl * 1.2, ch * smooth(k * 2 - 0.4), span=150, arms=2)
        # le cyclone naît des lames : deux rubans courbes d'un seul tenant
        if SP_EMERGE - 20 <= tl < SP_EMERGE + 110:
            e = env(tl, SP_EMERGE - 20, SP_EMERGE + 10, SP_EMERGE + 40, SP_EMERGE + 110)
            for j, (cx, cy, rr, a0) in enumerate(((fc[0] - 4, fc[1], 15, -130), (nc[0] + 4, nc[1] - 4, 16, -70))):
                arc = [(cx + rr * math.cos(math.radians(a0 + d)), cy + rr * math.sin(math.radians(a0 + d))) for d in range(0, 161, 40)]
                fig.fx_front.append(E.ruban(fig, arc, 5.0, 'vent', op=e, kind='tete', halo=0.8))
        # il file vers l'ennemi en grandissant
        if tl >= SP_EMERGE:
            kk = min(1.0, (tl - SP_EMERGE) / (SP_HIT - SP_EMERGE))
            x = 96 + (FOE[0] - 96) * (smooth(kk) * 0.8 + 0.2 * kk)
            grow = 0.35 + 0.65 * smooth(kk)
            fade = 1.0
            hh = 70 * grow
            if tl > SP_END:
                q = min(1.0, (tl - SP_END) / 450.0)
                fade = 1 - q
                hh = 70 * (1 - 0.3 * q)
            base_y = GR - (0 if tl <= SP_END else 30 * smooth((tl - SP_END) / 450.0))
            if fade > 0.02:
                tornado(fig, (x, base_y), hh, 17 * grow, tl * 1.4, op=fade, lean=-0.4 + 0.4 * kk)
                # le cyclone soulève une bouffée d'air clair au sol
                if tl < SP_END:
                    for j in range(2):
                        u = ((tl / 360.0) + j / 2.0) % 1.0
                        fig.fx_back.append(E.nuage(fig, x - 6 + 12 * j + 7 * u * (1 if j else -1), GR - 2.5 - 3 * u,
                                                   3.0 * (1 - 0.4 * u) * grow, 'vent', op=0.85 * (1 - u), seed=j))
                # quelques feuilles prises dans le cyclone
                for i in range(4):
                    a = tl / 90.0 + i * 1.6
                    t = ((tl / 700.0) + i / 4.0) % 1.0
                    r = 3 + 15 * grow * t
                    lx, ly = x + r * math.cos(a), base_y - hh * t + r * 0.28 * math.sin(a)
                    (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(
                        E.feuille(fig, lx, ly, math.degrees(a) * 1.5, 1.0, op=fade * env(t, 0, 0.1, 0.85, 1.0)))
        # l'éclat sur l'ennemi, trois entailles de lumière en croissant dans le tourbillon
        if tl >= SP_HIT - 20:
            tg = tl - SP_HIT
            fl = env(tg, -20, 0, 30, 160)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(FOE[0]), fm(FOE[1]), fm(90), g_rad(
                    fig, FOE, 90, [(0, '#ffffff', 0.8 * fl), (0.16, WA[1], 0.5 * fl), (0.45, WA[2], 0.16 * fl), (1, WA[3], 0)])))
            for j, (t0, ang, dx, dy) in enumerate(((0, -40, 0, -4), (110, 30, 3, 2), (230, -80, -2, -10))):
                u = (tg - t0) / 1000.0
                if 0 <= u < 0.3:
                    fig.fx_front.append(E.entaille(fig, (FOE[0] + dx, FOE[1] + dy), ang, 32, smooth(u / 0.05), 'vent',
                                                   op=env(u, 0, 0.01, 0.1, 0.3)))
            # à la fin : le cyclone se défait, les bouffées montent et s'étalent, quelques feuilles retombent
            fk = (tl - SP_END) / 1000.0
            if 0 < fk < 0.9:
                o = env(fk, 0, 0.1, 0.5, 0.9)
                for j, (dx, dy, rr, sp) in enumerate(((-12, -12, 4.6, -16), (8, -30, 4.2, 14), (16, -8, 3.4, 22))):
                    fig.fx_back.append(E.nuage(fig, FOE[0] + dx + sp * fk, GR + dy - 12 * fk, rr * (0.8 + 0.5 * fk), 'vent',
                                               op=0.9 * o, seed=j))
                for i in range(5):
                    x = FOE[0] - 22 + i * 11 + 6 * math.sin(fk * 5 + i)
                    y = GR - 60 + 8 * (i % 3) + 50 * fk
                    if y < GR - 1:
                        fig.fx_front.append(E.feuille(fig, x, y, 40 * math.sin(fk * 6 + i) + i * 30, 1.0, op=o))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros (comme les vidéos de Kael et d'Elvyn)."""
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
    cx = (48 - x0) * k
    sd.ellipse([cx - 42 * k, fy - 3.0 * k, cx + 42 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : repos ×2, attaque ×2, spéciale ×1 (comme Kael et Elvyn)."""
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
            SHOT.clear()
            TW.clear()
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    return V.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        i_ = sys.argv.index('--planche')
        arg = sys.argv[i_ + 1] if len(sys.argv) > i_ + 1 else ''
        if arg:
            moments = [float(v) for v in arg.split(',')]
        else:
            moments = [1.0, a_s + 0.2, a_s + 0.36, a_s + 0.45, a_s + 0.56, a_s + 0.68,
                       s_s + 0.4, s_s + 0.7, s_s + 0.85, s_s + 1.0, s_s + 1.15, s_s + 1.28, s_s + 1.45, s_s + 1.8, s_s + 2.0, 3.35]
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


if __name__ == '__main__':
    main()
