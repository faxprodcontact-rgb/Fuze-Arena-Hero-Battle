# Zaroth vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026, sur le modèle de Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/zaroth/build.py) — respiration lourde, attaque de base
# (la coupe en diagonale : il lève le sabre à côté du masque, TIENT, puis une seule coupe d'un éclair ; un fin croissant
# d'eau se détache, file vers l'ennemi et le fend ; il secoue la lame et revient en garde), attaque spéciale « Rempart
# des marées » (il plante le sabre, l'eau jaillit et monte en spirale en un dôme autour de lui, le dôme s'abaisse en un
# anneau d'eau qui s'éloigne tout autour, l'eau qui reste scintille sur son armure, un peu d'eau claire le soigne, puis
# il arrache le sabre et le pointe vers l'ennemi en défi : lueur rouge qui pulse, marque en amande au-dessus du casque).
#
#   python3 refonte-graphique/ui-moderne/heros/zaroth/anim.py            # → anim.gif + anim.mp4 dans pixel/sortie/ui/vecto/zaroth/
#   python3 refonte-graphique/ui-moderne/heros/zaroth/anim.py --planche [a0.3,s1.2,…]   # planche d'images clés (contrôle)
#
# Méthode (celle de Kael) : le dessin (zaroth.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui
# respire et se penche depuis les hanches, tête et plaques des épaulières qui suivent avec retard, jupe de plaques qui se
# balance ; le sabre est placé par sa garde et son angle, les deux bras le suivent par cinématique inverse, le haut des
# bras caché sous les épaulières). Poses clés reprises du pixel art (mêmes temps lourds : longue tenue, coup très court,
# retour sobre), reliées par des courbes douces sans dépassement, 24 images par seconde. Les effets d'eau (traînée,
# croissant, gerbes, gouttes, spirale, anneau, bulles) sont dessinés dans le même style : dégradés, un seul contour,
# aucun flou SVG, jamais de rayons droits répétés.
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
import zaroth as Z  # noqa: E402
from atelier import sm, ribbon, ellipse, lock, f as fm  # noqa: E402

ROOT = Z.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'zaroth')
TMP = os.path.join(HERE, '_images')
FPS = 24
VIEW = (-30, -38, 284, 160)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = Z.GRD
FOE = (222.0, 78.0)                  # l'ennemi (milieu du corps), là où frappe le croissant d'eau
W_ = Z.WATER                         # blanc, écume, cyan pâle, bleu clair, bleu, bleu profond
WINK = '#14325e'                     # le contour des effets d'eau
RED = ['#ffd6d0', '#ff8a7a', '#f0404a', '#b01838', '#5e0a2a']

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


PAIRS = ['O', 'head', 'shn', 'shf']
SCAL = ['crouch', 'lean', 'tilt', 'ang', 'lift', 'sn', 'sf', 'kz', 'stretch']
NUM = SCAL + [p + c for p in PAIRS for c in 'xy']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, ang=Z.ANG0, lift=0, sn=0, sf=0, kz=0, stretch=0, Ox=Z.O0[0], Oy=Z.O0[1],
             headx=0, heady=0, shnx=0, shny=0, shfx=0, shfy=0)
    for key, v in k.items():
        if key in PAIRS:
            d[key + 'x'], d[key + 'y'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# Angles de lame en degrés, y vers le bas (−90 : la lame monte tout droit ; 90 : elle pique vers le sol).
# 2) L'attaque de base : la coupe en diagonale (kesa-giri). Pixel : il se ramasse, lève le sabre tout droit à côté du
# masque (300 ms de tenue), coupe en 50 ms, arrêt net lame basse, chiburi, retour en garde.
RAISE = dict(O=(91.0, 55.0), ang=-97, crouch=1, lean=-2, lift=1.4, head=(-0.8, 0), shn=(5, -2), sn=0.4, sf=0.3, kz=0.6)
CUT = dict(O=(92.0, 86.0), ang=26, crouch=2, lean=3, head=(0.8, 0.8), tilt=1.5, shn=(7, 3), shf=(-2, 1), sn=-0.6, sf=-0.4, kz=-1.4)
ATTACK = [
    (0, {}),
    (90, dict(crouch=1, kz=0.3)),
    (170, dict(O=(86.0, 62.0), ang=-84, crouch=1, lean=-1, lift=0.8, shn=(3, -1), sn=0.2, kz=0.6)),
    (290, RAISE),
    (470, dict(RAISE, O=(91.4, 54.4), ang=-99, lean=-2.3, head=(-1, 0))),
    (505, dict(O=(103.0, 65.0), ang=-24, crouch=2, lean=2, lift=0.3, shn=(7, 0), stretch=4, kz=-0.6)),
    (545, dict(CUT, stretch=2)),
    (580, dict(CUT, O=(92.0, 86.6), crouch=2.2, lean=3.3, sn=0.5, sf=0.4)),
    (900, dict(CUT, sn=0, sf=0, kz=-0.4)),
    (975, dict(O=(90.0, 84.0), ang=50, crouch=2, lean=2, head=(0.6, 0.6), shn=(6, 3), kz=0.6)),
    (1060, dict(O=(85.0, 78.0), ang=-22, crouch=1, lean=1, shn=(3, 1), kz=0.2)),
    (1190, dict(crouch=1)),
    (1380, {}),
]
A_CUT = (470, 560)          # la coupe (traînée)
A_MOON = 560                # le croissant d'eau se détache
A_HIT = 880                 # il fend l'ennemi
A_SHAKE = 975               # le chiburi

# 3) L'attaque spéciale « Rempart des marées » (sort d'équipe).
PLANT = dict(O=(90.0, 66.0), ang=90, crouch=1, lean=1, shn=(4, 0), shf=(-1, 0))
DEFI = dict(O=(96.0, 64.0), ang=-6, crouch=1, lean=2, head=(1, 0), shn=(7, 0), shf=(-1, 0))
SPECIAL = [
    (0, {}),
    (100, dict(crouch=1)),
    (240, dict(O=(91.0, 57.0), ang=84, crouch=0, lean=-1, lift=1.2, head=(0, -1), shn=(4, -2), sn=0.3, sf=0.3)),
    (280, dict(O=(91.0, 56.5), ang=85, crouch=0, lean=-1.2, lift=1.3, head=(0, -1.2), shn=(4, -2))),
    (330, dict(PLANT, crouch=2, head=(1, 1), sn=-0.6, sf=-0.5, kz=-1.0)),
    (450, dict(PLANT, crouch=2, head=(1, 1), sn=0.3, sf=0.2, kz=0.4)),
    (700, dict(PLANT, head=(0, -0.5), tilt=-1, lift=0.5)),
    (900, dict(PLANT, head=(0, -0.6), tilt=-1.2, lift=0.6)),
    (1000, dict(PLANT, head=(0.5, 0.3), lift=0.2, kz=0.5)),
    (1300, dict(PLANT, head=(0, -0.4))),
    (1360, dict(O=(94.0, 62.0), ang=-40, crouch=1, lean=1, shn=(5, -1), sn=0.4, kz=0.6)),
    (1420, dict(DEFI, stretch=1, sn=-0.3, kz=-0.6)),
    (1690, DEFI),
    (1800, dict(DEFI, O=(94.0, 65.0), ang=-10)),
    (1900, dict(O=(90.0, 65.0), ang=-50, crouch=1, lean=1, shn=(4, 0))),
    (2000, dict(crouch=1)),
    (2160, {}),
]
S_PLANT = 330               # la lame se plante
S_DOME = (450, 700)         # le dôme monte (puis tient jusqu'au lancement)
S_LAUNCH = 900              # LANCEMENT : le dôme s'abaisse en anneau qui s'éloigne
S_HEAL = 1060
S_DEFI = 1420

IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : un reflet d'eau clair glisse lentement le long du sabre, de la garde à la pointe, puis s'efface.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    f = (T / IDLE_T) % 1.0
    return dict(sheen=math.sin(math.pi * f), sx=f)


def idle_offsets(T):
    """La respiration lourde : le buste et les épaulières montent, la tête suit avec retard, les plaques du bas des
    épaulières avec encore plus de retard, la jupe glisse quand le poids se repose."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, heady=0.35 * math.sin(u - 0.9), sn=0.35 * math.sin(u - 1.5), sf=0.3 * math.sin(u - 1.8),
                kz=0.7 * math.sin(u - 2.2), crouch=0.25 * (0.5 - 0.5 * math.cos(u - 2.6)), tilt=0.5 * math.sin(u - 1.1))


def pose_at(T, action=None, t0=0.0):
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
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = w * idl['breath']
    for p in PAIRS:
        P[p] = (P.pop(p + 'x'), P.pop(p + 'y'))
    sg = signe(T)                                  # le signe du repos : le reflet du sabre (anim.signe)
    P['sheen'], P['sx'] = w * sg['sheen'], sg['sx']
    P['blink'] = 1.0 if (w > 0.95 and 1.3 <= (T % IDLE_T) < 1.38) else 0.0
    P['sw_front'] = P['O'][1] < 63.5 and P['ang'] < -60
    return P


# ======================================================================== les effets d'eau (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


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


def arc_band(C, R, a0, a1, w, taper=0.8, n=28, ry=1.0):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * ry * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * ry * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def trail(fig, C, R, a0, a1, w, op=1.0):
    """La traînée de la lame : un ruban d'eau en croissant (fil blanc contre la lame, cyan, bleu vers l'arrière)."""
    if abs(a1 - a0) < 4:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + 1.0, a0, a1, w)
    rim = arc_band(C, R + 1.6, a0, a1, w * 0.35)
    g1 = g_lin(fig, pa, pb, [(0, W_[4], 0), (0.55, W_[3], 0.55 * op), (1, W_[2], 0.85 * op)])
    g2 = g_lin(fig, pa, pb, [(0, W_[2], 0), (0.6, W_[1], 0.8 * op), (1, W_[0], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def crescent(fig, c, R, facing, w, span=120, op=1.0):
    """Un fin croissant d'eau tranchant, bombé vers `facing` (degrés), cornes effilées, bord d'écume devant."""
    outer, inner = [], []
    n = 26
    for i in range(n + 1):
        t = i / n
        a = math.radians(facing - span / 2 + span * t)
        ww = w * math.sin(math.pi * t) ** 0.8
        outer.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
        inner.append((c[0] + (R - ww) * math.cos(a), c[1] + (R - ww) * math.sin(a)))
    sh = sm(outer + inner[::-1][1:-1], sharp=(0, n), t=0.6)
    foam = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(facing - span / 2 + span * t)
        ww = w * 0.38 * math.sin(math.pi * t) ** 0.8
        foam.append((c[0] + (R - ww) * math.cos(a), c[1] + (R - ww) * math.sin(a)))
    fo = sm(outer + foam[::-1][1:-1], sharp=(0, n), t=0.6)
    fa = (math.cos(math.radians(facing)), math.sin(math.radians(facing)))
    gr = g_lin(fig, (c[0] + fa[0] * R, c[1] + fa[1] * R - R * 0.5), (c[0] + fa[0] * (R - w), c[1] + fa[1] * (R - w) + R * 0.5),
               [(0, W_[1]), (0.4, W_[3]), (1, W_[4])])
    return outlined([(sh, gr, 1), (fo, W_[0], 0.95)], w=1.2, op=op)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte : bille ronde devant, effilée derrière (dans le sens de sa course), éclairée en haut à droite."""
    a = math.atan2(vy, vx)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), (x - r, y + r), [(0, W_[1]), (0.5, W_[3]), (1, W_[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.34, r * 0.26), W_[0], 0.95)], w=1.0, op=op)


def bead(fig, x, y, r=1.0, op=1.0):
    """Une bulle (ou une goutte ronde) : un rond clair bordé, un reflet."""
    gr = g_rad(fig, (x + r * 0.3, y - r * 0.3), r * 1.3, [(0, W_[1]), (0.6, W_[2]), (1, W_[3])])
    return outlined([(ellipse(x, y, r, r), gr, 0.9), (ellipse(x + r * 0.35, y - r * 0.35, r * 0.3, r * 0.24), W_[0], 1)], w=0.8, op=op)


def sheet(fig, base, h, w, lean=0.0, bend=0.0, op=1.0):
    """Une gerbe d'eau : une langue qui jaillit du point `base`, large en bas, pointe qui se recourbe."""
    if h < 0.8:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.15, by - h * 0.35)
    p2 = (bx - bend * w * 0.4 + lean * h * 0.6, by - h * 0.72)
    p3 = (bx + lean * h + bend * w * 0.6, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.2)
    gr = g_lin(fig, p3, p0, [(0, W_[1]), (0.45, W_[2]), (1, W_[4])])
    q = lambda p, k: (bx + (p[0] - bx) * k + 0.3, by + (p[1] - by) * k)
    hl = lock((bx + w * 0.15, by), q(p1, 0.9), q(p2, 0.9), q(p3, 0.88), w * 0.32, n=8, bulge=0.1)
    return outlined([(sh, gr, 1), (hl, W_[0], 0.8)], w=1.1, op=op)


def stream(fig, pts, w0, w1, gr_dir=None, op=1.0):
    """Un ruban d'eau le long d'une ligne (effilé aux deux bouts) : dégradé, écume sur le dessus."""
    if len(pts) < 3:
        return ''
    n = len(pts) - 1
    ws = [max(0.12, (w0 + (w1 - w0) * i / n) * math.sin(math.pi * min(1, (i + 0.5) / n)) ** 0.5) for i in range(n + 1)]
    sh = ribbon(pts, ws)
    top = ribbon([(x + 0.25, y - ws[i] * 0.22) for i, (x, y) in enumerate(pts)], [w * 0.35 for w in ws])
    a, b = gr_dir or (pts[0], pts[-1])
    gr = g_lin(fig, a, b, [(0, W_[2]), (0.5, W_[3]), (1, W_[4])])
    return outlined([(sh, gr, 1), (top, W_[0], 0.75)], w=1.0, op=op)


def ground_ring(fig, cx, rx, ry, w, op, front):
    """L'anneau d'eau posé au sol (ellipse aplatie) : sa moitié de derrière ou de devant."""
    if op <= 0.02 or rx < 2:
        return ''
    a0, a1 = (180, 360) if not front else (0, 180)
    outer, inner = [], []
    n = 36
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        k = 0.55 + 0.45 * abs(math.sin(a)) if front else 0.4 + 0.6 * abs(math.sin(a))
        ww = w * k
        outer.append((cx + rx * math.cos(a), GR - 0.6 + ry * math.sin(a)))
        inner.append((cx + (rx - ww) * math.cos(a), GR - 0.6 + (ry - ww * 0.45) * math.sin(a) - ww * 0.5))
    sh = sm(outer + inner[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.5)
    fo = sm(outer + [((o[0] + i_[0]) / 2, (o[1] + i_[1]) / 2) for o, i_ in zip(outer, inner)][::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.5)
    gr = g_lin(fig, (cx, GR - ry - w), (cx, GR + ry), [(0, W_[1]), (0.5, W_[3]), (1, W_[4])])
    return outlined([(sh, gr, 1), (fo, W_[1], 0.7)], w=1.0, op=op)


def glint(fig, x, y, r, op=1.0):
    """Un éclat sur l'armure : un losange aux côtés creusés (quatre pointes inégales), blanc bleuté."""
    pts = [(x, y - r), (x + r * 0.2, y - r * 0.2), (x + r * 0.7, y), (x + r * 0.2, y + r * 0.2), (x, y + r * 0.8),
           (x - r * 0.2, y + r * 0.2), (x - r * 0.6, y), (x - r * 0.2, y - r * 0.2)]
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.6)
    return '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), W_[0], max(0, min(1, op)))


def mark(fig, c, s, op=1.0):
    """La marque de la provocation (signe inventé) : un œil en amande rouge, pupille fendue, au-dessus du casque."""
    x, y = c
    alm = sm([(x - 4.6 * s, y), (x - 1.6 * s, y - 2.6 * s), (x + 1.6 * s, y - 2.6 * s), (x + 4.6 * s, y), (x + 1.6 * s, y + 2.6 * s),
              (x - 1.6 * s, y + 2.6 * s)], sharp=(0, 3), t=0.9)
    iris = ellipse(x, y, 1.9 * s, 1.9 * s)
    pup = sm([(x, y - 1.7 * s), (x + 0.55 * s, y), (x, y + 1.7 * s), (x - 0.55 * s, y)], sharp=(0, 2), t=0.8)
    gr = g_lin(fig, (x + 3 * s, y - 3 * s), (x - 3 * s, y + 3 * s), [(0, RED[1]), (0.5, RED[2]), (1, RED[3])])
    return outlined([(alm, gr, 1), (iris, g_rad(fig, (x + 0.5 * s, y - 0.5 * s), 2.4 * s, [(0, RED[0]), (0.6, RED[1]), (1, RED[2])]), 1),
                     (pup, RED[4], 1), (ellipse(x + 0.8 * s, y - 0.9 * s, 0.4 * s, 0.32 * s), '#ffffff', 1)], ink='#3a0818', w=1.2, op=op)


# ---- l'attaque de base

HIT = {}


def fx_attack(tl, ang_prev):
    def f(fig, ctx):
        O, ang, tip = ctx['O'], ctx['ang'], ctx['tip']
        R = math.dist(O, tip)
        a1 = ang
        a0 = ang_prev + ctx['P']['lean']
        while a0 > a1 + 180:
            a0 -= 360
        while a0 < a1 - 180:
            a0 += 360
        if abs(a1 - a0) > 14 and A_CUT[0] <= tl <= A_CUT[1] + 40:
            fig.fx_back.append(trail(fig, O, R, a0, a1, 10))
        # quelques gouttes arrachées au fil pendant la coupe
        if A_CUT[0] + 30 <= tl <= A_CUT[1] + 120:
            k = (tl - A_CUT[0] - 30) / 150.0
            for i, (da, dr) in enumerate(((-14, 3), (-34, 5), (-52, 2))):
                a = math.radians(ang + da)
                p = (O[0] + (R + dr + 10 * k) * math.cos(a), O[1] + (R + dr + 10 * k) * math.sin(a) + 6 * k * k)
                fig.fx_front.append(drop(fig, p[0], p[1], -math.sin(a), math.cos(a), 1.0 if i % 2 else 0.8, op=1 - k))
        # le fin croissant d'eau : il se détache du bout de la lame, file vers l'ennemi, le fend
        if A_MOON <= tl < A_HIT + 40:
            k = ease((tl - A_MOON) / (A_HIT - A_MOON))
            c0 = (HIT['tip'][0] - 10, HIT['tip'][1] - 16)
            c1 = (FOE[0] - 14, FOE[1] - 4)
            c = (c0[0] + (c1[0] - c0[0]) * k, c0[1] + (c1[1] - c0[1]) * k - 6 * math.sin(math.pi * k))
            fig.fx_front.append(crescent(fig, c, 22 - 2 * k, -14 + 6 * k, 6.2 - 1.6 * k, span=118, op=min(1, (tl - A_MOON) / 40)))
            if k > 0.15:
                for j in range(3):
                    kk = max(0, k - 0.12 - 0.08 * j)
                    if kk > 0:
                        cc = (c0[0] + (c1[0] - c0[0]) * kk + 14, c0[1] + (c1[1] - c0[1]) * kk + 6 + 5 * j)
                        fig.fx_back.append(drop(fig, cc[0], cc[1] + 6 * j, 1, 0.2, 0.7 + 0.2 * (j % 2), op=0.8 - 0.25 * j))
        # la gerbe sur l'ennemi
        tau = (tl - A_HIT) / 1000.0
        if tau >= 0:
            X, Y = FOE
            e = env(tau, 0, 0.05, 0.14, 0.42)
            if e > 0:
                fig.fx_back.append(crescent(fig, (X - 12, Y - 2), 20, -8, 4.0 * e, span=110, op=e))
                for j, (lean, h, w) in enumerate(((-0.5, 16, 5.0), (0.2, 22, 6.0), (0.9, 15, 4.6))):
                    fig.fx_front.append(sheet(fig, (X + 2 + 4 * j, Y + 6), h * e, w, lean=lean, bend=0.6 - 0.6 * j, op=e))
            for i, (vx, vy, r) in enumerate(((60, -90, 1.2), (95, -40, 1.0), (30, -120, 0.9), (110, 10, 0.8), (-30, -80, 1.0), (75, -110, 0.8))):
                if tau < 0.65:
                    x, y = ballistic((X + 4, Y + 2), (vx, vy), 220, tau)
                    fig.fx_front.append(drop(fig, x, y, vx, vy + 220 * tau, r, op=max(0, 1 - tau / 0.65)))
        # le chiburi : il secoue la lame, quelques gouttes s'envolent du fil
        tau = (tl - A_SHAKE) / 1000.0
        if 0 <= tau < 0.5:
            for i, (fr, vx, vy) in enumerate(((0.55, 30, 20), (0.75, 45, 10), (0.9, 55, 30), (1.0, 70, 5), (0.65, 20, 40))):
                p = (O[0] + fr * (tip[0] - O[0]), O[1] + fr * (tip[1] - O[1]))
                x, y = ballistic(HIT.get('shake_' + str(i), p), (vx, vy - 40), 240, tau)
                HIT.setdefault('shake_' + str(i), p)
                if y < GR:
                    fig.fx_front.append(drop(fig, x, y, vx, vy - 40 + 240 * tau, 0.8 + 0.2 * (i % 2), op=1 - tau / 0.5))
    return f


# ---- l'attaque spéciale

SP = {}


def helix(cx, h_max, rx, ph, turns, level, n=40):
    """Une spirale d'eau sur la surface du dôme : (x, y, devant ?) du pied jusqu'à la hauteur atteinte."""
    out = []
    for i in range(n + 1):
        t = i / n * level
        h = h_max * t
        r = rx * math.sqrt(max(0.0, 1 - t * t)) + 1.5
        th = math.radians(ph) + 2 * math.pi * turns * t
        out.append((cx + r * math.cos(th), GR - 1 - h + r * 0.16 * math.sin(th), math.sin(th) > 0, t))
    return out


def runs(pts):
    """Coupe une ligne en morceaux de même côté (devant / derrière)."""
    out, cur = [], [pts[0]]
    for p in pts[1:]:
        if p[2] != cur[-1][2]:
            cur.append(p)
            out.append(cur)
            cur = [p]
        else:
            cur.append(p)
    out.append(cur)
    return out


def fx_special(tl, ang_prev):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        O, tip = ctx['O'], ctx['tip']
        cx = 64.0
        # la gerbe du sabre planté
        tau = (t - S_PLANT) / 1000.0
        if 0 <= tau < 0.45:
            e = env(tau, 0, 0.04, 0.12, 0.45)
            x = tip[0]
            fig.fx_front.append(E.gerbe(fig, x + 0.5, GR, min(0.95, tau / 0.45), 0.95, seed=1))
            for i, (vx, vy) in enumerate(((-60, -110), (70, -120), (10, -150))):
                px, py = ballistic((x, GR - 3), (vx, vy), 380, tau)
                if py < GR:
                    fig.fx_front.append(drop(fig, px, py, vx, vy + 380 * tau, 1.0 if i % 2 else 0.8, op=1 - tau / 0.45))
            fig.fx_back.append(ground_ring(fig, x, 8 + 30 * tau, 2.0 + 4 * tau, 2.4, (1 - tau / 0.45) * 0.9, False))
            fig.fx_front.append(ground_ring(fig, x, 8 + 30 * tau, 2.0 + 4 * tau, 2.4, (1 - tau / 0.45) * 0.9, True))
        # le dôme d'eau qui monte en spirale et tourne autour de lui
        if S_DOME[0] <= t < S_LAUNCH + 140:
            level = ease((t - S_DOME[0]) / (S_DOME[1] - S_DOME[0]))
            down = ease((t - S_LAUNCH) / 140.0) if t >= S_LAUNCH else 0.0
            ph = (t - S_DOME[0]) * 0.36
            H, RX = 104 * (1 - 0.85 * down), 58 + 30 * down
            op = 1 - down
            for j in range(3):
                # UN ruban d'eau en spirale sur la surface du dôme (effets_pro), coupé devant / derrière sans jonction visible
                if level > 0.03:
                    bk, fr, _ = E.spirale(fig, (cx, GR - 1), RX, RX, ph + 120 * j, 360 * 1.15 * level, 6.4, tilt=0.16, rise=H * level,
                                          p='eau', n=40, stops=E.spirale_feu('eau'),
                                          rfun=lambda u, L=level: RX * math.sqrt(max(0.0, 1 - (u * L) ** 2)) + 1.5)
                    fig.fx_back.append(E.group(bk, op * 0.85))
                    fig.fx_front.append(E.group(fr, op))
            # le voile du dôme (translucide), et l'eau qui tourbillonne à son pied
            if level > 0.15:
                gy = GR - H * level
                veil = sm([(cx - RX, GR), (cx - RX * 0.95, GR - H * 0.4 * level), (cx - RX * 0.6, GR - H * 0.85 * level),
                           (cx, gy - 2), (cx + RX * 0.6, GR - H * 0.85 * level), (cx + RX * 0.95, GR - H * 0.4 * level), (cx + RX, GR)])
                fig.fx_back.append('<path d="%s" fill="%s"/>' % (veil.d(), g_lin(fig, (cx, gy), (cx, GR), [(0, W_[2], 0.05 * op), (1, W_[3], 0.22 * op)])))
            fig.fx_back.append(ground_ring(fig, cx, RX * (0.6 + 0.4 * level), 7, 3.0, 0.9 * op, False))
            fig.fx_front.append(ground_ring(fig, cx, RX * (0.6 + 0.4 * level), 7, 3.0, 0.9 * op, True))
            if 0.3 < level:
                for j in range(5):
                    a = math.radians(ph * 2.2 + 72 * j)
                    r = RX * 0.9
                    x, y = cx + r * math.cos(a), GR - 8 - 30 * ((j * 0.37) % 1) * level
                    (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(drop(fig, x, y, -math.sin(a), 0.3, 0.8, op=0.8 * op))
        # LANCEMENT : l'anneau d'eau s'éloigne tout autour de lui, s'abaisse et se défait en arcs
        if S_LAUNCH <= t < S_LAUNCH + 520:
            k = (t - S_LAUNCH) / 520.0
            rx = 60 + 120 * ease(k)
            ry = 9 + 10 * ease(k)
            op = env(k, 0, 0.08, 0.55, 1.0)
            w = 5.0 * (1 - 0.6 * k)
            fig.fx_back.append(ground_ring(fig, cx, rx, ry, w, op, False))
            fig.fx_front.append(ground_ring(fig, cx, rx, ry, w, op, True))
            for j in range(3):
                a = math.radians(40 + 130 * j)
                x, y = cx + rx * math.cos(a), GR - 0.6 + ry * math.sin(a)
                (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(E.gerbe(fig, x, y + 0.6, min(0.95, 0.2 + k), 0.55, op=op, seed=j))
        # l'armure d'eau : une lueur bleue, des éclats qui scintillent sur les plaques
        arm = env(t, S_LAUNCH, S_LAUNCH + 120, S_DEFI, S_DEFI + 260)
        if arm > 0:
            ch = ctx['chest']
            fig.under.append((ch[0], ch[1] - 10, 46, 56, W_[3], 0.3 * arm, None))
            spots = [(45, 60), (92, 62), (70, 22), (60, 82), (84, 88), (41, 72), (95, 70), (78, 32), (52, 92), (88, 104)]
            for j, (x, y) in enumerate(spots):
                ph = (t / 1000.0) * 3.0 + j * 0.61
                s = max(0.0, math.sin(ph * math.pi)) ** 3
                if s > 0.05:
                    fig.over.append(glint(fig, x + ctx['U'][4], y + ctx['U'][5], 3.2 * s, op=arm * s))
        # le soin : un peu d'eau claire tombe sur lui, de petites bulles montent
        if S_HEAL <= t < S_HEAL + 600:
            k = (t - S_HEAL) / 600.0
            for j in range(4):
                st = j * 0.1
                kk = (k - st) / 0.5
                if 0 <= kk <= 1:
                    x = 48 + 12 * j
                    y = -30 + 70 * kk * kk
                    fig.fx_front.append(drop(fig, x, y, 0, 1, 0.9, op=1 - kk ** 3))
            for j in range(4):
                kk = (k - 0.25 - 0.1 * j) / 0.6
                if 0 <= kk <= 1:
                    x = 46 + 12 * j + 2 * math.sin(kk * 7 + j)
                    y = 100 - 70 * kk - 4 * (j % 3)
                    fig.fx_front.append(bead(fig, x, y, 0.7 + 0.3 * (j % 3), op=math.sin(math.pi * kk)))
        # le défi : une lueur rouge douce qui gonfle puis s'éteint, la marque qui bat au-dessus du casque
        dv = env(t, S_DEFI - 40, S_DEFI + 60, S_DEFI + 300, 1820)
        if dv > 0:
            ch = ctx['chest']
            pulse = 0.5 + 0.5 * math.sin((t - S_DEFI) / 1000.0 * 2 * math.pi * 3.0)
            fig.under.append((ch[0], ch[1] - 8, 44 + 6 * pulse, 58 + 6 * pulse, RED[2], (0.22 + 0.16 * pulse) * dv, None))
            c = ctx['crest']
            fig.over.append(mark(fig, (c[0], c[1] - 10), (1.15 + 0.2 * pulse) * (0.6 + 0.4 * dv), op=dv))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce au sol."""
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
    sh = Image.new('RGBA', (w, h))
    cx = (62 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 38 * k, fy - 3.2 * k, cx + 38 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite : repos ×2, attaque ×2, spéciale ×1 (en secondes)."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', IDLE_T * 0.6), ('attack', A), ('idle', IDLE_T * 0.8),
           ('special', S), ('idle', IDLE_T)]
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
        Pp = pose_at(T - 0.05, act, t0)
        if act == 'attack':
            if HIT.get('t0') != t0:
                HIT.clear()
                HIT['t0'] = t0
                Ph = pose_at(t0 + A_MOON / 1000.0, act, t0)
                HIT['tip'] = Z.build(pose=Ph).ctx['tip']
            fx = [fx_attack(tl, Pp['ang'])]
        else:
            fx = [fx_special(tl, Pp['ang'])]
    return Z.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        i = sys.argv.index('--planche')
        if len(sys.argv) > i + 1:
            moments = [{'a': a_s, 's': s_s}.get(m[0], 0) + float(m.lstrip('as')) for m in sys.argv[i + 1].split(',')]
        else:
            moments = [1.0, a_s + 0.2, a_s + 0.4, a_s + 0.5, a_s + 0.54, a_s + 0.7, a_s + 0.9, a_s + 1.0,
                       s_s + 0.26, s_s + 0.36, s_s + 0.6, s_s + 0.8, s_s + 0.98, s_s + 1.2, s_s + 1.5, s_s + 1.9]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.environ.get('PLANCHE_OUT', TMP), 'planche.png')
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
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                    '-vf', 'fps=12,scale=400:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    gifp], check=True)
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement, les petits outils d'effets ci-dessus passent par effets_pro (anneaux et rubans d'eau d'un seul
# tenant, gouttes étirées par leur course, perles et reflets en lumière, marque sans contour) ; l'attaque garde son dessin.
import effets_pro as E  # noqa: E402


def _ground_ring(fig, cx, rx, ry, w, op, front):
    if op <= 0.02 or rx < 2:
        return ''
    a0, a1 = (180, 360) if not front else (0, 180)
    return E.ruban(fig, E.arc_ell((cx, GR - 0.6), rx, ry, a0, a1), w * 1.7, 'eau', op=op * (1 if front else 0.75), kind='fuseau')


E.accrocher(sys.modules[__name__], {
    'ground_ring': _ground_ring,
    'stream': lambda fig, pts, w0, w1, gr_dir=None, op=1.0: E.ruban(fig, pts, max(w0, w1) * 1.6, 'eau', op=op, kind='fuseau'),
    'drop': lambda fig, x, y, vx, vy, r=1.0, op=1.0: E.goutte(fig, x, y, vx * 40, vy * 40 + 20, r, 'eau', op=op),
    'bead': lambda fig, x, y, r=1.0, op=1.0: E.lumiere(fig, (x, y), r * 3.2, op, 'eau'),
    'glint': lambda fig, x, y, r, op=1.0: E.lumiere(fig, (x, y), r * 2.2, op, 'eau'),
    'mark': lambda fig, c, s, op=1.0: E.amande(fig, c, 5.4 * s, 'sang', op=op),
})


if __name__ == '__main__':
    main()
