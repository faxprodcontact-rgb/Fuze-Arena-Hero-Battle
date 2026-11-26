# Corvin vectoriel ANIMÉ (refonte des héros du 26/11/2026, même méthode que Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/corvin/build.py) — garde vigilante, attaque de base
# « Bouclier et dague », attaque spéciale « Rempart des feuilles » — dans le style lisse de l'interface, à 24 i/s.
#
#   python3 refonte-graphique/ui-moderne/heros/corvin/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/corvin/
#   python3 refonte-graphique/ui-moderne/heros/corvin/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (corvin.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et
# se penche depuis les hanches, les jambes plient (pieds au sol), la tête, l'oreille, la frange et la cape suivent avec
# retard ; le bouclier suit le bras lointain (il pousse, s'ouvre, se lève, se plante) ; le bras proche est placé par
# cinématique inverse depuis le poing, qui tient la dague (le coude tourne autour de sa vraie jointure). Les poses clés
# reprennent celles du pixel art (mêmes gestes, mêmes temps : il se ramasse, pousse le bouclier, choc tenu, estocade
# par-dessus le bord, impact tenu, retour ; pour la spéciale : bouclier levé, feuille qui s'illumine, bouclier planté,
# dôme de vent, anneau qui s'étend au sol tout autour, défi la dague pointée), reliées par des courbes douces sans
# dépassement. Les effets du vent (croissant, éclat, filets de vitesse, tourbillon de feuilles, anneau au sol, dôme,
# volutes) ont les couleurs d'Eldra (même élément) ; feuilles de la forêt et feuilles d'or ; lueur rouge et marque
# de la provocation comme Zaroth : dégradés, un seul contour, aucun flou SVG, jamais de rayons répétés.
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import corvin as K  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'corvin')
TMP = os.environ.get('CORVIN_TMP') or tempfile.mkdtemp(prefix='corvin-anim-')
FPS = 24
VIEW = (-42, -14, 240, 135)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']
WINK = '#123c4a'                     # le contour des effets de vent (sarcelle très sombre)
DUST = ['#fff2d8', '#ecd2a6', '#c8a47c', '#8e6a5e']
DINK = '#4a3044'
RED = ['#ffd6d0', '#ff8a7a', '#f0404a', '#b01838', '#5e0a2a']
CX = 64.0                            # le milieu de Corvin au sol

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


NUM = ['crouch', 'lean', 'tilt', 'ear', 'fr', 'cape', 'sx', 'sy', 'srot', 'glow', 'gx', 'gy', 'da', 'wa', 'stretch', 'red',
       'headx', 'heady']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, ear=0, fr=0, cape=0, sx=0, sy=0, srot=0, glow=0, gx=K.G0[0], gy=K.G0[1], da=K.DA0,
             wa=K.WA0, stretch=0, red=0, headx=0, heady=0)
    for key, v in k.items():
        if key == 'g':
            d['gx'], d['gy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'sh':
            d['sx'], d['sy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, comme le pixel art)
# 2) L'attaque de base « Bouclier et dague » : il se ramasse derrière le bouclier (dague ramenée, l'oreille dressée,
# tenu), pousse le bouclier d'un coup (un croissant de vent roule devant), choc tenu (éclat de vent, feuilles
# projetées) ; le bouclier s'ouvre sur le côté et l'estocade part par-dessus son bord (lame étirée par la vitesse,
# filets de vent), impact tenu (un tourbillon de feuilles s'enroule autour de la pointe), il ramène la dague et revient
# en garde ; les feuilles retombent.
ATTACK = [
    (0, {}),
    (80, {}),
    (280, dict(crouch=1.2, lean=-2, sh=(-2, 0.5), g=(47.2, 82.8), da=-32, wa=-98, head=(-1, 0.8), tilt=-2, ear=1, fr=1, cape=1)),
    (330, dict(crouch=1.3, lean=-2.2, sh=(-2.2, 0.6), g=(47.0, 82.6), da=-33, wa=-98, head=(-1.1, 0.9), tilt=-2.2, ear=1, fr=1, cape=1)),
    (390, dict(crouch=1.6, lean=3, sh=(7, -1), g=(48.6, 83.0), da=-26, head=(1, 0), tilt=1.5, ear=0, fr=1, cape=-1)),
    (420, dict(crouch=2, lean=4, sh=(9, -1), srot=2, head=(1.2, 0.2), tilt=2, fr=0.5, cape=-1)),
    (520, dict(crouch=2, lean=4.2, sh=(9.2, -1), srot=2, head=(1.2, 0.3), tilt=2, fr=0, cape=-0.8)),
    (570, dict(crouch=2, lean=4.5, sh=(4, 0.6), srot=-2, g=(74, 61.6), da=-4, wa=-150, stretch=6, head=(1.2, 0.2), tilt=1.5, fr=1,
               cape=-1)),
    (610, dict(crouch=2.2, lean=5, sh=(2.6, 1.2), srot=-3, g=(78, 61.8), da=-3, wa=-160, stretch=1.0, head=(1.3, 0.3), tilt=2, fr=1,
               cape=-1)),
    (780, dict(crouch=2.2, lean=5, sh=(2.6, 1.2), srot=-3, g=(77.6, 62.0), da=-3, wa=-160, stretch=0.6, head=(1.3, 0.3), tilt=2, fr=0,
               cape=0)),
    (880, dict(crouch=1.2, lean=2, sh=(3, 0), srot=1, g=(58, 73), da=-14, wa=-125, cape=1, fr=-0.5)),
    (1000, dict(crouch=0.5, sh=(0.6, 0), g=(50.4, 83.2), da=-21, wa=-103, cape=0.5)),
    (1150, {}),
]
ATTACK_BASH = 420                     # le choc du bouclier
ATTACK_HIT = 610                      # la pointe touche

# 3) L'attaque spéciale « Rempart des feuilles » (sort d'équipe : bouclier sur toute l'équipe, puis provocation) : il
# se ramasse et lève le bouclier, la feuille d'or s'illumine ; le vent se lève en anneau à ses pieds et un tourbillon
# de rubans et de feuilles monte autour de lui ; il PLANTE le bouclier : le tourbillon se referme en dôme translucide
# (arrêt sur l'image) ; le dôme s'abaisse en un anneau posé au sol qui s'étend TOUT AUTOUR de lui et se défait en
# volutes, les feuilles retombent en cercle ; il arrache le bouclier et pointe sa dague vers l'ennemi : la lueur rouge
# de la provocation pulse sur lui et la marque bat au-dessus de sa capuche ; il revient en garde.
PLANT = dict(crouch=3, lean=2, sh=(6, 8), glow=3, head=(1, 0), tilt=1)
DEFI = dict(crouch=1, lean=2, sh=(6, 4), g=(68, 62), da=-14, wa=-150, head=(1, -1), tilt=1, ear=1, fr=1, cape=-1)
SPECIAL = [
    (0, {}),
    (100, {}),
    (220, dict(crouch=1, lean=-1, sh=(0, -3), glow=1, head=(0, 1), ear=1, fr=1, cape=1, g=(48.6, 83.4), da=-26)),
    (360, dict(crouch=2, lean=-1, sh=(1, -6), glow=2, head=(0, 1), ear=1, fr=1, cape=1, g=(48.4, 83.2), da=-27)),
    (520, dict(crouch=2, lean=-1.2, sh=(1, -7), glow=3, head=(0, 1.1), ear=0.4, fr=0, cape=0, g=(48.4, 83.0), da=-27)),
    (580, dict(PLANT, cape=-1)),
    (800, dict(PLANT, cape=-0.6, fr=1)),
    (880, dict(PLANT, cape=0.4, fr=0.5)),
    (1220, dict(PLANT, glow=1, cape=1, fr=0)),
    (1320, dict(crouch=2, lean=1, sh=(4, 4), glow=1, head=(0, 1), ear=1, cape=0)),
    (1420, dict(DEFI, red=1)),
    (1760, dict(DEFI, red=0.5, fr=0, ear=0.5)),
    (1880, dict(crouch=1, lean=1, sh=(1, 0), g=(58, 73), da=-14, wa=-125, cape=1, red=0)),
    (2000, dict(crouch=0.4, g=(50.4, 83.2), da=-21, wa=-103, cape=0.4)),
    (2150, {}),
]
SP_RISE = 100                         # le vent se lève
SP_PLANT = 580                        # le bouclier planté : le dôme se referme
SP_RING = 880                         # LANCEMENT : le dôme s'abaisse en anneau au sol
SP_DEFI = 1420                        # la provocation

# ======================================================================== la garde (en boucle, 2 s)


def idle_offsets(T):
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    tw = 4.0
    ear = 0.6 * math.sin(u - 1.4)
    ph = T % tw
    if 2.3 <= ph < 2.7:                                   # l'oreille frémit (il écoute)
        ear += 1.2 * math.sin(math.pi * (ph - 2.3) / 0.4) * math.sin((ph - 2.3) * 40)
    return dict(breath=br, crouch=0.35 * (0.5 - 0.5 * math.cos(u - 2.4)), heady=0.3 * math.sin(u - 1.9),
                tilt=0.5 * math.sin(u - 1.2), ear=ear, fr=0.8 * math.sin(u - 1.9), cape=0.9 * math.sin(u - 0.8),
                srot=0.4 * math.sin(u - 1.0), sy=0.25 * math.sin(u - 1.6))


def pose_at(T, action=None, t0=0.0):
    P = {}
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['breath'] = w * idl['breath']
    P['g'] = (P.pop('gx'), P.pop('gy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['sh'] = (P.pop('sx'), P.pop('sy'))
    P['blink'] = 1.0 if (w > 0.95 and 1.36 <= (T % 4.0) < 1.46) else 0.0
    return P


# ======================================================================== les effets du vent (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, ry or r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def stroke_shape(center, widths):
    """Un ruban fermé le long d'une ligne, largeur donnée en chaque point (bouts pointus)."""
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


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290):
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
    gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.35, WIND[2]), (0.7, WIND[1]), (1, WIND[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.1, op=op)


def ell_pts(C, rx, ry, a0, a1, n=28):
    return [(C[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def swirl(fig, C, rx, ry, a0, a1, w, op=1.0):
    """Un ruban de vent le long d'un arc d'ellipse (effilé aux deux bouts)."""
    if op <= 0.02 or w < 0.1:
        return ''
    pts = ell_pts(C, rx, ry, a0, a1, 24)
    ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.7) for i in range(25)]
    sh = stroke_shape(pts, ws)
    core = stroke_shape(pts, [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.8)], w=1.0, op=op)


def leaf(fig, x, y, a, s=1.6, op=1.0, gold=False):
    """Une feuille de la forêt (verte) ou une feuille d'or qui tourbillonne : bords bombés, pointe, nervure claire."""
    if op <= 0.02:
        return ''
    c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
    P = lambda px, py: (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(-1.5, 0), P(-0.4, -0.85), P(1.0, -0.55), P(1.7, 0), P(1.0, 0.55), P(-0.4, 0.85)], sharp=(0, 3), t=0.9)
    vein = ribbon([P(-1.6, 0), P(0, -0.04), P(1.4, 0)], [0.05, 0.2 * s, 0.05])
    if gold:
        gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, '#fff6c0'), (0.5, '#ffcc48'), (1, '#b86a1e')])
        ink, vc = '#4a2010', '#fff8dc'
    else:
        gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, '#d2f28a'), (0.5, '#5cb850'), (1, '#1f6048')])
        ink, vc = '#123a2e', '#e8ffd0'
    return outlined([(sh, gr, 1), (vein, vc, 0.75)], ink=ink, w=0.9, op=op)


def dust(fig, cx, cy, r, op=1.0, k=0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = [(0, 0, 1), (0.8, 0.3, 0.72), (-0.82, 0.28, 0.7), (0.2, -0.55, 0.62), (-0.35, -0.35, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in j[:4 + (k % 2)]]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def arc_band(C, R, a0, a1, w, taper=0.8, n=28, ry=None):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    k = (ry / R) if ry else 1.0
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * k * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * k * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté de l'ennemi."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.9 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper=0.0)
    out += outlined([(ring, WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


def mark(fig, c, s, op=1.0):
    """La marque de la provocation (signe inventé, le même que Zaroth) : un œil en amande rouge, pupille fendue."""
    x, y = c
    alm = sm([(x - 4.6 * s, y), (x - 1.6 * s, y - 2.6 * s), (x + 1.6 * s, y - 2.6 * s), (x + 4.6 * s, y), (x + 1.6 * s, y + 2.6 * s),
              (x - 1.6 * s, y + 2.6 * s)], sharp=(0, 3), t=0.9)
    iris = ellipse(x, y, 1.9 * s, 1.9 * s)
    pup = sm([(x, y - 1.7 * s), (x + 0.55 * s, y), (x, y + 1.7 * s), (x - 0.55 * s, y)], sharp=(0, 2), t=0.8)
    gr = g_lin(fig, (x + 3 * s, y - 3 * s), (x - 3 * s, y + 3 * s), [(0, RED[1]), (0.5, RED[2]), (1, RED[3])])
    return outlined([(alm, gr, 1), (iris, g_rad(fig, (x + 0.5 * s, y - 0.5 * s), 2.4 * s, [(0, RED[0]), (0.6, RED[1]), (1, RED[2])]), 1),
                     (pup, RED[4], 1), (ellipse(x + 0.8 * s, y - 0.9 * s, 0.4 * s, 0.32 * s), '#ffffff', 1)], ink='#3a0818', w=1.2, op=op)


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


def leaf_glow(fig, ctx, g):
    """La feuille d'or du bouclier qui s'illumine : un halo doré (dégradé radial) par-dessus."""
    if g <= 0.02:
        return
    c = ctx['leaf']
    r = 7 + 4 * g
    fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(r * 1.35), g_rad(
        fig, c, r, [(0, '#fffde8', min(0.85, 0.3 * g)), (0.4, '#ffe680', min(0.5, 0.17 * g)), (1, '#ffcc48', 0)], ry=r * 1.35)))


def falling_leaves(fig, t, seed, n, C, R, h0, dur, front_only=False):
    """Des feuilles qui retombent en se balançant, en cercle autour de C (vert et or) ; t en ms depuis le départ."""
    for j in range(n):
        a = math.radians(j * 360 / n + seed * 37)
        rr = R * (0.75 + 0.25 * ((j * 0.618 + seed) % 1))
        x0 = C[0] + rr * math.cos(a)
        z = math.sin(a)                       # derrière (−) ou devant (+)
        if front_only and z < 0:
            continue
        k = t / dur
        if not (0 <= k <= 1):
            continue
        y = C[1] - h0 * (1 - k) * (0.6 + 0.4 * ((j * 0.37) % 1)) + 6 * z
        x = x0 + 3.2 * math.sin(k * 9 + j)
        op = env(t, 0, 80, dur * 0.75, dur)
        el = leaf(fig, x, y, 40 * math.sin(k * 8 + j) + j * 50, 1.25, op=op, gold=(j % 3 == 0))
        (fig.fx_front if z >= 0 else fig.fx_back).append(el)


# ---- l'attaque de base

HIT = {}


def fx_attack(tl):
    def f(fig, ctx):
        L = ctx['shield_L']
        SHM = ctx['SHM']
        from atelier import mapp
        front = mapp(SHM, L(16.4, -2.0))                  # le devant du bouclier (son bord droit)
        # la poussée : un croissant de vent roule devant le bouclier
        e = env(tl, 330, 380, 420, 480)
        if e > 0:
            C = mapp(SHM, K.SC0)
            k = smooth((tl - 330) / 150)
            fig.fx_front.append(outlined([(arc_band((C[0] + 4 + 8 * k, C[1]), 22, -58, 58, 3.4 * e, taper=0.0), g_lin(
                fig, (C[0] + 20, C[1] - 20), (C[0] + 20, C[1] + 20), [(0, WIND[2]), (0.5, WIND[0]), (1, WIND[2])]), 1)], w=1.0, op=e))
        # le choc : l'éclat de vent sur le bord du bouclier, deux feuilles projetées
        if tl >= ATTACK_BASH:
            if 'front' not in HIT:
                HIT['front'] = front
            fr_ = HIT['front']
            tau = tl - ATTACK_BASH
            if tau < 240:
                k = tau / 240
                fig.fx_front.append(pop(fig, (fr_[0] + 4 + 4 * k, fr_[1]), 4.4 + 3.4 * k, facing=0, op=1 - k ** 1.6))
            for j, (vx, vy) in enumerate(((70, -60), (90, -15), (60, 30))):
                tt = tau / 1000
                if tt < 0.6:
                    x, y = ballistic((fr_[0] + 4, fr_[1]), (vx, vy), 90, tt)
                    fig.fx_front.append(leaf(fig, x, y, tt * 700 + j * 90, 1.3, op=env(tau, 0, 30, 380, 600), gold=(j == 1)))
        # l'estocade : deux filets de vent le long de la lame (la vitesse)
        u, tip = ctx['u'], ctx['tip']
        n = (u[1], -u[0])
        e = env(tl, 530, 560, 600, 680)
        if e > 0:
            for side in (1, -1):
                p0 = (tip[0] - 30 * u[0] + side * 2.6 * n[0], tip[1] - 30 * u[1] + side * 2.6 * n[1])
                p3 = (tip[0] + 2 * u[0] + side * 1.0 * n[0], tip[1] + 2 * u[1] + side * 1.0 * n[1])
                fig.fx_back.append(gust(fig, p0, (p0[0] + 12 * u[0] + side * 2 * n[0], p0[1] + 12 * u[1] + side * 2 * n[1]),
                                        (p3[0] - 10 * u[0] + side * 2 * n[0], p3[1] - 10 * u[1] + side * 2 * n[1]), p3, 2.0, curl=0,
                                        op=e, tail=0.5 * env(tl, 590, 680, 700, 701)))
        # l'impact : le tourbillon de feuilles s'enroule autour de la pointe, tourne plus large, s'ouvre en volutes
        if tl >= ATTACK_HIT:
            if 'tip' not in HIT:
                HIT['tip'] = tip
            T_ = HIT['tip']
            tau = tl - ATTACK_HIT
            if tau < 200:
                k = tau / 200
                fig.fx_front.append(pop(fig, (T_[0] + 2, T_[1]), 3.6 + 2.6 * k, facing=0, op=1 - k ** 1.5))
            o = env(tau, 0, 60, 300, 520)
            if o > 0:
                C = (T_[0] + 3 + 4 * smooth(tau / 500), T_[1])
                rx, ry = 7 + 8 * smooth(tau / 500), 4.2 + 4 * smooth(tau / 500)
                rot = tau * 0.9
                fig.fx_back.append(swirl(fig, C, rx, ry, 190 + rot, 350 + rot, 2.2 * o, op=o))
                fig.fx_front.append(swirl(fig, C, rx, ry, 10 + rot, 170 + rot, 2.6 * o, op=o))
                if tau > 260:
                    kk = smooth((tau - 260) / 260)
                    fig.fx_front.append(gust(fig, (C[0] + rx * 0.6, C[1] - ry), (C[0] + rx + 4, C[1] - ry - 3 * kk),
                                             (C[0] + rx + 8, C[1] - ry - 4 - 2 * kk), (C[0] + rx + 11 + 4 * kk, C[1] - ry - 5 - 3 * kk),
                                             1.8, curl=2.4 + kk, s=-1, op=o, tail=0.5 * kk))
            # les feuilles : sur le cercle du tourbillon, puis elles s'écartent et retombent en se balançant
            for j in range(5):
                a = math.radians(j * 72 + tau * 0.9)
                if tau < 420:
                    rr = 6 + 9 * smooth(tau / 420)
                    x = T_[0] + 4 + rr * math.cos(a)
                    y = T_[1] + rr * 0.6 * math.sin(a)
                    op = env(tau, 0, 60, 2000, 2001)
                else:
                    tt = (tau - 420) / 1000
                    a0 = math.radians(j * 72 + 420 * 0.9)
                    x = T_[0] + 4 + 15 * math.cos(a0) + 12 * tt + 3 * math.sin(tt * 10 + j)
                    y = T_[1] + 9 * math.sin(a0) + 30 * tt + 30 * tt * tt
                    op = max(0.0, 1 - tt / 0.5)
                el = leaf(fig, x, y, tau * 0.8 + j * 70, 1.2, op=op, gold=(j % 2 == 0))
                (fig.fx_front if math.sin(a) >= 0 or tau >= 420 else fig.fx_back).append(el)
    return f


# ---- l'attaque spéciale

DOME_RX, DOME_H = 50.0, 104.0


def dome_path(C, rx, h):
    """Le dôme : une demi-ellipse posée au sol (contour fermé par le bas)."""
    pts = [(C[0] + rx * math.cos(math.radians(a)), C[1] - h * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    pts += [(C[0] - rx * math.cos(math.radians(a)), C[1] + 0.16 * rx * math.sin(math.radians(a))) for a in range(6, 175, 12)]
    return sm(pts, sharp=(0, 30), t=0.8)


def dome(fig, C, rx, h, op, t):
    """Le dôme de vent translucide : un voile jade derrière lui (bord plus clair en haut à droite), un voile très
    léger devant, le bord lumineux (UN contour, ouvert sur le sol), des rubans qui tournent à sa surface."""
    if op <= 0.02:
        return
    sh = dome_path(C, rx, h)
    fig.fx_back.append('<path d="%s" fill="%s"/>' % (sh.d(), g_rad(fig, (C[0] + rx * 0.35, C[1] - h * 0.75), rx * 1.25, [
        (0, WIND[1], 0.42 * op), (0.55, WIND[3], 0.26 * op), (1, WIND[4], 0.34 * op)], ry=h * 1.2)))
    fig.fx_front.append('<path d="%s" fill="%s"/>' % (sh.d(), g_rad(fig, (C[0] + rx * 0.35, C[1] - h * 0.75), rx * 1.25, [
        (0, WIND[0], 0.22 * op), (0.6, WIND[2], 0.08 * op), (1, WIND[3], 0.16 * op)], ry=h * 1.2)))
    # le bord : une bande plus épaisse en haut à droite (là où la lumière frappe la bulle)
    pts = [(C[0] + rx * math.cos(math.radians(a)), C[1] - h * math.sin(math.radians(a))) for a in range(0, 181, 5)]
    ws = [max(0.1, (0.9 + 1.6 * max(0, math.cos(math.radians(a - 50)))) * math.sin(math.radians(a)) ** 0.25) for a in range(0, 181, 5)]
    ws[0] = ws[-1] = 0.1
    rim = stroke_shape(pts, ws)
    core = stroke_shape(pts, [w * 0.45 for w in ws])
    fig.fx_front.append(outlined([(rim, g_lin(fig, pts[-1], pts[0], [(0, WIND[3]), (0.6, WIND[1]), (1, WIND[2])]), 1),
                                  (core, WIND[0], 0.9)], w=1.0, op=op))
    # deux rubans qui tournent à la surface du dôme (une bande de l'ellipse, devant et derrière)
    for j, (yk, sp) in enumerate(((0.38, 1.0), (0.68, -0.8))):
        yy = C[1] - h * yk
        rr = rx * math.sqrt(max(0.0, 1 - yk * yk))
        a = (t * 0.5 * sp + j * 90) % 360
        fig.fx_front.append(swirl(fig, (C[0], yy), rr, rr * 0.18, a, a + 140, 2.2, op=op * 0.9))
        fig.fx_back.append(swirl(fig, (C[0], yy), rr, rr * 0.18, a + 180, a + 300, 1.6, op=op * 0.6))


def ring(fig, C, rx, w, op, gap=0.0, curls=0.0):
    """L'anneau de vent posé au sol (une ellipse aplatie), devant et derrière lui ; il se défait en arcs (gap) et en
    volutes (curls)."""
    if op <= 0.02:
        return
    ry = rx * 0.16
    for a0 in (0, 90, 180, 270):
        g = gap * 40
        a1, a2 = a0 + g / 2, a0 + 90 - g / 2
        if a2 - a1 < 6:
            continue
        mid = (a1 + a2) / 2
        dst = fig.fx_front if math.sin(math.radians(mid)) > 0 else fig.fx_back
        dst.append(swirl(fig, C, rx, ry, a1, a2, w, op=op))
        if curls > 0.05:
            p = (C[0] + rx * math.cos(math.radians(a2)), C[1] + ry * math.sin(math.radians(a2)))
            d = (-math.sin(math.radians(a2)) * rx, math.cos(math.radians(a2)) * ry)
            q = (p[0] + d[0] * 0.12, p[1] + d[1] * 0.12)
            dst.append(gust(fig, p, lerp2(p, q, 0.4), lerp2(p, q, 0.8), q, w * 0.8, curl=2.0 + 1.5 * curls,
                            s=1 if math.cos(math.radians(a2)) > 0 else -1, op=op * curls))


def lerp2(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        P = ctx['P']
        C = (CX + 2, GR)
        leaf_glow(fig, ctx, P['glow'])
        # 1) le vent se lève : un anneau au ras du sol autour de ses pieds, des rubans qui montent en spirale avec des
        # feuilles (le tourbillon), jusqu'au-dessus de sa capuche
        g = env(t, SP_RISE, 260, SP_PLANT - 20, SP_PLANT + 40)
        if g > 0:
            rot = t * 0.7
            fig.fx_back.append(swirl(fig, (C[0], C[1] - 1.5), 34, 6, 190 + rot % 60, 340 + rot % 60, 2.6 * g, op=g))
            fig.fx_front.append(swirl(fig, (C[0], C[1] - 1.5), 34, 6, 10 + rot % 60, 165 + rot % 60, 3.2 * g, op=g))
            up = smooth((t - SP_RISE) / (SP_PLANT - SP_RISE))
            for j in range(3):
                # trois rubans : aux genoux, à la taille, et au-dessus de la capuche (jamais devant le visage)
                yy = (C[1] - 10 - 6 * up, C[1] - 38 - 8 * up, C[1] - 96 - 14 * up)[j]
                if j == 2 and up < 0.25:
                    continue
                rr = (36, 34, 22)[j]
                a = (rot * (1.2 + 0.2 * j) + j * 120) % 360
                o = g * env(t, SP_RISE + 60 * j, SP_RISE + 60 * j + 140, 2000, 2001)
                if j == 2:
                    o *= smooth((up - 0.25) / 0.25)
                fig.fx_front.append(swirl(fig, (C[0], yy), rr, rr * 0.2, a, a + 150, 2.6, op=o))
                fig.fx_back.append(swirl(fig, (C[0], yy), rr, rr * 0.2, a + 180, a + 310, 2.0, op=o * 0.8))
            for j in range(9):
                k = ((t - SP_RISE) / 900 * (0.8 + 0.1 * (j % 3)) + j / 9) % 1
                a = math.radians(j * 40 + t * 0.6)
                rr = 30 + 6 * (j % 3)
                x = C[0] + rr * math.cos(a)
                y = C[1] - 4 - 100 * k * up + 0.2 * rr * math.sin(a)
                el = leaf(fig, x, y, t * 0.5 + j * 50, 1.25, op=g * min(1, 3 * (1 - k)), gold=(j % 3 == 0))
                (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(el)
        # 2) il plante le bouclier : poussière sous la pointe, le tourbillon se referme en dôme (éclat en haut)
        tau = t - SP_PLANT
        if 0 <= tau < 420:
            L = ctx['shield_L']
            from atelier import mapp
            tipw = mapp(ctx['SHM'], L(0, 26.4))
            for j, (dx, r) in enumerate(((-6, 2.6), (5, 3.0), (-1, 2.2), (9, 1.8))):
                k = tau / 420
                fig.fx_front.append(dust(fig, tipw[0] + dx * (0.5 + k), GR - 1.5 - 3 * k - (j % 2), r * (0.6 + 0.6 * k), op=1 - k, k=j))
        d_op = env(t, SP_PLANT - 30, SP_PLANT + 50, SP_RING, SP_RING + 120)
        if d_op > 0:
            grow = 0.85 + 0.15 * smooth((t - SP_PLANT + 30) / 120)
            low = smooth((t - SP_RING) / 140)          # le dôme s'abaisse
            dome(fig, C, DOME_RX * grow * (1 + 0.2 * low), DOME_H * grow * (1 - 0.9 * low), d_op, t)
            fl = env(t, SP_PLANT, SP_PLANT + 40, SP_PLANT + 120, SP_PLANT + 260)
            if fl > 0:                                   # l'éclat en haut du dôme
                top = (C[0] + 14, C[1] - DOME_H * 0.93)
                fig.fx_front.append(pop(fig, top, 5 + 3 * fl, facing=-60, op=fl))
            # des feuilles prises dans le dôme
            for j in range(7):
                a = math.radians(j * 51 + t * 0.25)
                yk = 0.2 + 0.1 * (j % 5)
                rr = DOME_RX * grow * math.sqrt(1 - yk * yk) * 0.96
                x = C[0] + rr * math.cos(a)
                y = C[1] - DOME_H * grow * (1 - 0.9 * low) * yk + 0.18 * rr * math.sin(a)
                el = leaf(fig, x, y, t * 0.4 + j * 60, 1.2, op=d_op * (1 - low), gold=(j % 3 == 1))
                (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(el)
        # 3) LANCEMENT : l'anneau posé au sol s'étend TOUT AUTOUR de lui, se défait en arcs et en volutes
        tau = t - SP_RING
        if 0 <= tau < 560:
            k = smooth(tau / 560)
            ring(fig, (C[0], C[1] + 1), DOME_RX * 1.2 + 70 * k, 3.4 * (1 - 0.6 * k), op=1 - k ** 2, gap=k, curls=k)
        if 0 <= tau < 900:
            falling_leaves(fig, tau, 1, 10, (C[0], C[1] - 1), 40 + 30 * smooth(tau / 900), 70, 900)
        # 4) le défi : une lueur rouge douce qui gonfle puis s'éteint, un liseré rouge sur lui, la marque qui bat
        dv = env(t, SP_DEFI - 60, SP_DEFI + 40, SP_DEFI + 300, 1840)
        if dv > 0:
            ch = ctx['chest']
            pulse = 0.5 + 0.5 * math.sin((t - SP_DEFI) / 1000.0 * 2 * math.pi * 3.0)
            fig.under.append((ch[0], ch[1] - 6, 40 + 6 * pulse, 56 + 6 * pulse, RED[2], (0.24 + 0.16 * pulse) * dv, None))
            fig.aura = (RED[1], 1.0 + 0.8 * pulse, 0.75 * dv)
            c = ctx['hood_top']
            fig.over.append(mark(fig, (c[0] + 4, c[1] - 9), (1.15 + 0.2 * pulse) * (0.6 + 0.4 * dv), op=dv))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous lui."""
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
    cx = (CX + 2 - x0) * k
    sd.ellipse([cx - 36 * k, fy - 3.0 * k, cx + 36 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


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
        if act == 'attack':
            if tl < ATTACK_BASH:
                HIT.clear()
            fx = [fx_attack(tl)]
        else:
            fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
    os.makedirs(TMP, exist_ok=True)
    segs, total = timeline()
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        moments = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]] or \
            [1.0, a_s + 0.30, a_s + 0.43, a_s + 0.57, a_s + 0.62, a_s + 0.75, a_s + 0.9, a_s + 1.05,
             s_s + 0.30, s_s + 0.50, s_s + 0.62, s_s + 0.75, s_s + 0.95, s_s + 1.15, s_s + 1.50, s_s + 1.70]
        # l'état des effets (HIT) dépend des images précédentes : on rejoue l'attaque depuis son début
        svgs = []
        for T in moments:
            HIT.clear()
            for a, s, e in segs:
                if s <= T < e and a == 'attack':
                    for i in range(int((T - s) * FPS)):
                        frame_svg(s + i / FPS, segs)
            svgs.append(frame_svg(T, segs))
        pngs = render(svgs, 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, 'planche.png')
        sheet_.save(out)
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
    for width, colors in ((400, 128), (380, 96), (360, 80)):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                        '-vf', 'fps=12,scale=%d:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=%d:stats_mode=diff[p];'
                        '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle' % (width, colors), gifp], check=True)
        if os.path.getsize(gifp) <= 3 * 1024 * 1024:
            break
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
