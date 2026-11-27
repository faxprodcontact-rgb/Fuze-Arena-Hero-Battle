# L'oiseau-tempête vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/
# oiseau-tempete/build.py) — respiration, attaque de base « Bec-tempête », attaque spéciale « Ouragan » — dans le style
# lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/oiseau-tempete/anim.py          # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/oiseau-tempete/anim.py --planche [instants en s]   # planche de contrôle
#
# Méthode (celle de Kael et de Sorai, ../../heros/sorai/anim.py, dont les petits effets de vent sont recopiés ici) : le
# dessin (oiseau-tempete.py) est fait de morceaux ; chaque image le redessine dans une POSE (le corps qui se ramasse et
# se penche depuis les hanches, les serres collées au sol ; le cou qui s'étire avec la tête ; la tête qui part par
# à-coups comme un oiseau ; le bec du bas qui pivote au coin du bec ; les AILES qui tournent autour de l'épaule — la
# lointaine en retard —, les rémiges qui s'écartent, le bout des plumes qui traîne ; la crête et la queue qui suivent).
# Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps) et sont reliées par des courbes douces sans
# dépassement. Effets de vent et d'orage dessinés dans le même style : dégradés, un seul contour par objet, aucun flou
# SVG, éclairs EN COURBES (jamais de zigzag droit), jamais de rayons droits répétés.
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
spec = importlib.util.spec_from_file_location('oiseau_tempete', os.path.join(HERE, 'oiseau-tempete.py'))
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, resample, bez, mapp, f as fm  # noqa: E402
from outils import feather, plume, unit, add, lerp, norm, crpath  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'oiseau-tempete')
TMP = os.environ.get('VECTO_TMP_ANIM') or '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-oiseau-tempete/images'
FPS = 24
VIEW = (-26.0, -62.0, 560.0, 315.0)   # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
HIT = (452.0, 180.0)                 # l'ennemi (le milieu de sa poitrine), là où frappe le vent
# le vent (mêmes tons que les effets d'Orin et de Sorai) : blanc, blanc bleuté, cyan pâle, jade clair, jade, jade sombre
WIND = ['#ffffff', '#e2faff', '#b0ecf0', '#78d6be', '#34b092', '#1a6e68']
WINK = '#123e4a'                     # le contour des effets de vent
DUST = ['#f6e4c0', '#d6b68a', '#a07c64', '#705456']
STORMC = ['#f2f0fa', '#c6c4de', '#9894bc', '#6a6492']     # le nuage d'orage (tons tirés du plumage)
BOLT = ['#ffffff', '#fff6c0', '#f8cc50', '#d8922a']        # l'éclair : cœur blanc, or de l'oiseau

# ======================================================================== petits effets (recopiés de Sorai)

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


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, _, _ in shapes_fills) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
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


def arc_band(C, R, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def smear(fig, C, R, a0, a1, w, op=1.0):
    """La traînée d'un coup d'éventail : un croissant courbe qui s'efface vers l'arrière, vent clair, liseré jade."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R - 0.5, a0, a1, w)
    rim = arc_band(C, R + 0.8, a0, a1, w * 0.34)
    g1 = g_lin(fig, pa, pb, [(0, WIND[2], 0), (0.55, WIND[1], 0.6 * op), (1, WIND[0], 0.95 * op)])
    g2 = g_lin(fig, pa, pb, [(0, WIND[3], 0), (0.5, WIND[3], 0.8 * op), (1, WIND[2], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


def spiral_pts(c, r, a0, turns, up, n=14):
    out = []
    s = -1 if up else 1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + s * 2 * math.pi * turns * t
        rr = r * (1 - 0.75 * t)
        out.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return out


def gust(fig, p0, p1, p2, p3, w, curl=3.0, up=True, op=1.0, tail=0.0):
    """Une rafale : un ruban de vent effilé le long d'une courbe, qui finit en volute ; `tail` l'efface par l'arrière."""
    if op <= 0.02 or w < 0.3:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 16)
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1
    nx, ny = (dy / L, -dx / L) if up else (-dy / L, dx / L)
    cc = (c[-1][0] + nx * curl, c[-1][1] + ny * curl)
    a0 = math.degrees(math.atan2(c[-1][1] - cc[1], c[-1][0] - cc[0]))
    sp = spiral_pts(cc, curl, a0, 0.85, False, n=12)
    alt = spiral_pts(cc, curl, a0, 0.85, True, n=12)

    def cont(s_):
        return (s_[1][0] - s_[0][0]) * dx + (s_[1][1] - s_[0][1]) * dy
    sp = sp if cont(sp) > cont(alt) else alt
    pts = c + sp[1:]
    pts = pts[int(len(pts) * tail):]
    if len(pts) < 4:
        return ''
    n = len(pts)
    ws = [w * (0.25 + 0.75 * math.sin(math.pi * min(1, (i / (n - 1)) * 1.3)) ** 0.7) * (1 - 0.8 * (i / (n - 1)) ** 2) for i in range(n)]
    ws[0], ws[-1] = 0.1, 0.1
    sh = ribbon(pts, ws)
    core = ribbon(pts[: int(n * 0.7)], [x * 0.38 for x in ws[: int(n * 0.7)]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op)


def curl(fig, c, r, a0, turn=300, w=2.0, op=1.0, cw=False):
    """Une petite volute de vent : un ruban qui s'enroule en s'affinant, un seul contour."""
    if op <= 0.02 or r < 0.6:
        return ''
    pts = []
    n = 16
    s = -1 if cw else 1
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + s * turn * t)
        rr = r * (1 - 0.6 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    ws = [0.15] + [w * (1 - 0.7 * i / n) * min(1, i / 3) for i in range(1, n)] + [0.1]
    sh = ribbon(pts, ws)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, WIND[0]), (0.5, WIND[2]), (1, WIND[3])])
    return outlined([(sh, gr, 1)], w=0.9, op=op)


def ring_arc(fig, c, rx, ry, a0, a1, w, op=1.0, tones=None):
    """Un arc de vent (morceau d'ellipse effilé aux deux bouts), cœur blanc."""
    if op <= 0.02 or abs(a1 - a0) < 3:
        return ''
    pts = []
    n = 24
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)))
    ws = [w * math.sin(math.pi * i / n) ** 0.6 + 0.1 for i in range(n + 1)]
    sh = ribbon(pts, ws)
    core = ribbon(pts[4:n - 3], [x * 0.4 for x in ws[4:n - 3]])
    t = tones or (WIND[4], WIND[2], WIND[3])
    gr = g_lin(fig, pts[0], pts[-1], [(0, t[0]), (0.5, t[1]), (1, t[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def puff(fig, cx, cy, r, op=1.0, tones=None, ink=None):
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


def bezier(p0, p1, p2, p3, n):
    return bez(p0, p1, p2, p3, n)


def along(pts, s):
    s = max(0.0, min(1.0, s))
    x = s * (len(pts) - 1)
    i = min(len(pts) - 2, int(x))
    t = x - i
    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)


def helix(fig, cx, y0, h, r0, r1, turns, phase, w, flat_=0.32, t0=0.0, t1=1.0, op=1.0, sway=0.0):
    """Une spirale de vent qui monte en s'évasant (de y0, en bas, à y0 − h ; rayon r0 → r1). Elle passe devant le
    sujet quand elle tourne du côté du spectateur, derrière sinon : renvoie (derrière, devant). Un seul ruban, effilé
    aux deux bouts ; t0..t1 : la partie dessinée."""
    back, front = [], []
    if op <= 0.02 or t1 - t0 < 0.02:
        return back, front
    n = int(turns * 64) + 12
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = math.radians(phase) + 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        x = cx + r * math.cos(a) + sway * t * t
        y = y0 - h * t + r * flat_ * math.sin(a)
        pts.append((x, y, math.sin(a) > 0, t))
    # couper en morceaux devant / derrière
    segs = []
    cur = [pts[0]]
    for p in pts[1:]:
        if p[2] != cur[-1][2]:
            cur.append(p)
            segs.append(cur)
            cur = [p]
        else:
            cur.append(p)
    segs.append(cur)
    for sg in segs:
        if len(sg) < 3:
            continue
        P = [(x, y) for x, y, _, _ in sg]
        ws = []
        for j, (_, _, _, t) in enumerate(sg):
            u = (t - t0) / max(1e-6, t1 - t0)
            ww = w * (0.35 + 0.65 * t) * min(1, u * 6) * min(1, (1 - u) * 6)
            ends = min(1.0, j / 2.0, (len(sg) - 1 - j) / 2.0)
            ws.append(max(0.1, ww * (0.35 + 0.65 * ends)))
        sh = ribbon(P, ws)
        fr = sg[len(sg) // 2][2]
        if fr:
            core = ribbon(P, [x * 0.38 for x in ws])
            gr = g_lin(fig, P[0], P[-1], [(0, WIND[2]), (0.5, WIND[1]), (1, WIND[3])])
            front.append(outlined([(sh, gr, 1), (core, WIND[0], 0.9)], w=1.0, op=op))
        else:
            gr = g_lin(fig, P[0], P[-1], [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[4])])
            back.append(outlined([(sh, gr, 1)], w=1.0, op=op * 0.95))
    return back, front




# ======================================================================== les poses clés (temps du pixel art)
NUM = ['crouch', 'lean', 'headx', 'heady', 'tilt', 'jaw', 'crest', 'wn', 'wf', 'wns', 'wfs', 'wd', 'tail', 'glow']


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# 2) L'attaque de base « Bec-tempête » (pixel : ATTAQUE). Il reste à sa place. Il se ramasse et recule la tête, bec
# grand ouvert, la crête se couche, l'aile se soulève, un souffle s'enroule devant le bec (tenu) ; la tête part comme
# un fouet vers l'avant et le bec claque : un croissant de vent naît du claquement et file vers la cible, frappe sa
# poitrine (éclat, entaille de vent, plumes, petite étincelle courbe d'or) et se défait ; la tête revient par à-coups.
ATTACK = [
    (0, {}),
    (150, dict(crouch=1.5, lean=-3, head=(-5, -4), tilt=-6, jaw=1.6, crest=1.0, wn=6, wf=-3, wns=2, tail=0.5)),
    (390, dict(crouch=1.8, lean=-3.6, head=(-6, -5), tilt=-7, jaw=2.2, crest=1.2, wn=8, wf=-4, wns=3, tail=0.6)),
    (440, dict(crouch=1.2, lean=5, head=(9, 5), tilt=7, jaw=-6, crest=-0.6, wn=-4, wf=4, wns=-1, wd=2)),
    (520, dict(crouch=1.0, lean=5.2, head=(9.5, 5.5), tilt=8, jaw=-6, crest=-0.8, wn=-5, wf=5, wd=3)),
    (620, dict(crouch=0.8, lean=3.6, head=(6, 3), tilt=5, jaw=-1, crest=0.3, wn=-2, wf=3, wd=2)),
    (700, dict(crouch=0.6, lean=3.4, head=(6, 3), tilt=5, jaw=0.4, crest=0.4, wn=-1, wf=2, wd=1)),
    (800, dict(crouch=0.5, lean=1.8, head=(3, 1), tilt=2, jaw=0.6, crest=0.1, wn=1, wf=1)),
    (880, dict(crouch=0.4, lean=1.6, head=(3, 1), tilt=2, jaw=0.2, crest=-0.2, wn=1.5)),
    (1000, dict(crouch=0.6, lean=0.4, head=(1, 1), jaw=0, crest=-0.3, wn=1)),
    (1140, dict(crest=0.15, wn=0.3)),
    (1290, {}),
]
AT_SNAP, AT_HIT = 440, 650                     # le bec claque (le croissant naît) / il frappe la cible (ms)

# 3) L'attaque spéciale « Ouragan » (pixel : SPECIALE). Il se ramasse ; ses deux ailes s'ouvrent en grand, il se
# dresse, la tête haute, bec ouvert (le cri) ; les éclairs d'or de son plumage s'embrasent ; le vent s'enroule autour
# de lui et soulève des plumes. Il lève encore les ailes (tenu), puis les rabat d'un coup énorme : une traînée suit le
# bout des ailes, une grande rafale part au ras du sol vers les héros. Sur la cible : le nuage d'orage se forme, le vent
# tourne autour d'elle, des arcs d'éclair courbes tombent, des plumes volent ; puis tout se défait, il replie les ailes.
SPECIAL = [
    (0, {}),
    (160, dict(crouch=3, lean=2, head=(-2, 3), tilt=2, jaw=1.2, crest=0.8, wn=-4, wf=4, tail=0.6)),
    (270, dict(crouch=1, lean=-2, head=(-1, -4), tilt=-6, jaw=2.5, crest=-0.6, wn=22, wf=-6, wns=4, wfs=2, glow=1, tail=1)),
    (380, dict(crouch=-0.5, lean=-4, head=(-3, -8), tilt=-12, jaw=3.0, crest=-1.0, wn=38, wf=-10, wns=7, wfs=4, glow=2, tail=1.4)),
    (620, dict(crouch=-0.8, lean=-4.4, head=(-3.4, -8.6), tilt=-13, jaw=3.2, crest=-1.1, wn=44, wf=-12, wns=8, wfs=5, glow=2, tail=1.5)),
    (850, dict(crouch=-1.0, lean=-4.8, head=(-3.6, -9), tilt=-13, jaw=3.4, crest=-1.2, wn=48, wf=-13, wns=9, wfs=5, glow=2, tail=1.6)),
    (920, dict(crouch=2.5, lean=6, head=(6, 4), tilt=6, jaw=1.0, crest=1.0, wn=-38, wf=16, wns=4, wfs=4, wd=6, glow=2, tail=0.4)),
    (1010, dict(crouch=3, lean=7, head=(7, 5), tilt=7, jaw=1.4, crest=1.1, wn=-46, wf=20, wns=2, wfs=3, wd=8, glow=1.8, tail=0.2)),
    (1270, dict(crouch=2.6, lean=6.4, head=(6.4, 4.6), tilt=6, jaw=1.6, crest=0.9, wn=-44, wf=19, wns=2, wfs=3, wd=6, glow=1.4, tail=0.2)),
    (1370, dict(crouch=1.6, lean=4, head=(3, 1), tilt=3, jaw=1.8, crest=0.2, wn=-28, wf=12, wd=3, glow=1)),
    (1480, dict(crouch=1, lean=2.4, head=(2, 0), tilt=1, jaw=1.2, crest=-0.2, wn=-12, wf=6, glow=0.6)),
    (1600, dict(crouch=0.4, lean=1, head=(0.5, 0), jaw=0.4, crest=0.2, wn=-2, wf=4, glow=0.3)),
    (1740, dict(crouch=0.8, head=(0, 1), crest=0.3, wn=4, wf=-2, wd=-2)),
    (1910, dict(crouch=0.2, crest=0, wn=1, wf=-0.5, wd=-0.5)),
    (2170, {}),
]
SP_CHARGE = (200, 900)
SP_BEAT = (850, 1000)
SP_GUST = (900, 1400)
SP_STORM = (1000, 2050)
IDLE_T = 2.6                          # une respiration (s) : lente, c'est un géant


def idle_offsets(T):
    """La respiration d'un géant : le poitrail se gonfle, la tête suit avec retard et fait de petits à-coups d'oiseau ;
    l'aile levée respire (le bout des plumes en retard), la lointaine en retard encore ; la crête et la queue suivent."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # les petits à-coups de la tête (un oiseau ne tourne pas la tête en continu)
    step = math.floor((T % (2 * IDLE_T)) / (IDLE_T / 2))
    jerk = [(0.0, 0.0, 0.0), (0.8, -0.3, 1.5), (0.4, 0.2, 0.5), (-0.3, 0.0, -1.0)][int(step) % 4]
    return dict(breath=br, headx=jerk[0] + 0.2 * math.sin(u - 1.0), heady=jerk[1] - 0.6 * br, tilt=jerk[2],
                wn=2.2 * math.sin(u - 0.5), wf=-1.6 * math.sin(u - 1.1), wd=1.6 * math.sin(u - 1.4),
                crest=0.25 * math.sin(u - 1.6), tail=0.15 * math.sin(u - 2.0), glow=0.15 + 0.15 * math.sin(u * 0.5))


def pose_at(T, action=None, t0=0.0):
    w = 1.0
    tl = 0.0
    act = act_l = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        act_l = keyed(keys, tl - 60)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    idl_l = idle_offsets(T - 0.15)
    src = act or flat({})
    srcl = act_l or flat({})
    V = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P = dict(crouch=V['crouch'], lean=V['lean'], head=(V['headx'], V['heady']), tilt=V['tilt'], jaw=V['jaw'],
             crest=V['crest'], wn_l=V['wn'], wf_l=srcl['wf'] + w * idl_l['wf'], wn_s=V['wns'], wf_s=srcl['wfs'],
             wd=V['wd'], tail=V['tail'], glow=max(0.0, V['glow']))
    P['breath'] = w * idl['breath']
    P['ws'] = 0.5 + (0.8 if act else 0.0)
    P['ph'] = 2 * math.pi * T / IDLE_T + (2.0 * T if act else 0.0)
    P['blink'] = 1.0 if (w > 0.95 and 1.6 <= (T % 4.3) < 1.72) else 0.0
    return P, tl


# ======================================================================== les effets propres au boss

def crescent(fig, c, R, a0, a1, w, op=1.0, tilt=0.0):
    """Un croissant de vent (effilé aux DEUX bouts) le long d'un arc autour de c ; angles en degrés (y vers le bas)."""
    if op <= 0.02:
        return ''
    n = 30
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t + tilt)
        ww = w * math.sin(math.pi * t) ** 0.8
        outer.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
        inner.append((c[0] + (R - ww) * math.cos(a), c[1] + (R - ww) * math.sin(a)))
    sh = sm(outer + inner[::-1][1:-1], sharp=(0, n), t=0.6)
    core_o = [(c[0] + (R - 0.25 * w * math.sin(math.pi * i / n) ** 0.8) * math.cos(math.radians(a0 + (a1 - a0) * i / n + tilt)),
               c[1] + (R - 0.25 * w * math.sin(math.pi * i / n) ** 0.8) * math.sin(math.radians(a0 + (a1 - a0) * i / n + tilt))) for i in range(4, n - 3)]
    core = ribbon(core_o, [0.1] + [w * 0.3 * math.sin(math.pi * (i + 4) / n) for i in range(1, len(core_o) - 1)] + [0.1])
    pa, pb = outer[0], outer[-1]
    gr = g_lin(fig, (c[0] + R, c[1] - R), (c[0] - R, c[1] + R), [(0, WIND[1]), (0.5, WIND[2]), (1, WIND[4])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.95)], w=1.1, op=op)


def bolt_arc(fig, p0, p1, bend, w, op=1.0, seed=0, branch=None):
    """Un arc d'éclair EN COURBES : trois arcs qui se répondent (jamais de zigzag droit), effilé aux deux bouts, cœur
    blanc, or de l'oiseau, un seul contour ; une lueur ronde (dégradé) à son pied."""
    if op <= 0.02:
        return ''
    d = (p1[0] - p0[0], p1[1] - p0[1])
    L = math.hypot(*d) or 1
    nx, ny = -d[1] / L, d[0] / L
    pts = []
    for i, (t, k) in enumerate(((0, 0), (0.18, 1), (0.36, -0.7), (0.56, 0.9), (0.76, -0.6), (1.0, 0))):
        s = bend * k * (1 if (seed % 2) else -1)
        pts.append((p0[0] + d[0] * t + nx * s, p0[1] + d[1] * t + ny * s))
    c = crpath(pts, 30)
    n = len(c) - 1
    ws = [max(0.12, w * math.sin(math.pi * i / n) ** 0.6) for i in range(n + 1)]
    sh = ribbon(c, ws)
    core = ribbon(c, [x * 0.38 for x in ws])
    parts = [(sh, g_lin(fig, p0, p1, [(0, BOLT[1]), (0.5, BOLT[2]), (1, BOLT[1])]), 1), (core, BOLT[0], 1)]
    if branch:
        bc = crpath([c[int(n * branch[0])], add(c[int(n * branch[0])], branch[1], 0.5), add(c[int(n * branch[0])], branch[1], 1.0)], 12)
        m = len(bc) - 1
        bws = [max(0.1, w * 0.6 * math.sin(math.pi * (0.5 + 0.5 * i / m)) ** 0.7) for i in range(m + 1)]
        parts += [(ribbon(bc, bws), BOLT[2], 1), (ribbon(bc, [x * 0.35 for x in bws]), BOLT[0], 1)]
    glow = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(p1[0]), fm(p1[1]), fm(14), g_rad(
        fig, p1, 14, [(0, '#ffffff', 0.8 * op), (0.4, BOLT[1], 0.4 * op), (1, BOLT[2], 0)]))
    return glow + outlined(parts, ink='#4a2a1c', w=1.0, op=op)


def storm_cloud(fig, cx, cy, r, op=1.0, k=1.0):
    """Le nuage d'orage : des boules réunies sous UN contour, éclairées en haut à droite, le dessous plus sombre."""
    if op <= 0.02 or r < 0.5:
        return ''
    balls = [(0, 0, 1.0), (1.0, 0.25, 0.78), (-1.05, 0.3, 0.74), (0.35, -0.55, 0.72), (-0.5, -0.4, 0.62),
             (1.75, 0.5, 0.5), (-1.8, 0.55, 0.48)]
    balls = [(cx + dx * r, cy + dy * r, rr * r * k) for dx, dy, rr in balls]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.4, cy + r * 0.9), [(0, STORMC[0]), (0.45, STORMC[1]), (1, STORMC[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), '#2a2440', '#2a2440') for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    # le dessous plat et sombre du nuage (une bande douce)
    under = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="0.55"/>' % (fm(cx), fm(cy + 0.62 * r), fm(1.9 * r), fm(0.32 * r), STORMC[3])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, under)


def storm_feather(fig, x, y, ang, s=1.0, op=1.0):
    """Une plume d'orage arrachée : la plume du dessin en petit (reflet bleu vers la lumière), un contour."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    sd = (-d[1], d[0])
    L = 13.0 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sh = feather(p0, add(lerp(p0, p3, 0.33), sd, 0.6 * s), add(lerp(p0, p3, 0.7), sd, 1.2 * s), p3, 4.4 * s, n=10)
    quill = ribbon([p0, lerp(p0, p3, 0.5), lerp(p0, p3, 0.85)], [0.6 * s, 0.4 * s, 0.1])
    M = K.STORM
    gr = g_lin(fig, (x + 3 * s, y - 3 * s), (x - 3 * s, y + 3 * s), [(0, M.hi), (0.35, M.light), (1, M.shadow)])
    return outlined([(sh, gr, 1), (quill, M.deep, 0.7)], ink='#1f1238', w=1.0, op=op)


def jade_feather(fig, x, y, ang, s=1.0, op=1.0):
    """Une petite plume jade (de la crête) emportée par le vent."""
    if op <= 0.02:
        return ''
    d = unit(ang)
    L = 9.0 * s
    p0 = (x - d[0] * L / 2, y - d[1] * L / 2)
    p3 = (x + d[0] * L / 2, y + d[1] * L / 2)
    sd = (-d[1], d[0])
    sh = plume(p0, add(lerp(p0, p3, 0.33), sd, 0.4 * s), add(lerp(p0, p3, 0.7), sd, 0.9 * s), p3, 3.6 * s, n=10, tip=0.5)
    J = K.JADE
    gr = g_lin(fig, (x + 3 * s, y - 3 * s), (x - 3 * s, y + 3 * s), [(0, J.hi), (0.4, J.light), (1, J.base)])
    return outlined([(sh, gr, 1)], ink='#103a3e', w=0.9, op=op)


# ---- l'attaque de base « Bec-tempête »

def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        bk = ctx['beak']
        # le souffle s'enroule devant le bec (tenu)
        e0 = env(t, 110, 220, 400, 460)
        if e0 > 0:
            k = min(1.0, (t - 110) / 300)
            fig.fx_back.append(curl(fig, (bk[0] + 16 - 6 * k, bk[1] - 8), 7.5 - 2 * k, 0.9 * t, 290, 2.6, op=e0))
            fig.fx_front.append(curl(fig, (bk[0] + 14 - 5 * k, bk[1] + 10), 6.5 - 1.6 * k, 200 - 0.8 * t, 280, 2.4, op=e0, cw=True))
            fig.fx_front.append(curl(fig, (bk[0] + 26 - 10 * k, bk[1] + 1), 5.0, 90 + 1.1 * t, 260, 2.0, op=e0 * 0.9))
        # le claquement : un éclat devant le bec
        e1 = env(t, AT_SNAP - 20, AT_SNAP, AT_SNAP + 30, AT_SNAP + 110)
        if e1 > 0:
            fig.fx_front.append(flash(fig, (bk[0] + 8, bk[1] + 2), 16, op=e1))
            fig.fx_front.append(ring_arc(fig, (bk[0] + 4, bk[1] + 2), 14, 16, -70, 70, 3.0, op=e1))
        # le croissant de vent file vers la cible (légère courbe), deux brins de vent derrière lui
        p0 = START.get('a') or (bk[0] + 12, bk[1] + 2)
        if AT_SNAP <= t < AT_HIT:
            u = (t - AT_SNAP) / (AT_HIT - AT_SNAP)
            u = u ** 0.9
            x = p0[0] + (HIT[0] - 10 - p0[0]) * u
            y = p0[1] + (HIT[1] - p0[1]) * u - 10 * math.sin(u * math.pi)
            s = 0.8 + 0.5 * u
            for sg, dy in ((1, -9), (-1, 9)):
                tail = 40 + 60 * u
                fig.fx_back.append(gust(fig, (x - tail, y + dy * 1.6), (x - tail * 0.6, y + dy * 1.4 + 3 * sg), (x - tail * 0.3, y + dy),
                                        (x - 6, y + dy * 0.7), 3.4, curl=0.1, up=sg > 0, op=0.9, tail=0.0))
            fig.fx_front.append(crescent(fig, (x - 12 * s, y), 20 * s, -68, 68, 9.0 * s, op=1.0, tilt=-8 + 10 * u))
        if t >= AT_HIT:
            impact(fig, t - AT_HIT)
    return f


def impact(fig, t, big=1.0):
    """Le croissant frappe la poitrine : un éclat, l'entaille de vent, une bouffée, deux volutes qui s'échappent, une
    petite étincelle courbe d'or, des plumes jade qui volent."""
    x, y = HIT
    e0 = env(t, -1, 20, 100, 300)
    if e0 > 0:
        k = min(1, t / 140)
        fig.fx_back.append(flash(fig, (x, y), 30 * big, op=e0))
        fig.fx_front.append(crescent(fig, (x - 8, y), 24 + 8 * k, -60, 60, 7 * (1 - 0.5 * k), op=e0, tilt=-20 + 30 * k))
        fig.fx_front.append(puff(fig, x + 2, y + 2, 9 * big * (1 - 0.4 * k), op=e0))
    e1 = env(t, 0, 60, 220, 560)
    if e1 > 0:
        j = min(1.0, t / 420)
        fig.fx_front.append(gust(fig, (x + 6, y - 8), (x + 18, y - 22 - 6 * j), (x + 30, y - 24 - 8 * j), (x + 40, y - 34 - 12 * j),
                                 5.0 * big, curl=6 + 2 * j, up=True, op=e1, tail=0.55 * j))
        fig.fx_back.append(gust(fig, (x + 6, y + 10), (x + 18, y + 20 + 3 * j), (x + 30, y + 18 + 5 * j), (x + 40, y + 26 + 6 * j),
                                4.2 * big, curl=5.5 + 2 * j, up=False, op=e1, tail=0.55 * j))
    e2 = env(t, 30, 60, 160, 260)
    if e2 > 0:
        fig.fx_front.append(bolt_arc(fig, (x + 4, y - 16), (x + 14, y + 6), 3.0, 2.4, op=e2, seed=1))
    e3 = env(t, 0, 40, 380, 600)
    if e3 > 0:
        tt = t / 1000.0
        for i, (dx, dy, a0, sp) in enumerate(((-6, -10, 30, 1.0), (10, -4, 120, 1.3), (2, 8, 220, 0.8))):
            fig.fx_front.append(jade_feather(fig, x + dx + 30 * tt * sp, y + dy - 20 * tt + 70 * tt * tt, a0 + 500 * tt * sp, 1.0, op=e3))


# ---- l'attaque spéciale « Ouragan »

def fx_special(tl):
    def f(fig, ctx):
        t = tl
        cx = 150.0
        # le vent s'enroule autour de lui et soulève des plumes (la charge)
        ev = env(t, SP_CHARGE[0], 450, SP_CHARGE[1] - 60, SP_CHARGE[1] + 80)
        if ev > 0:
            grow = ease((t - SP_CHARGE[0]) / 450)
            ph = -0.5 * t
            b, fr = helix(fig, cx, GR - 2, 40 + 150 * grow, 70, 105, 1.8, ph, 6.0, flat_=0.2, t0=0.0, t1=0.25 + 0.75 * grow, op=ev)
            fig.fx_back += b
            fig.fx_front += fr
            for i in range(4):
                a = math.radians(ph * 1.3 + i * 97)
                tt = 0.2 + 0.2 * i
                x = cx + 95 * math.cos(a)
                y = GR - 30 - 140 * tt * grow + 20 * math.sin(a)
                lay = fig.fx_front if math.sin(a) > 0 else fig.fx_back
                lay.append(storm_feather(fig, x, y, math.degrees(a) + 90, 0.9, op=ev))
            for j, dx in enumerate((-60, -20, 40, 80)):
                fig.fx_back.append(dust(fig, cx + dx + 3 * math.sin(t / 80 + j), GR - 2, 4.0 + 1.5 * (j % 2), op=ev * 0.85))
        # le battement : une traînée suit le bout des ailes
        e1 = env(t, SP_BEAT[0], SP_BEAT[0] + 40, SP_BEAT[1] - 20, SP_BEAT[1] + 120)
        if e1 > 0:
            R = ctx['wn_root']
            a_now = 197.6 + ctx['P']['wn_l'] + ctx['P']['lean'] * 0.8
            fig.fx_back.append(smear(fig, R, 136.0, a_now + 85 * e1, a_now - 2, 20.0, op=e1))
        # la rafale part au ras du sol vers les héros
        if SP_GUST[0] <= t < SP_GUST[1]:
            u = (t - SP_GUST[0]) / (SP_GUST[1] - SP_GUST[0])
            op = 1.0 if u < 0.6 else 1 - (u - 0.6) / 0.4
            for j, (y0, w, d0) in enumerate(((GR - 6, 7.0, 0.0), (GR - 26, 5.6, 0.12), (GR - 48, 4.4, 0.22))):
                uu = max(0.0, min(1.0, (u - d0) / 0.7))
                if uu <= 0:
                    continue
                xa = 200 + 40 * uu
                xb = 230 + (HIT[0] + 20 - 230) * ease(uu)
                fig.fx_front.append(gust(fig, (xa, y0 + 4), ((xa + xb) / 2, y0 - 4), ((xa + xb) / 2 + 30, y0 + 3), (xb, y0 - 2),
                                         w, curl=5 + j, up=j % 2 == 0, op=op, tail=0.5 * uu))
            for j, dx in enumerate((190, 215, 240)):
                fig.fx_front.append(dust(fig, dx + 40 * u, GR - 3, 5.0 * (1 - 0.5 * u), op=op * 0.9))
        # l'orage sur la cible : le nuage se forme, le vent tourne autour d'elle, des arcs d'éclair courbes tombent
        if SP_STORM[0] <= t < SP_STORM[1]:
            tt = t - SP_STORM[0]
            es = env(t, SP_STORM[0], SP_STORM[0] + 200, SP_STORM[1] - 300, SP_STORM[1])
            grow = ease(tt / 260)
            cy = HIT[1] - 112
            ph = -0.9 * t
            b, fr = helix(fig, HIT[0], GR - 2, 120, 26, 40, 1.6, ph, 4.6, flat_=0.25, t0=0.0, t1=0.3 + 0.7 * grow, op=es)
            fig.fx_back += b
            fig.fx_front += fr
            fig.fx_back.append(storm_cloud(fig, HIT[0] + 2 * math.sin(t / 300), cy, 22 * (0.4 + 0.6 * grow), op=es))
            for (a, b_, seed, br) in ((240, 330, 1, (0.45, (12, 6))), (480, 560, 2, (0.55, (-12, 8))), (700, 770, 3, None)):
                eb = env(tt, a, a + 20, b_ - 30, b_)
                if eb > 0:
                    fig.fx_front.append(bolt_arc(fig, (HIT[0] - 4 + seed * 3, cy + 12), (HIT[0] + 2 - seed * 2, HIT[1] + 18),
                                                 6.0, 4.2, op=eb, seed=seed, branch=br))
                    fig.fx_back.append(flash(fig, HIT, 34, op=eb * 0.9))
            for j in range(4):
                a = math.radians(ph * 1.6 + j * 90)
                x = HIT[0] + 34 * math.cos(a)
                y = HIT[1] + 30 - 26 * j + 8 * math.sin(a)
                lay = fig.fx_front if math.sin(a) > 0 else fig.fx_back
                lay.append(storm_feather(fig, x, y, math.degrees(a) + 90, 0.8, op=es) if j % 2 else jade_feather(fig, x, y, math.degrees(a), 1.0, op=es))
        # deux plumes arrachées par le battement descendent en se balançant
        if t >= SP_BEAT[1]:
            tt = (t - SP_BEAT[1]) / 1000.0
            e4 = env(t, SP_BEAT[1], SP_BEAT[1] + 60, 2000, 2160)
            for i, (p, side) in enumerate(((SP_STORE.get('w0', (40, 150)), -1), (SP_STORE.get('w1', (250, 60)), 1))):
                x = p[0] + side * 12 * tt + 5 * math.sin(tt * 5 + i * 2)
                y = p[1] + 10 + 60 * tt + 3 * i
                if y < GR - 4:
                    lay = fig.fx_front if i == 0 else fig.fx_back
                    lay.append(storm_feather(fig, x, y, 70 + 40 * math.sin(tt * 5 + i * 2), 1.0, op=e4))
    return f


START = {}
SP_STORE = {}

# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une lumière
    douce, l'ombre douce au sol sous lui (même fond que Kael, Orin et Sorai)."""
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
    sd = ImageDraw.Draw(sh)
    cx = (150 - x0) * k
    sd.ellipse([cx - 70 * k, fy - 4 * k, cx + 70 * k, fy + 4 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3.0 * k)))
    return im


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    A, S = ATTACK[-1][0] / 1000, SPECIAL[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', A), ('idle', 0.9), ('attack', A), ('idle', 1.2), ('special', S), ('idle', 1.6)]
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


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if 'a' not in START:
            Ph, _ = pose_at(t0 + AT_SNAP / 1000.0, act, t0)
            b = K.build(pose=Ph).ctx['beak']
            START['a'] = (b[0] + 10, b[1] + 2)
        fx = [fx_attack(tl)]
    elif act == 'special':
        if 'w0' not in SP_STORE:
            Ph, _ = pose_at(t0 + SP_BEAT[1] / 1000.0, act, t0)
            c = K.build(pose=Ph).ctx
            SP_STORE['w0'] = c['wn_tip']
            SP_STORE['w1'] = c['wf_tip']
        fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def main():
    planche = '--planche' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    segs, total = timeline()
    n = int(round(total * FPS))
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.3, a_s + 0.45, a_s + 0.55, a_s + 0.7, a_s + 0.85, s_s + 0.16, s_s + 0.4,
                            s_s + 0.8, s_s + 0.93, s_s + 1.02, s_s + 1.15, s_s + 1.3, s_s + 1.5, s_s + 1.75, s_s + 2.0]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(os.path.dirname(TMP), 'planche.png')
        sheet.save(out)
        print('planche :', out)
        return
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
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
