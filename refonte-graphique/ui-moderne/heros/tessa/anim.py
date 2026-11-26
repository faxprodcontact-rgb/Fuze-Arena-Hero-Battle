# Tessa vectorielle ANIMÉE (refonte de tous les héros, 26/11/2026, sur le modèle de Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/tessa/build.py) — l'affût du rapace (respiration, tête
# qui reste fixe puis se recale par à-coups comme un oiseau, regard qui se fixe, ailes qui respirent, plumes du cou qui
# frémissent, clignement), le tir (la flèche part dans un tourbillon de vent, la corde claque et vibre, une volute dépose
# une nouvelle flèche), l'attaque spéciale « Serres du ciel » (elle hérisse ses ailes, tire trois flèches qui montent en
# spirale et se fondent en un aigle de vent ; l'aigle crie, fond en piqué sur l'ennemi, serres en avant, et éclate) —
# dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/tessa/anim.py              # → anim.gif + anim.mp4 dans pixel/sortie/ui/vecto/tessa/
#   python3 refonte-graphique/ui-moderne/heros/tessa/anim.py --planche    # seulement une planche d'images clés (contrôle)
#   python3 refonte-graphique/ui-moderne/heros/tessa/anim.py --planche a0.3,s1.2   # … à ces instants (a = attaque, s = spéciale)
#
# Méthode (celle de Kael) : le dessin (tessa.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste
# qui respire et se penche depuis les hanches, tête, plumes du cou, ailes qui se soulèvent et s'ouvrent en éventail, bras
# proche placé par cinématique inverse depuis le poing qui tient la corde, arc qui se bande ou se détend, corde tendue
# jusqu'à l'encoche ou libre qui vibre). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps :
# visée tenue, lâcher très court, retour) reliées par des courbes douces sans dépassement, 24 images par seconde. Les
# effets de vent (anneaux autour de la flèche, traînées, volutes, croissants, l'aigle de vent, poussière, plumes) sont
# dessinés dans le même style : dégradés, un seul contour, aucun flou SVG, jamais de rayons droits répétés.
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
import tessa as T  # noqa: E402
from atelier import sm, ribbon, ellipse, resample, bez, limb, f as fm  # noqa: E402
from outils import plume, unit, lerp, add, norm  # noqa: E402

ROOT = T.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'tessa')
TMP = os.environ.get('TESSA_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-26, -42, 290, 163.125)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = T.GRD
INK = '#1f1238'
FOE = (222.0, 84.0)                   # l'ennemi (milieu du corps) : là où file la flèche
IMPACT = (222.0, GR - 6.0)            # là où frappe l'aigle de vent
APEX = (184.0, 10.0)                 # là-haut, à droite : l'aigle de vent s'y forme
# le vent (mêmes tons que les effets d'Eldra, Myrr et Orin) : blanc, blanc bleuté, cyan pâle, jade clair, jade, jade sombre
WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                      # le contour des effets de vent
DUST = ['#f6e4c0', '#d6b68a', '#a07c64', '#705456']


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


NUM = ['crouch', 'lean', 'tilt', 'fix', 'ruff', 'wn_lift', 'wn_spread', 'wf_lift', 'wf_spread', 'open', 'arrow', 'free',
       'bulge', 'relax', 'bow_dx', 'bow_tilt', 'hx', 'hy', 'headx', 'heady', 'wave']
H0 = T.HAND0


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, fix=0, ruff=0, wn_lift=0, wn_spread=0, wf_lift=0, wf_spread=0, open=0, arrow=1, free=0,
             bulge=0, relax=0, bow_dx=0, bow_tilt=0, hx=H0[0], hy=H0[1], headx=0, heady=0, wave=0)
    for key, v in k.items():
        if key == 'hand':                     # le poing : décalage le long de la flèche (− = il tire plus loin)
            d['hx'], d['hy'] = H0[0] + v[0], H0[1] + v[1]
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
# 2) Le tir (pixel : ATTAQUE). Elle fixe la cible (la tête plonge vers la flèche, le regard se durcit), bande encore
# l'arc (tenue) ; un petit tourbillon s'enroule autour de la pointe. Elle lâche : la flèche file dans un tourbillon de
# vent, la corde claque et vibre, la main s'ouvre en arrière, l'arc saute en avant et se détend, les plumes du cou
# frémissent. Puis la main revient : une volute dépose une nouvelle flèche sur la corde, qu'elle bande de nouveau.
REL = 400                     # l'instant du lâcher (ms)
ATTACK = [
    (0, {}),
    (110, dict(head=(0.8, 0.8), fix=1, hand=(-1, 0))),
    (360, dict(head=(0.8, 0.8), fix=1, hand=(-3, 0), relax=-1, lean=-1, wn_lift=-1.5, wf_lift=-1)),
    (REL - 10, dict(head=(0.8, 0.8), fix=1, hand=(-3.2, 0), relax=-1.1, lean=-1.1, wn_lift=-1.6, wf_lift=-1)),
    (REL + 50, dict(head=(0, 0), fix=0, hand=(-6, 0.4), open=1, arrow=0, free=1, bulge=3, relax=1.6, bow_dx=1, bow_tilt=1.4,
                    lean=-1.2, wn_lift=1.4, wf_lift=1, ruff=2)),
    (REL + 120, dict(hand=(-6.4, 0.5), open=1, arrow=0, free=1, bulge=-2, relax=1.4, bow_dx=0.6, bow_tilt=0.6, lean=-0.6,
                     wn_lift=1, wf_lift=0.6, ruff=1)),
    (REL + 200, dict(hand=(-6, 0.4), open=1, arrow=0, free=1, bulge=1, relax=1, bow_dx=0.2, ruff=0.5)),
    (REL + 260, dict(hand=(-3, 0.2), open=1, arrow=0, free=1, bulge=0, relax=0.9)),
    (REL + 340, dict(hand=(6, 0), open=0, arrow=0, free=1, relax=0.8)),
    (REL + 400, dict(hand=(8, 0), open=0, arrow=1, free=0, relax=0.7)),
    (REL + 520, dict(hand=(3, 0), relax=0.2)),
    (REL + 640, dict(head=(0.8, 0), fix=1)),
    (1150, {}),
]

# 3) L'attaque spéciale « Serres du ciel » (pixel : SPECIALE). Elle relève la tête vers le ciel par à-coups, hérisse ses
# ailes, bande l'arc à l'extrême (trois tourbillons tournent autour de la pointe, des plumes de vent y sont aspirées).
# Elle lâche en rabattant les ailes (poussière sous ses serres) : trois flèches montent en se tressant, se fondent en un
# aigle de vent qui ouvre les ailes et crie, puis fond en piqué, serres en avant. Arrêt sur l'image à l'impact : le vent
# éclate en deux grands croissants au ras du sol, des plumes volent puis retombent. Elle replie ses ailes et réencoche.
SREL = 720                    # le lâcher
S_EAGLE = 980                 # l'aigle naît là-haut
S_DIVE = 1420                 # il fond en piqué
S_HIT = 1560                  # l'impact
SPECIAL = [
    (0, {}),
    (130, dict(head=(1, -1), fix=1, wn_lift=1, ruff=1)),
    (200, dict(head=(1, -1), fix=1, tilt=-4, wn_lift=2, wn_spread=5, wf_lift=1, wf_spread=3, ruff=2, hand=(-1, 0))),
    (330, dict(head=(1, -0.5), fix=1, tilt=-5, wn_lift=3.5, wn_spread=10, wf_lift=2, wf_spread=7, ruff=3, hand=(-2, 0), relax=-1)),
    (420, dict(head=(1, 0), fix=1, tilt=-9, wn_lift=5, wn_spread=15, wf_lift=3, wf_spread=10, ruff=3, hand=(-3, 0), relax=-2, lean=-1)),
    (SREL - 10, dict(head=(1, 0), fix=1, tilt=-10, wn_lift=5.6, wn_spread=17, wf_lift=3.4, wf_spread=11, ruff=3, hand=(-3.4, 0),
                     relax=-2.2, lean=-1.2)),
    (SREL + 50, dict(head=(0, -0.6), tilt=-12, wn_lift=-3, wn_spread=0, wf_lift=-2, wf_spread=0, ruff=2, hand=(-6, 0.4), open=1,
                     arrow=0, free=1, bulge=3, relax=1.6, bow_dx=1, bow_tilt=1.4, lean=-1.2, crouch=0.8)),
    (SREL + 130, dict(head=(0, -1), tilt=-13, wn_lift=0, wf_lift=0, ruff=1, hand=(-6.4, 0.5), open=1, arrow=0, free=1, bulge=-2,
                      relax=1.4, bow_dx=0.5, bow_tilt=0.6, lean=-0.6, crouch=0.4)),
    (S_EAGLE, dict(head=(1, -1), fix=1, tilt=-14, wn_lift=1, hand=(-6, 0.4), open=1, arrow=0, free=1, bulge=0, relax=1)),
    (S_DIVE, dict(head=(1, -1), fix=1, tilt=-12, wn_lift=1, hand=(-6, 0.4), open=1, arrow=0, free=1, relax=1)),
    (S_HIT, dict(head=(1, 0.4), fix=1, tilt=1, wn_lift=0, ruff=2, hand=(-6, 0.4), open=1, arrow=0, free=1, relax=1, lean=0.6)),
    (S_HIT + 300, dict(head=(0, 0), tilt=0, ruff=1, hand=(-5, 0.3), open=1, arrow=0, free=1, relax=0.9)),
    (S_HIT + 420, dict(hand=(6, 0), open=0, arrow=0, free=1, relax=0.8)),
    (S_HIT + 480, dict(hand=(8, 0), open=0, arrow=1, free=0, relax=0.7)),
    (S_HIT + 620, dict(hand=(3, 0), relax=0.2)),
    (S_HIT + 760, dict(head=(0.8, 0), fix=1)),
    (2500, {}),
]

IDLE_T = 2.4                  # la respiration : un cycle (s)


# ======================================================================== la respiration et l'affût (en boucle)

def step(t, a, b):
    """0 avant a, 1 après b (transition très courte et douce : un à-coup d'oiseau)."""
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)


def idle_offsets(T_):
    u = 2 * math.pi * T_ / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # la tête reste fixe dans l'espace quand le buste respire (elle compense), puis se recale d'un coup ; une fois sur
    # deux elle avance par à-coup et se fixe sur la cible (le regard se durcit), puis revient
    tl = T_ % (2 * IDLE_T)
    hx = 0.8 * (step(tl, 1.30, 1.38) - step(tl, 2.62, 2.70)) + 0.5 * (step(tl, 3.6, 3.66) - step(tl, 4.3, 4.36))
    fix = step(tl, 1.30, 1.38) - step(tl, 2.62, 2.70)
    # compensation du souffle, recalée par à-coups : la tête « colle » à sa place pendant que le buste monte ou
    # descend, puis rattrape le corps d'un coup (toutes les 0,6 s, en deux images)
    tc = T_ % IDLE_T
    k0 = math.floor(tc / 0.6) * 0.6
    snap = step(tc - k0, 0.0, 0.08)
    held = 0.5 - 0.5 * math.cos(2 * math.pi * (k0 - 0.6) / IDLE_T)
    now0 = 0.5 - 0.5 * math.cos(2 * math.pi * k0 / IDLE_T)
    q = held + (now0 - held) * snap
    lock = 0.6 * (br - q)
    return dict(breath=br, crouch=0.35 * (0.5 - 0.5 * math.cos(u - 1.2)), headx=hx, heady=lock, fix=fix,
                wn_lift=1.3 * math.sin(u - 1.0), wf_lift=1.0 * math.sin(u - 1.4), ruff=0.25 + 0.25 * math.sin(u * 2 + 0.4),
                wave=0.3 * math.sin(u - 0.6))


def pose_at(T_, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    P = {}
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T_ - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        # la respiration s'efface au début de l'action et revient à la fin
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T_)
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['fix'] = max(src['fix'], w * idl['fix'])
    if act:
        # ce qui ne se fond pas : la flèche part d'un coup, la main s'ouvre, la corde claque (deux images) ; la nouvelle
        # flèche apparaît dans la volute, la corde revient à la main
        rel, back_ = (REL, REL + 400) if action == 'attack' else (SREL, S_HIT + 480)
        P['arrow'] = 0.0 if rel <= tl < back_ else 1.0
        P['open'] = 1.0 if rel <= tl < back_ - 120 else 0.0
        P['free'] = ease((tl - rel) / 50) * (1 - ease((tl - (back_ - 60)) / 60))
    P['breath'] = w * idl['breath']
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ph'] = 2 * math.pi * T_ * 0.9
    P['blink'] = 1.0 if (w > 0.95 and 3.05 <= (T_ % 4.8) < 3.13) else 0.0
    if P['fix'] > 0.5:
        P['fix'] = 1.0
    return P, tl


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, _ in shapes_fills if fl is not None) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


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


def spiral_pts(c, r, a0, turns, cw, n=14):
    """Une volute : la spirale qui s'enroule (sens horaire si cw), de rayon r vers le centre."""
    out = []
    s = 1 if cw else -1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + s * 2 * math.pi * turns * t
        rr = r * (1 - 0.72 * t)
        out.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return out


def stroke_fx(fig, pts, w, op=1.0, pale=False, core=True, ink=True):
    """Un ruban de vent effilé aux deux bouts le long d'une ligne (largeur max w), cœur blanc, un contour jade sombre."""
    if op <= 0.02 or w < 0.25 or len(pts) < 3:
        return ''
    n = len(pts)
    ws = [max(0.08, w * abs(math.sin(math.pi * i / (n - 1))) ** 0.7) for i in range(n)]
    sh = ribbon(pts, ws)
    items = [(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[3] if not pale else WIND[2]), (0.5, WIND[2]), (1, WIND[4] if not pale else WIND[3])]), 1)]
    if core:
        a, b = int(n * 0.2), int(n * 0.8)
        if b - a >= 3:
            items.append((ribbon(pts[a:b], [x * 0.38 for x in ws[a:b]]), WIND[0], 0.9))
    return outlined(items, w=1.0 if ink else 0, op=op)


def curl(fig, c, r, a0, turns=0.85, w=2.2, cw=False, op=1.0, lead=None):
    """Une volute de vent (avec, si `lead`, une petite queue droite qui y entre)."""
    pts = spiral_pts(c, r, a0, turns, cw, n=16)
    if lead:
        pts = resample([lead] + pts, 20)
    n = len(pts)
    ws = [max(0.08, w * (abs(math.sin(math.pi * min(1, i / (n - 1) * 1.6))) ** 0.6) * (1 - 0.85 * (i / (n - 1)) ** 1.5)) for i in range(n)]
    ws[0] = 0.1
    sh = ribbon(pts, ws)
    a, b = 2, int(n * 0.6)
    core = ribbon(pts[a:b], [x * 0.38 for x in ws[a:b]])
    gr = g_lin(fig, pts[0], c, [(0, WIND[3]), (0.6, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def arc_pts(C, rx, ry, a0, a1, n=24, tilt=0.0):
    out = []
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((C[0] + x * ct - y * st, C[1] + x * st + y * ct))
    return out


def crescent(fig, C, rx, ry, a0, a1, w, op=1.0, tilt=0.0, head=0.55):
    """Un croissant de vent le long d'un arc d'ellipse : plein vers `head` (0..1 le long de l'arc), effilé aux bouts."""
    if op <= 0.02 or w < 0.25:
        return ''
    pts = arc_pts(C, rx, ry, a0, a1, 28, tilt)
    n = len(pts)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        k = (t / head) if t < head else ((1 - t) / (1 - head))
        ws.append(max(0.08, w * k ** 0.7))
    sh = ribbon(pts, ws)
    a, b = int(n * 0.15), int(n * 0.85)
    core = ribbon(pts[a:b], [x * 0.4 for x in ws[a:b]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (head, WIND[2]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op)


def ring_halves(fig, c, rx, ry, w, op=1.0, lean=0.3):
    """Un anneau de vent autour d'un fût horizontal, vu de côté : une ellipse haute et étroite, penchée vers l'arrière ;
    la moitié de derrière (plus sombre) et celle de devant (claire), rendues à part."""
    def half(a0, a1, front):
        pts = []
        for i in range(19):
            a = math.radians(a0 + (a1 - a0) * i / 18)
            pts.append((c[0] + rx * math.cos(a) - lean * ry * math.sin(a), c[1] - ry * math.sin(a)))
        ws = [max(0.08, w * abs(math.sin(math.pi * i / 18)) ** 0.5) for i in range(19)]
        sh = ribbon(pts, ws)
        if front:
            core = ribbon(pts[3:16], [x * 0.4 for x in ws[3:16]])
            return outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])]), 1), (core, WIND[0], 0.9)], w=1.0, op=op)
        return outlined([(sh, g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])]), 1)], w=1.0, op=op * 0.9)
    return half(90, 270, False), half(-90, 90, True)


def puff(fig, cx, cy, r, op=1.0, tones=None, ink=None, hollow=0.0):
    """Une bouffée (vent pâle, ou poussière) : quelques boules réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    tones = tones or [WIND[0], WIND[1], WIND[3]]
    ink = ink or '#2c6a70'
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def dust(fig, cx, cy, r, op=1.0):
    return puff(fig, cx, cy, r, op, tones=[DUST[0], DUST[1], DUST[2]], ink='#5a4048')


def flash(fig, c, r, op=1.0):
    """Un éclat : un dégradé rond (blanc → cyan → transparent), pas un voile plat."""
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(
        fig, c, r, [(0, '#ffffff', 0.95 * op), (0.25, WIND[1], 0.75 * op), (0.6, WIND[2], 0.3 * op), (1, WIND[3], 0)]))


def feather_fx(fig, x, y, ang, kind='vent', s=1.0, op=1.0):
    """Une plume envolée (vent, blanche ou brune), un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    L = 7.0 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    p1 = add(add(p0, d, L * 0.33), sd, 0.4 * s)
    p2 = add(add(p0, d, L * 0.7), sd, 0.9 * s)
    sh = plume(p0, p1, p2, p3, 2.8 * s, n=10)
    quill = ribbon([p0, add(p0, d, L * 0.5), add(p0, d, L * 0.85)], [0.45 * s, 0.3 * s, 0.1])
    if kind == 'vent':
        gr = g_lin(fig, (x + 2, y - 2), (x - 2, y + 2), [(0, WIND[0]), (0.4, WIND[2]), (1, WIND[4])])
        return outlined([(sh, gr, 1), (quill, WIND[0], 0.8)], w=0.9, op=op)
    m = T.WHITE if kind == 'blanc' else T.BROWN
    gr = g_lin(fig, (x + 2, y - 2), (x - 2, y + 2), [(0, m.light), (0.5, m.base), (1, m.shadow)])
    return outlined([(sh, gr, 1), (quill, m.hi, 0.7)], ink=INK, w=0.9, op=op)


def arrow_fx(fig, tail, ang, kind='hero', op=1.0, L=58.0):
    """Une flèche en vol (le dessin de la flèche encochée) ; kind = 'vent' : une flèche de vent (jade, sans métal)."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    P_ = lambda u, v: (tail[0] + d[0] * u + sd[0] * v, tail[1] + d[1] * u + sd[1] * v)
    shaft = ribbon([P_(0.6, 0), P_(L * 0.5, 0), P_(L - 3.5, 0)], [1.1, 1.1, 1.1], sharp_ends=False)
    head = sm([P_(L - 5.4, -0.5), P_(L - 3.4, -2.2), P_(L + 0.4, 0), P_(L - 3.4, 2.2), P_(L - 5.4, 0.5)], sharp=(0, 2, 4), t=0.7)
    vt = sm([P_(1.6, -0.5), P_(2.4, -3.4), P_(6.0, -3.4), P_(11.6, -0.5)], sharp=(0, 1, 3), t=0.7)
    vb = sm([P_(1.6, 0.5), P_(2.2, 3.0), P_(5.6, 3.2), P_(11.4, 0.5)], sharp=(0, 1, 3), t=0.7)
    if kind == 'hero':
        items = [(vb, g_lin(fig, P_(10, 0), P_(2, 3), [(0, T.BROWN.light), (1, T.BROWN.shadow)]), 1),
                 (shaft, g_lin(fig, P_(0, -1), P_(0, 1), [(0, T.SHAFT.light), (0.5, T.SHAFT.base), (1, T.SHAFT.shadow)]), 1),
                 (vt, g_lin(fig, P_(10, -3), P_(2, 0), [(0, '#ffffff'), (1, T.WHITE.base)]), 1),
                 (head, g_lin(fig, P_(L, -2), P_(L - 5, 2), [(0, T.STEEL.hi), (0.5, T.STEEL.light), (1, T.STEEL.shadow)]), 1)]
        return outlined(items, ink=INK, w=1.7, op=op)
    items = [(vb, g_lin(fig, P_(10, 0), P_(2, 3), [(0, WIND[3]), (1, WIND[4])]), 1),
             (shaft, g_lin(fig, P_(0, -1), P_(0, 1), [(0, WIND[1]), (1, WIND[3])]), 1),
             (vt, g_lin(fig, P_(10, -3), P_(2, 0), [(0, WIND[0]), (1, WIND[2])]), 1),
             (head, g_lin(fig, P_(L, -2), P_(L - 5, 2), [(0, WIND[0]), (0.5, WIND[2]), (1, WIND[4])]), 1)]
    return outlined(items, w=1.3, op=op)


# ---- l'aigle de vent (spéciale) : corps fuselé, tête de pygargue au bec crochu d'or, œil d'ambre sous l'arcade,
# grandes ailes de vent aux rémiges écartées (levées pour le cri, repliées en arrière pour le piqué), serres d'or.
# Dessiné dans un repère local (il regarde vers +x), à l'échelle s, tourné de rot degrés.

def eagle(fig, C, rot, s, pose, op=1.0, open_=1.0):
    if op <= 0.02:
        return '', ''
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def X(p):
        x, y = p[0] * s, p[1] * s
        return (C[0] + x * ca - y * sa, C[1] + x * sa + y * ca)

    def S(pts, sharp=(), t=0.9):
        return sm([X(p) for p in pts], sharp=sharp, t=t)
    cri = pose == 'cri'

    def wing(dx, dy, k):
        """Une aile d'une seule forme : le bord d'attaque, les grandes rémiges du bout écartées en doigts (pointes
        arrondies, creux entre elles), le bord de fuite en petits festons jusqu'au corps ; une bande claire de
        couvertures le long du bord d'attaque."""
        if cri:
            o = open_
            lead = [(-1, -5), (-4, -16 - 4 * o), (-8, -27 - 6 * o)]
            fingers = [(-20, -40 - 3 * o), (-26, -38 - 2 * o), (-31, -33 - o), (-34, -27)]
            trail = [(-29, -20), (-24, -14), (-17, -9), (-9, -5)]
        else:
            lead = [(2, -5), (-3, -9), (-9, -11)]
            fingers = [(-33, -9), (-35, -5), (-34, -1), (-31, 2)]
            trail = [(-24, 3), (-16, 3.4), (-8, 3)]
        tr = lambda p: (p[0] * k + dx, p[1] * k + dy)
        pts, sharp = [tr(p) for p in lead], []
        prev = lead[-1]
        for i, f_ in enumerate(fingers):
            # un creux avant chaque doigt (sauf le premier), le doigt pointu-arrondi
            if i > 0:
                q = fingers[i - 1]
                mid = lerp(q, f_, 0.5)
                c0 = lerp(mid, lead[-1] if cri else (-12, -4), 0.28)
                pts.append(tr(c0))
                sharp.append(len(pts) - 1)
            pts.append(tr(f_))
        for i, q in enumerate(trail):
            prev_ = trail[i - 1] if i else fingers[-1]
            m = lerp(prev_, q, 0.5)
            pts.append(tr(add(m, (1.2, 1.6) if cri else (0.6, 1.8))))
            pts.append(tr(q))
            sharp.append(len(pts) - 1)
        shape = S(pts, sharp=tuple(sharp), t=0.85)
        cov = S([tr(p) for p in lead] + [tr(lerp(lead[-1], fingers[0], 0.3)), tr(lerp(lead[-1], trail[0], 0.45)),
                                         tr(lerp(lead[1], trail[1], 0.45)), tr(lerp(lead[0], trail[-1], 0.5))], t=0.9)
        return shape, cov
    back, front = [], []
    # l'aile lointaine (derrière le corps), plus petite et plus sombre
    fwing, fcov = wing(2.5, -2.5 if cri else -1.5, 0.82)
    g_far = g_lin(fig, X((-4, -26)), X((-30, -10)), [(0, WIND[2]), (1, WIND[4])])
    back.append(outlined([(fwing, g_far, 1), (fcov, WIND[2], 0.7)], op=op))
    body = S([(13, -6), (5, -9), (-7, -7.6), (-17, -4), (-21, -1), (-17, 2.6), (-6, 5.4), (6, 5.6), (13, 2)])
    tail = S([(-17, -2.4), (-27, -5.6), (-31.6, -4.2), (-30, -1.0), (-33.0, 1.2), (-30.4, 3.4), (-31.4, 6.4), (-26.6, 6.0), (-17, 2.6)],
             sharp=(2, 3, 4, 5, 6))
    headp = S([(8, -7.6), (13, -12.4), (19.4, -13.2), (23.4, -10.6), (23.6, -6.4), (19, -3.6), (11, -2.6)])
    beak = (S([(21, -12.6), (25, -13), (28.4, -11.4), (29.6, -8.6), (28.2, -6.4), (27.8, -8.6), (25, -10), (21.6, -9.6)], sharp=(4,)) if cri else
            S([(21, -12), (25, -12.4), (28, -10.6), (29, -7.4), (27.6, -5.0), (27.2, -7.6), (25.2, -8.8), (21.6, -8.4)], sharp=(4,)))
    jaw = S([(21.6, -8.6), (26.4, -7.0), (27.4, -4.8), (22.4, -6.0)]) if cri else None
    gbody = g_lin(fig, X((12, -10)), X((-20, 6)), [(0, WIND[0]), (0.35, WIND[1]), (0.75, WIND[2]), (1, WIND[4])])
    gtail = g_lin(fig, X((-17, -3)), X((-32, 5)), [(0, WIND[2]), (1, WIND[4])])
    ghead = g_lin(fig, X((22, -13)), X((10, -3)), [(0, '#ffffff'), (1, WIND[1])])
    gbeak = g_lin(fig, X((26, -12)), X((25, -6)), [(0, T.BEAK.light), (0.5, T.BEAK.base), (1, T.BEAK.shadow)])
    # les serres d'or : pendantes au cri, lancées en avant (devant la tête) au piqué ; griffes d'ardoise
    legs = [((3, 3), (5, 10)), ((-3, 3), (-2, 9))] if cri else [((4, 4), (16, 7.5)), ((0, 4.6), (13, 9.6))]
    litems = []
    for a_, b_ in legs:
        litems.append((limb([X(a_), X(lerp(a_, b_, 0.5)), X(b_)], [2.4 * s, 2.0 * s, 1.8 * s]), gbeak, 1))
        d = norm((b_[0] - a_[0], b_[1] - a_[1]))
        sd = (-d[1], d[0])
        for side in (-1, 0, 1):
            t0 = add(b_, sd, side * 0.9)
            t1 = add(add(add(b_, d, 2.0), sd, side * 1.6), (-sd[0] * 0.0 + 0.6 * d[1], -0.6 * d[0]))
            litems.append((limb([X(t0), X(t1)], [1.1 * s, 0.8 * s]), T.CLAW.base, 1))
    items = [(tail, gtail, 1), (body, gbody, 1),
             (S([(-17, -3.6), (-6, -6.8), (6, -7.2), (10, -4.6), (0, -2.4), (-12, -0.8)]), WIND[0], 0.55),
             (headp, ghead, 1)]
    if jaw:
        items.append((jaw, g_lin(fig, X((24, -8)), X((24, -5)), [(0, T.BEAK.base), (1, T.BEAK.shadow)]), 1))
    items.append((beak, gbeak, 1))
    # l'œil d'ambre sous une arcade (une ombre jade au-dessus)
    items += [(S([(15.6, -11.4), (19.0, -12.0), (22.4, -11.0), (21.6, -10.0), (18.6, -10.6), (16.0, -10.4)]), WIND[4], 0.8),
              (ellipse(*X((19.4, -9.6)), 1.3 * s, 0.9 * s), T.EYE[1], 1), (ellipse(*X((19.9, -9.6)), 0.55 * s, 0.6 * s), T.EYE[3], 1)]
    front.append(outlined(litems + items if cri else items + litems, op=op))
    nwing, ncov = wing(0, 0, 1.0)
    g_near = g_lin(fig, X((-4, -30)), X((-32, -12)), [(0, WIND[0]), (0.45, WIND[2]), (1, WIND[3])])
    front.append(outlined([(nwing, g_near, 1), (ncov, WIND[0], 0.75)], op=op))
    return ''.join(back), ''.join(front)


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


# ======================================================================== le tir

def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        tip, nock = ctx['tip'], ctx['nock']
        back, front = fig.fx_back, fig.fx_front
        # la visée : un petit tourbillon s'enroule devant la pointe
        k = env(tl, 90, 200, REL - 40, REL + 20)
        if k > 0:
            front.append(curl(fig, (tip[0] + 3.6, tip[1] - 0.4), 3.4 + 0.6 * k, 90 + tl * 0.9, 0.9, 2.0 * k + 0.4, cw=True, op=k))
        # la flèche file (vitesse ~ 1,2 px/ms) dans son tourbillon : deux anneaux autour du fût, une traînée effilée
        tr = tl - REL
        if 0 <= tr <= 260:
            y = nock[1]
            x_tail = 60.0 + 1.25 * tr
            front.append(fly_arrow(fig, x_tail, y, tr))
        # la fin de la traînée qui pâlit et se défait en volute
        if 150 <= tr <= 420:
            fd = (tr - 150) / 270
            y = nock[1]
            x1 = 250 - 40 * fd
            x0 = 160 + 70 * fd
            pts = [(x0 + (x1 - x0) * i / 12, y + 0.3 * math.sin(i * 0.9)) for i in range(13)]
            back.append(stroke_fx(fig, pts, 2.4 * (1 - fd) + 0.4, op=1 - fd * 0.8, pale=True))
            back.append(curl(fig, (x0 + 4, y - 3.4), 3.8 - 1.2 * fd, 120, 0.85, 2.0 * (1 - fd) + 0.3, cw=False, op=1 - fd))
        # le claquement de la corde : un souffle en croissant devant l'arc, qui s'ouvre puis se défait
        k = env(tr, 0, 30, 70, 170)
        if k > 0:
            g = ctx['grip']
            front.append(crescent(fig, (g[0] + 2 + 6 * (tr / 170), g[1] + 0.5), 5 + 4 * tr / 170, 10 + 4 * tr / 170, -70, 70, 3.2 * k, op=k))
        # la nouvelle flèche : une volute de vent s'enroule autour du fût et la dépose sur la corde
        new_arrow(fig, ctx, tl - (REL + 340))
    return f


def fly_arrow(fig, x_tail, y, tr):
    """La flèche en vol et son tourbillon (deux anneaux de vent enroulés autour du fût, une traînée effilée)."""
    out = []
    L = 58.0
    trail = min(60, 0.9 * tr + 8)
    pts = [(x_tail - trail * i / 12, y + 0.25 * math.sin(i * 1.1 + tr * 0.05)) for i in range(13)][::-1]
    out.append(stroke_fx(fig, pts, 2.6, pale=True))
    rings = [(x_tail + L - 14 - 0.02 * tr, 2.0, 4.2 + 0.006 * tr, 2.4), (x_tail + L - 36 - 0.05 * tr, 2.4, 5.6 + 0.01 * tr, 2.0)]
    halves = [ring_halves(fig, (rx, y), a, b, w) for rx, a, b, w in rings]
    out += [h[0] for h in halves]
    out.append(arrow_fx(fig, (x_tail, y), 0, 'hero', L=L))
    out += [h[1] for h in halves]
    return ''.join(out)


def new_arrow(fig, ctx, tn):
    """tn = 0 quand la main revient à la corde : la volute s'enroule autour du fût (avant et après l'apparition)."""
    if -60 <= tn <= 200:
        k = env(tn, -60, 0, 60, 200)
        nock = ctx['nock']
        y = nock[1]
        x = nock[0] + 28
        a0 = 200 + tn * 1.2
        pts = [(x + 22 * math.cos(math.radians(a)), y + 4 * math.sin(math.radians(a))) for a in [a0 + i * 9 for i in range(17)]]
        fig.fx_front.append(stroke_fx(fig, pts, 2.4 * k + 0.3, op=k))
        pts = [(x + 22 * math.cos(math.radians(a)), y + 4 * math.sin(math.radians(a))) for a in [a0 - 180 + i * 9 for i in range(17)]]
        fig.fx_back.append(stroke_fx(fig, pts, 2.0 * k + 0.3, op=k * 0.9))
        fig.fx_front.append(curl(fig, (nock[0] + 54, y - 3.2), 3.2, 200 + tn, 0.8, 2.0 * k + 0.3, cw=True, op=k))


# ======================================================================== la spéciale « Serres du ciel »

def volley_path(p0):
    return resample(bez(p0, (p0[0] + 30, p0[1] - 2), (APEX[0] - 22, APEX[1] + 44), APEX, 60), 120)


def path_at(pts, s):
    s = max(0.0, min(1.0, s))
    n = len(pts) - 1
    i = min(n - 1, int(s * n))
    t = s * n - i
    p = lerp(pts[i], pts[i + 1], t)
    d = norm((pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
    return p, d


ARROWS3 = [(0.0, 'hero'), (2 * math.pi / 3, 'vent'), (4 * math.pi / 3, 'vent')]
FEATHERS = [(-2.6, -6.5, 'vent', 0), (2.0, -7.5, 'vent', 1), (3.8, -4.8, 'brun', 2), (-4.0, -3.6, 'blanc', 0),
            (0.6, -8.6, 'blanc', 1), (-1.2, -5.0, 'brun', 1), (4.6, -6.6, 'vent', 2)]
P0_VOLLEY = [None]


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        tip, nock = ctx['tip'], ctx['nock']
        back, front = fig.fx_back, fig.fx_front
        feet = (64.0, GR)
        # ---- la charge : trois tourbillons tournent autour de la pointe et s'y resserrent ; des plumes de vent sont
        # aspirées vers la pointe ; le vent se lève au ras du sol sous ses serres
        kc = env(tl, 120, 260, SREL - 40, SREL + 20)
        if kc > 0:
            lv = ease((tl - 120) / (SREL - 160))
            R = 12 - 7 * lv
            for i in range(3):
                a = 90 + i * 120 + tl * 0.55
                c = (tip[0] + 3 + R * math.cos(math.radians(a)), tip[1] + 0.8 * R * math.sin(math.radians(a)))
                (front if i != 1 else back).append(curl(fig, c, 4.4 - 1.4 * lv, a + 90, 0.85, 2.4 * kc, cw=True, op=kc))
            if lv > 0.75:
                front.append(flash(fig, (tip[0] + 2, tip[1]), 4 + 3 * (lv - 0.75) * 4, op=kc * (lv - 0.75) * 4))
            src = [(feet[0] - 40, GR - 60), (feet[0] - 30, GR - 14), (feet[0] + 24, GR - 8)]
            for i, (sx, sy) in enumerate(src):
                t = min(1.0, lv * 1.15 - 0.1 * i)
                if t <= 0:
                    continue
                x = sx + (tip[0] - sx) * t
                y = sy + (tip[1] - sy) * t - 14 * math.sin(math.pi * t)
                (front if i % 2 else back).append(feather_fx(fig, x, y, -30 + 140 * t + 40 * i, 'vent', 0.9, op=kc * (1 - max(0, t - 0.85) / 0.15)))
            pts = [(feet[0] + 28 * math.cos(math.radians(a)), GR - 1.5 + 3 * math.sin(math.radians(a))) for a in range(200, 345, 9)]
            back.append(stroke_fx(fig, pts, 1.2 + 1.4 * lv, op=kc))
        # ---- le lâcher : les ailes se rabattent, la poussière fuse sous ses serres, un souffle part derrière elle
        tr = tl - SREL
        if 0 <= tr <= 360:
            k = env(tr, 0, 30, 120, 360)
            g = ctx['grip']
            if tr < 170:
                kk = env(tr, 0, 25, 60, 170)
                front.append(crescent(fig, (g[0] + 2 + 6 * (tr / 170), g[1] + 0.5), 5 + 4 * tr / 170, 10 + 4 * tr / 170, -70, 70, 3.4 * kk, op=kk))
            for j, (dx, r0) in enumerate(((-30, 4.6), (26, 4.0), (-42, 3.4))):
                out = dust(fig, feet[0] + dx * (1 + 0.5 * tr / 360), GR - 2.4, r0 * (0.6 + 0.6 * tr / 360), op=k)
                (back if j != 1 else front).append(out)
            pts = [(feet[0] - 44 + 12 * math.cos(math.radians(a)), GR - 44 + 24 * math.sin(math.radians(a))) for a in range(120, 245, 8)]
            back.append(stroke_fx(fig, pts, 2.6 * k, op=k))
        # ---- les trois flèches montent en se tressant, avec leurs traînées ; elles se resserrent là où l'aigle naît
        if P0_VOLLEY[0] is None:
            P0_VOLLEY[0] = (tip[0] + 1, tip[1])
        pts = volley_path(P0_VOLLEY[0])
        if SREL <= tl <= S_EAGLE + 60:
            s_head = ease((tl - SREL) / (S_EAGLE - SREL - 40)) * 1.0
            s_tail = max(0.0, s_head - 0.42)
            merge = ease((tl - (S_EAGLE - 110)) / 150)
            fade = 1 - ease((tl - S_EAGLE) / 60)
            for ph, kind in ARROWS3:
                def off(s):
                    a = 5.0 * min(1.0, s / 0.3) * (1 - merge)
                    ang = 2 * math.pi * 1.6 * s + ph
                    return a * math.sin(ang), math.cos(ang)
                tr_f, tr_b = [], []
                run_pts = []
                for i in range(25):
                    s = s_tail + (s_head - s_tail) * i / 24
                    p, d = path_at(pts, s)
                    nn = (d[1], -d[0])
                    o, z = off(s)
                    run_pts.append(((p[0] + o * nn[0], p[1] + o * nn[1]), z))
                # la traînée : devant ou derrière selon la spirale (par morceaux)
                seg, side = [], None
                for q, z in run_pts[:-2]:
                    sd = z > 0
                    if side is None or sd == side:
                        seg.append(q)
                    else:
                        (front if side else back).append(stroke_fx(fig, seg, 2.6, op=fade, pale=not side))
                        seg = [seg[-1], q]
                    side = sd
                if len(seg) >= 3:
                    (front if side else back).append(stroke_fx(fig, seg, 2.6, op=fade, pale=not side))
                hp, hd = path_at(pts, s_head)
                o, z = off(s_head)
                nn = (hd[1], -hd[0])
                hp = (hp[0] + o * nn[0], hp[1] + o * nn[1])
                ang = math.degrees(math.atan2(hd[1], hd[0]))
                Lr = 40.0
                tail_ = (hp[0] - hd[0] * Lr, hp[1] - hd[1] * Lr)
                (front if z > 0 else back).append(arrow_fx(fig, tail_, ang, kind, op=fade, L=Lr))
        # ---- l'aigle de vent naît là-haut, ouvre les ailes et crie (deux croissants devant le bec ouvert)
        if S_EAGLE - 60 <= tl <= S_DIVE + 20:
            grow = ease((tl - (S_EAGLE - 60)) / 140)
            op = min(1.0, (tl - (S_EAGLE - 60)) / 60)
            open_ = ease((tl - S_EAGLE) / 180)
            bob = 1.2 * math.sin((tl - S_EAGLE) / 90)
            b_, f_ = eagle(fig, (APEX[0], APEX[1] + bob), -14, 1.05 * (0.6 + 0.4 * grow), 'cri', op=op, open_=open_)
            front.append(b_ + f_)
            if grow > 0.2:
                front.append(flash(fig, APEX, 14 * (1 - open_) + 4, op=(1 - open_) * 0.8))
            kc = env(tl, S_EAGLE + 120, S_EAGLE + 180, S_DIVE - 120, S_DIVE - 20)
            if kc > 0:
                bk = (APEX[0] + 29 * math.cos(math.radians(-14)) + 8 * math.sin(math.radians(-14)), APEX[1] + 29 * math.sin(math.radians(-14)) - 9 * math.cos(math.radians(14)))
                cyc = ((tl - (S_EAGLE + 120)) % 160) / 160
                for i, r in enumerate((6 + 6 * cyc, 13 + 6 * cyc)):
                    front.append(crescent(fig, bk, r, r * 1.2, -60, 60, (4.0 - 0.8 * i) * (1 - 0.5 * cyc), op=kc * (1 - 0.6 * cyc), tilt=-14))
        # ---- le piqué, serres en avant : deux rubans courbes de l'apex à l'aigle
        if S_DIVE <= tl <= S_HIT + 10:
            u = ease((tl - S_DIVE) / (S_HIT - S_DIVE))
            u = u * u
            Cs = (APEX[0] + 6, APEX[1] + 6)
            Ce = (IMPACT[0] - 14, IMPACT[1] - 16)
            path = bez(Cs, (Cs[0] + 26, Cs[1] - 4), (Ce[0] - 12, Ce[1] - 34), Ce, 60)
            C = path[int(u * 60)]
            rot = -14 + (58 - -14) * min(1, u * 2.2)
            # la trace du piqué : deux rubans courbes qui suivent sa course et finissent derrière lui
            i1 = int(u * 60)
            i0 = max(0, i1 - 30)
            if i1 - i0 >= 4:
                seg = path[i0:i1 + 1]
                for dx, w in ((-4.0, 3.0), (4.0, 2.2)):
                    pts_ = []
                    for j, q in enumerate(seg):
                        a_ = seg[min(len(seg) - 1, j + 1)]
                        b_ = seg[max(0, j - 1)]
                        d = norm((a_[0] - b_[0], a_[1] - b_[1]))
                        pts_.append((q[0] - d[1] * dx, q[1] + d[0] * dx))
                    back.append(stroke_fx(fig, resample(pts_, 16), w, op=1))
            b_, f_ = eagle(fig, C, rot, 1.1, 'pique')
            front.append(b_ + f_)
        # ---- l'impact : arrêt sur l'image (l'aigle frappe), puis il éclate : ses ailes s'ouvrent en deux grands
        # croissants au ras du sol qui s'enroulent en volutes, une onde d'air court sur le sol, plumes et poussière
        th = tl - S_HIT
        X, Y = IMPACT
        if 0 <= th < 120:
            back.append(flash(fig, (X + 2, Y - 2), 16, op=1))
            b_, f_ = eagle(fig, (X - 14, Y - 16), 58, 1.1, 'pique')
            front.append(b_ + f_)
            back.append(dust(fig, X - 20, GR - 3, 5.0))
            front.append(dust(fig, X + 20, GR - 3, 4.5))
        if 120 <= th <= 760:
            k = (th - 120) / 640
            op = 1 - ease((k - 0.55) / 0.45)
            if k < 0.3:
                back.append(flash(fig, (X, Y - 5), 18 * (1 - k), op=1 - k / 0.3))
            r = 20 + 22 * ease(k * 1.4)
            back.append(crescent(fig, (X, GR - 2), 18 + 34 * ease(k), 3 + 3 * ease(k), 0, 360, 2.6 * (1 - k) + 0.4, op=op, head=0.5))
            front.append(crescent(fig, (X, Y - 2 - 10 * k), r, 12 + 10 * k, 180, 100, 4.4 * (1 - 0.6 * k), op=op, head=0.35))
            front.append(crescent(fig, (X, Y - 2 - 10 * k), r, 12 + 10 * k, 0, 80, 4.4 * (1 - 0.6 * k), op=op, head=0.35))
            front.append(curl(fig, (X - r + 5, Y - 9 - 14 * k), 5.5 - 2 * k, 170, 0.85, 2.8 * (1 - 0.5 * k), cw=True, op=op))
            front.append(curl(fig, (X + r - 5, Y - 9 - 14 * k), 5.5 - 2 * k, 10, 0.85, 2.8 * (1 - 0.5 * k), cw=False, op=op))
            rr = 7 + 3 * math.sin(math.pi * min(1, k * 1.3))
            back.append(dust(fig, X - 20 - 14 * k, GR - rr * 0.5, rr * 0.8, op=op))
            front.append(dust(fig, X + 20 + 14 * k, GR - rr * 0.5, rr * 0.7, op=op))
        if 120 <= th <= 1100:
            t = (th - 120) / 1000 * 4.4
            for i, (vx, vy, kind, sd) in enumerate(FEATHERS):
                x = X - 3 + vx * t * 2.8 + 2 * math.sin(t * 1.7 + i)
                y = Y - 10 + vy * t * 4 + 2.4 * t * t * 2.2
                y = min(y, GR - 2.5)
                op = 1 - ease((th - 800) / 300)
                (front if i % 2 else back).append(feather_fx(fig, x, y, 20 * math.sin(t * 2 + i) + 90 * (i % 2) - 30, kind, 0.9, op=op))
        # ---- elle réencoche : la volute dépose une nouvelle flèche
        new_arrow(fig, ctx, tl - (S_HIT + 420))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous l'héroïne."""
    x0, y0, vw, vh = view
    k = w / vw
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    fy = int((floor_y - y0) * k)
    for y in range(h):
        if y < fy:
            t = y / max(1, fy)
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            tt = (y - fy) / max(1, h - fy)
            c = tuple(int(a + (b - a) * tt) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, fy - 1, w, fy + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 40 * k, fy - 3.0 * k, cx + 40 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0 * k)))
    # l'ennemi : seulement une marque discrète au sol (là où vise la flèche)
    sh = Image.new('RGBA', (w, h))
    cx = (FOE[0] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 14 * k, fy - 1.6 * k, cx + 14 * k, fy + 1.6 * k], fill=(10, 4, 24, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5 * k)))
    return im


def timeline():
    """La suite : repos ×2, tir ×2, spéciale ×1 (en secondes)."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T * 0.6), ('attack', A), ('idle', IDLE_T * 0.8),
           ('special', S), ('idle', IDLE_T)]
    out, T_ = [], 0.0
    for a, d in seq:
        out.append((a, T_, T_ + d))
        T_ += d
    return out, T_


def frame_svg(T_, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T_ < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P, tl = pose_at(T_, act, t0)
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return T.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        i = sys.argv.index('--planche')
        moments = sys.argv[i + 1].split(',') if len(sys.argv) > i + 1 else None
        if moments is None:
            moments = [1.2, a_s + 0.3, a_s + 0.42, a_s + 0.48, a_s + 0.56, a_s + 0.75, a_s + 0.82, a_s + 0.95,
                       s_s + 0.45, s_s + 0.74, s_s + 0.85, s_s + 1.1, s_s + 1.3, s_s + 1.5, s_s + 1.64, s_s + 1.9]
        else:
            moments = [{'a': a_s, 's': s_s}.get(m[0], 0) + float(m.lstrip('as')) for m in moments]
        pngs = render([frame_svg(T_, segs) for T_ in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.environ.get('PLANCHE_OUT', TMP), 'planche.png')
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
