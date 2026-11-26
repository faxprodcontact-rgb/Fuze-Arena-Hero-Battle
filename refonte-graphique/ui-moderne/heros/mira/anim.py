# Mira vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/mira/build.py)
# — garde fière, attaque de base « Fauche du ciel », attaque spéciale « Envol de la valkyrie » (sort d'équipe) — dans
# le style lisse de l'interface, à 24 images par seconde (même méthode que Kael et Myrr : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/mira/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/mira/
#   python3 refonte-graphique/ui-moderne/heros/mira/anim.py --planche [instants…]   # une planche d'images clés (brouillon)
#
# Méthode : le dessin (mira.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et
# se penche depuis les hanches, la tête suit avec un léger retard, les ailes du casque frémissent, la tresse et la
# cape pendent et se balancent en retard ; la lance est tenue par le poing (point de prise et angle), le bras proche
# est placé par cinématique inverse depuis le poing (le coude tourne sur un arc : aucune jointure ne se décroche) ;
# le bouclier suit le buste et se lève pour le défi. Les poses clés et les durées reprennent celles du pixel art,
# reliées par des courbes douces sans dépassement.
# Effets du vent (mêmes formes et mêmes tons qu'Eldra, Myrr et Orin) : croissant de vent qui suit le fer, éclat,
# volutes, bouffées, plumes d'air ; pour la spéciale (sort d'équipe : tout naît sur elle et s'étend EN CERCLE autour
# d'elle) : la lance qui sonne sur le bouclier, de grandes ailes de vent, l'anneau de plumes de vent, l'armure de
# plumes, l'anneau qui s'élargit jusqu'au sol, le souffle qui soigne, puis la lueur rouge douce du défi. Aucun flou
# SVG ; jamais de rayons droits répétés.
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
import mira as M  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, mapp, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of, leaf  # noqa: E402

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'mira')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-mira'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-62, -58, 336.0, 189.0)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = M.GRD
AIR = 34.0                           # la hauteur de son envol (la spéciale)
CEN = (68.0, GR - 1.0)               # le centre du cercle au sol, sous elle

WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']   # le vent (celui d'Eldra, Myrr, Orin)
WINK = '#123c4a'                     # le contour des effets de vent
GOLDFX = ['#fffbe8', '#fff0b0', '#ffd45c', '#e0962e', '#a8601e']
REDS = '#ff4a5a'


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
    for i in range(n - 1):
        if ts[i] <= t <= ts[i + 1]:
            h = ts[i + 1] - ts[i]
            u = (t - ts[i]) / h
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1
            h10 = u ** 3 - 2 * u ** 2 + u
            h01 = -2 * u ** 3 + 3 * u ** 2
            h11 = u ** 3 - u ** 2
            return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]
    return vs[-1]


# les réglages animés (voir mira.py) ; gx, gy : le point de prise de la lance ; shx, shy : le bouclier ; cry : la
# bouche ; wing : les ailes de vent (0 rien, 1 naissantes, 2 grandes ouvertes, 3 battues) ; wop : leur opacité
BASE = dict(lean=0.0, crouch=0.0, lift=0.0, headx=0.0, heady=0.0, tilt=0.0, cry=1.0, wn=0.0, wf=0.0, tr=0.0, cp=0.0,
            cl=0.0, sk=0.0, gx=M.G0[0], gy=M.G0[1], ang=M.SANG0, shx=0.0, shy=0.0, sht=0.0, glow=0.0, stretch=0.0,
            wing=0.0, wop=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'grip':
            d['gx'], d['gy'] = v
        elif key == 'sh':
            d['shx'], d['shy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
A0 = M.SANG0
# 2) L'attaque de base « Fauche du ciel » (pixel : ATTAQUE) : elle lève la lance, la fait passer derrière sa tête et
# l'arme en arrière (fer vers le ciel derrière elle, buste cambré, tête relevée, tenu) ; la lance s'abat en un grand
# arc par-dessus le casque (un croissant de vent suit le fer) et finit couchée, bras tendu vers l'ennemi : éclat de
# vent au bout du fer, une virgule d'air qui continue l'arc, des plumes d'air (arrêt sur l'image) ; elle ramène la
# lance et reprend sa garde. Angles de lance en degrés (y vers le bas), continus.
ATTACK = [
    (0, {}),
    (90, dict(grip=(62.0, 76.5), ang=-34, crouch=1.0, head=(0, 0.6), tr=1.0, cp=0.6, sk=0.5)),
    (112, dict(grip=(36.5, 66.0), ang=-58, crouch=1.0, lean=-0.4, head=(-0.3, 0.6), tr=1.0, cp=0.7)),
    (136, dict(grip=(34.6, 51.0), ang=-84, crouch=1.0, lean=-0.8, head=(-0.6, 0.6), tilt=-0.8, wn=1, tr=1.0, cp=0.8)),
    (160, dict(grip=(43.0, 44.0), ang=-105, crouch=1.0, lean=-1.0, head=(-0.8, 0.6), tilt=-1.5, wn=2, tr=1.0, cp=0.8)),
    (250, dict(grip=(42.5, 42.5), ang=-132, crouch=1.2, lean=-2.0, head=(-1.0, 0.0), tilt=-4.0, wn=3, tr=2.0, cp=1.0, sk=0.8)),
    (380, dict(grip=(42.0, 42.0), ang=-135, crouch=1.3, lean=-2.2, head=(-1.1, -0.1), tilt=-4.5, wn=3, tr=2.2, cp=1.0, sk=0.8)),
    (430, dict(grip=(57.5, 33.5), ang=-72, stretch=2.0, crouch=1.0, lean=0.0, head=(0, 0), tilt=-1.0, wn=1, tr=1.0, cp=0.0)),
    (480, dict(grip=(79.0, 59.0), ang=-20, stretch=2.0, crouch=2.0, lean=2.0, head=(0.8, 0.2), tilt=2.0, wn=-2, tr=-1.0, cp=-1.0, sk=-0.6)),
    (525, dict(grip=(82.5, 61.0), ang=5, crouch=2.3, lean=3.0, head=(1.0, 0.3), tilt=3.0, wn=-3, tr=-2.0, cp=-1.0, sk=-1.0)),
    (650, dict(grip=(82.5, 61.2), ang=6, crouch=2.2, lean=3.0, head=(1.0, 0.3), tilt=3.0, wn=-2, tr=-2.0, cp=-1.0, sk=-1.0)),
    (750, dict(grip=(81.5, 61.6), ang=4, crouch=2.0, lean=2.6, head=(0.9, 0.2), tilt=2.4, wn=-1, tr=-1.0, cp=0.0, sk=-0.5)),
    (840, dict(grip=(70.5, 70.0), ang=-18, crouch=1.0, lean=1.0, head=(0.3, 0), tilt=0.8, tr=0.0, cp=1.0, sk=0.4)),
    (930, dict(grip=(63.0, 80.5), ang=-26, crouch=1.0, head=(0, 0.5), tr=1.0, cp=0.0)),
    (1040, dict(crouch=0.6, cp=-0.6, tr=0.3)),
    (1170, {}),
]
ATT_BEHIND = (95, 485)    # la lance passe derrière la tête et le corps
ATT_COUCH = (485, 900)    # couchée sous le bras (le talon passe derrière le corps)
ATT_SWING = (380, 525)    # la fauche (le croissant de vent suit le fer)
ATT_HIT = 525             # l'impact

# 3) L'attaque spéciale « Envol de la valkyrie » (pixel : SPECIALE ; sort d'équipe : défense de l'équipe, soin,
# provocation). La lance sonne sur le bord du bouclier, de grandes ailes de vent naissent dans son dos, elle bat des
# ailes et s'élève ; au plus haut, les ailes s'enroulent autour d'elle en un anneau de plumes de vent (arrêt sur
# l'anneau plein, des plumes se posent sur elle en armure) ; LANCEMENT : l'anneau s'élargit dans toutes les directions
# en descendant jusqu'au sol ; un souffle doux la soigne pendant qu'elle redescend ; elle se pose, puis lance son défi
# (bouclier levé, lance pointée vers l'ennemi, elle crie ; une lueur rouge douce pulse autour d'elle).
DEFI = dict(grip=(80.0, 58.5), ang=-8, crouch=1.0, lean=1.0, sh=(2.0, -6.0), sht=-4, head=(0.8, 0), tilt=1.5, cry=1.5,
            wn=-1, tr=-1.0, cp=-1.0)
SPECIAL = [
    (0, {}),
    (90, dict(grip=(62.0, 75.0), ang=-30, crouch=1.0, head=(0, 0.6), tr=1.0, cp=0.6)),
    (180, dict(grip=(63.4, 83.4), ang=-27, crouch=1.0, glow=2.0, tr=0.0, wn=-1)),
    (330, dict(grip=(63.2, 83.0), ang=-27, crouch=1.0, glow=1.6, head=(0, -0.4), wn=1, cl=1.0, wing=1.0, wop=0.0)),
    (430, dict(crouch=1.0, glow=1.0, head=(0, -0.6), wn=1, tr=-1.0, cp=-1.0, cl=2.0, wing=1.0, wop=1.0)),
    (580, dict(crouch=3.0, lean=-1.0, head=(0, 0.8), tilt=-1.5, tr=1.0, cp=1.0, cl=3.0, wing=2.0, wop=1.0)),
    (650, dict(lift=20.0, crouch=-1.0, head=(0, 0.8), tr=2.0, cp=1.0, cl=2.0, wing=3.0, wop=1.0, sk=1.0, grip=(63, 81))),
    (750, dict(lift=AIR, crouch=0.0, head=(0, 0), tr=1.0, cp=0.0, cl=2.0, wing=2.0, wop=1.0, sk=0.5, grip=(63, 81))),
    (800, dict(lift=AIR, head=(0, 0), wn=1, tr=0.0, cp=-1.0, cl=2.0, wing=3.0, wop=0.35, grip=(63, 81))),
    (830, dict(lift=AIR, head=(0, 0), wn=1, tr=0.0, cp=-1.0, cl=2.0, wing=3.0, wop=0.0, grip=(63, 81))),
    (1030, dict(lift=AIR, head=(0, -0.6), wn=1, tr=-1.0, cp=-1.0, cl=2.0, wing=3.0, wop=0.0, grip=(63, 81))),
    (1110, dict(lift=AIR - 4, head=(0, 0), tr=0.0, cp=0.0, cl=1.0, grip=(63, 81))),
    (1200, dict(lift=AIR - 12, head=(0, 0), wn=-1, tr=1.0, cp=1.0, cl=1.0, sk=-0.6)),
    (1310, dict(lift=AIR - 28, crouch=-1.0, head=(0, 0.8), tr=2.0, cp=2.0, sk=-1.0)),
    (1400, dict(lift=0.0, crouch=3.0, head=(0, 1.0), wn=1, tr=1.0, cp=1.0, sk=0.6)),
    (1460, dict(grip=(70.5, 64.5), ang=-22, crouch=2.0, sh=(1.0, -3.0), head=(0, 1.0), cry=1.2)),
    (1560, DEFI),
    (1680, dict(DEFI, wn=0, tr=-2.0)),
    (1790, dict(DEFI, tr=-1.0, cry=0.9)),
    (1890, dict(DEFI, cry=0.0, cp=0.0)),
    (1960, dict(grip=(70.5, 68.5), ang=-20, crouch=1.0, lean=1.0, sh=(1.0, -3.0), cry=0.3)),
    (2050, dict(grip=(63.0, 80.5), ang=-26, crouch=1.0, sh=(0, -1.0), head=(0, 1.0), cry=0.8)),
    (2150, dict(crouch=0.6, cp=-0.6)),
    (2260, {}),
]
SP_CLANG = 180          # la lance sonne sur le bouclier
SP_WINGS = (330, 830)   # les ailes de vent
SP_RING = (750, 1030)   # l'anneau de plumes se forme, plein (arrêt sur l'image 830..1030)
SP_LAUNCH = 1030        # LANCEMENT : l'anneau part d'elle
SP_HEAL = (1110, 1400)  # le souffle qui soigne
SP_DEFI = (1460, 1890)  # la lueur rouge du défi
SP_COUCH = (1430, 1990)


# ======================================================================== la respiration (1,6 s)
IDLE_T = 1.6


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # la tête suit le souffle avec retard ; les ailes du casque frémissent ; la tresse et la cape se balancent en
    # retard (elles pendent) ; la jupe aussi, d'un rien
    d = dict(heady=-0.25 * (0.5 - 0.5 * math.cos(u - 0.6)), tilt=0.35 * math.sin(u - 1.0),
             wn=1.6 * math.sin(u - 0.9), wf=1.4 * math.sin(u - 1.3), tr=1.2 * math.sin(u - 1.8),
             cp=0.5 * math.sin(u - 2.2), sk=0.25 * math.sin(u - 2.0))
    return d, br


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 120), max(0.0, (tl - (dur - 200)) / 200))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    br *= w
    behind = couch = False
    if action == 'attack':
        behind = ATT_BEHIND[0] <= tl < ATT_BEHIND[1]
        couch = ATT_COUCH[0] <= tl < ATT_COUCH[1]
    elif action == 'special':
        couch = SP_COUCH[0] <= tl < SP_COUCH[1]
    out = dict(breath=br, lean=P['lean'], crouch=P['crouch'], lift=P['lift'], head=(P['headx'], P['heady']),
               tilt=P['tilt'], cry=P['cry'], wn=P['wn'], wf=P['wf'] + 0.6 * P['wn'], tr=P['tr'] * 3.0, cp=P['cp'],
               cl=P['cl'], sk=P['sk'], grip=(P['gx'], P['gy']), ang=P['ang'], sh=(P['shx'], P['shy']), sht=P['sht'],
               glow=max(0.0, P['glow']), stretch=P['stretch'], behind=behind, couch=couch,
               wing=P['wing'], wop=max(0.0, min(1.0, P['wop'])))
    out['blink'] = 1.0 if (w > 0.95 and 1.10 <= (T % 3.2) < 1.19) else 0.0
    return out


# ======================================================================== les effets (dégradés, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, r if ry is None else ry, stops)


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


def glow(fig, c, r, color, op, ry=None):
    ry = r if ry is None else ry
    if op <= 0.01:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(ry), fig.rad(
        c[0], c[1], r, ry, [(0, color, op), (0.45, color, op * 0.4), (1, color, 0)]))


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
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
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def lens_pts(C, R, a0, a1, w, ry=None, n=28):
    """Un croissant effilé aux DEUX bouts le long d'un arc d'ellipse (anneau, onde, traînée)."""
    k = 1.0 if ry is None else ry / R
    pts = [(C[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + k * R * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    ws = [max(0.05, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]
    return pts, ws


def crescent(C, R, a0, a1, w, n=30):
    """Un croissant le long d'un arc : fin au départ (a0), plein vers a1, la pointe qui s'arrondit au bout."""
    pts = [(C[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + R * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    ws = [max(0.05, w * (i / n) ** 1.2 * (1 - 0.6 * max(0, (i / n - 0.85) / 0.15) ** 2)) for i in range(n + 1)]
    ws[-1] = 0.05
    return pts, ws


def pop(fig, c, r, facing=0.0, op=1.0):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté visé."""
    if op <= 0.02 or r < 0.3:
        return ''
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.92 * op), (0.3, WIND[1], 0.65 * op), (0.65, WIND[3], 0.25 * op), (1, WIND[4], 0)]))
    pts, ws = lens_pts(c, r * 1.3, facing - 70, facing + 70, r * 0.55)
    out += outlined([(stroke_shape(pts, ws), WIND[1], 1)], w=1.0, op=op * 0.9)
    return out


def puff(fig, cx, cy, r, op=1.0, k=0, dust=False):
    """Une bouffée (de vent, ou de poussière) : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = [(0, 0, 1), (0.8, 0.3, 0.72), (-0.82, 0.28, 0.7), (0.2, -0.55, 0.62), (-0.35, -0.35, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in j[:4 + (k % 2)]]
    tones = ('#f6e4c0', '#d6b68a', '#a07c64') if dust else (WIND[0], WIND[1], WIND[2])
    ink = '#5a3a3a' if dust else WINK
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def sparkle(fig, c, r, op=1.0, rot=0.0, tones=None):
    """Un éclat : une étoile à quatre branches inégales aux flancs courbes (blanc au cœur)."""
    if r < 0.2 or op <= 0.02:
        return ''
    tones = tones or (GOLDFX[0], GOLDFX[1])
    pts = []
    arms = (1.0, 0.5, 0.8, 0.45)
    for i in range(4):
        a = math.radians(rot + 90 * i - 90)
        pts.append((c[0] + r * arms[i] * math.cos(a), c[1] + r * arms[i] * math.sin(a)))
        b = math.radians(rot + 90 * i - 45)
        pts.append((c[0] + r * 0.2 * math.cos(b), c[1] + r * 0.2 * math.sin(b)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.9)
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.4, tones[0]), (1, tones[1])])
    return glow(fig, c, r * 1.2, tones[1], 0.35 * op) + '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op)


def plume(fig, c, ang, s=1.0, op=1.0):
    """Une plume d'air : vexille en amande courbe, rachis clair, un seul contour (jade sombre)."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (c[0] + s * (u[0] * i + v[0] * j), c[1] + s * (u[1] * i + v[1] * j))
    body = sm([P(-2.6, 0.1), P(-1.0, -0.9), P(1.2, -0.95), P(2.8, -0.2), P(1.6, 0.85), P(-0.8, 0.9)], sharp=(0, 3), t=0.9)
    quill = ribbon([P(-3.4, 0.25), P(-0.6, 0.05), P(2.4, -0.25)], [0.15 * s, 0.32 * s, 0.08])
    gr = g_lin(fig, P(2, -1), P(-2, 1), [(0, '#ffffff'), (0.5, WIND[1]), (1, WIND[3])])
    return outlined([(body, gr, 1), (quill, '#ffffff', 0.9)], ink=WINK, w=0.9, op=op)


def mote(fig, c, r, op=1.0):
    """Un grain de lumière (le soin) : un point blanc au halo cyan pâle."""
    if op <= 0.02:
        return ''
    return glow(fig, c, r * 2.6, WIND[2], 0.5 * op) + '<circle cx="%s" cy="%s" r="%s" fill="#ffffff" opacity="%g"/>' % (
        fm(c[0]), fm(c[1]), fm(r), op)


# ---- 2) l'attaque : la fauche

_HIT = {}


def fx_attack(tl):
    def f(fig, ctx):
        G, ang, tip = ctx['G'], ctx['ang'], ctx['tip']
        # le croissant de vent qui suit le fer (autour du poing), de l'angle d'il y a un instant jusqu'à la lance
        if ATT_SWING[0] + 20 <= tl <= ATT_HIT + 90:
            prev = keyed(ATTACK, max(0, tl - 70))['ang']
            k = env(tl, ATT_SWING[0] + 20, ATT_SWING[0] + 50, ATT_HIT - 10, ATT_HIT + 90)
            R = M.S_TIP + ctx['P']['stretch'] - 1.0
            a1 = ang
            a0 = prev + ctx['P']['lean']
            if a1 - a0 > 4:
                pts, ws = crescent(G, R, a0, a1, 6.5 * k)
                inner, wi = crescent(G, R - 1.0, a0 + (a1 - a0) * 0.3, a1, 2.4 * k)
                gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[4]), (0.5, WIND[2]), (1, WIND[0])])
                el = outlined([(stroke_shape(pts, ws), gr, 1), (stroke_shape(inner, wi), '#ffffff', 0.85)], w=1.1, op=0.95 * k)
                if ctx['P']['behind']:
                    fig.fx_back.append(el)
                else:
                    fig.fx_front.append(el)
        if tl < ATT_HIT - 5:
            return
        if 'T' not in _HIT or tl < ATT_HIT + 20:
            _HIT['T'] = tip
        T = _HIT['T']
        u = (tl - ATT_HIT) / 420.0
        k = env(tl, ATT_HIT - 5, ATT_HIT + 25, ATT_HIT + 90, ATT_HIT + 260)
        fig.fx_front.append(pop(fig, add(T, (2, 0)), 6.2 * (0.7 + 0.5 * k), facing=0, op=k))
        ko = 1 - smooth((tl - ATT_HIT - 200) / 260)
        if ko > 0.02:
            g = smooth(min(1.0, u * 1.8))
            # la virgule d'air qui continue l'arc vers le bas, devant
            q0 = add(T, (-10, -8))
            fig.fx_back.append(gust(fig, q0, add(q0, (8, -4)), add(T, (8, 2)), add(T, (6 + 4 * g, 10 + 2 * g)), 3.2,
                                    curl=3.4 * g + 0.6, s=1, tail=0.5 * u, op=ko))
            # deux volutes qui s'ouvrent (haut et bas)
            for s_, dy in ((-1, -1), (1, 1)):
                p0 = add(T, (2, 2 * dy))
                fig.fx_front.append(gust(fig, p0, add(p0, (5 * g, 7 * dy * g)), add(p0, (11 * g, 10 * dy * g)),
                                         add(p0, (15 * g, 5 * dy * g)), 2.4, curl=3.2 * g + 0.5, s=s_, tail=0.35 * u, op=ko))
            for j, (dx, dy, r) in enumerate(((7, -9, 2.8), (11, 6, 2.6), (2, 11, 2.2))):
                fig.fx_front.append(puff(fig, T[0] + dx * (0.5 + 0.7 * g), T[1] + dy * (0.5 + 0.7 * g) - 3 * u,
                                         r * (0.6 + 0.6 * g) * (1 - 0.4 * u), op=ko * 0.9, k=j))
            for j, (dx, dy, a0) in enumerate(((6, -13, -30), (19, -1, 40))):
                fp = add(T, (dx + 10 * u, dy - 6 * u + 14 * u * u))
                fig.fx_front.append(plume(fig, fp, a0 + 150 * u * (1 if j else -1), 1.0, op=ko))
    return f


# ---- 3) la spéciale

def ring_pts(c, rx, ry, a0, a1, n=40):
    return [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def wind_wing_state(k):
    """Les ailes de vent : 1 naissantes (à demi ouvertes derrière l'épaule), 2 grandes ouvertes et levées, 3 battues
    (abattues d'un coup) ; entre deux, un mélange. Repère du dessin, l'aile PROCHE (à gauche)."""
    S = {
        1: dict(R=(52.0, 56.0), W=(38.0, 36.0), T=(27.0, 23.0), a0=100, a1=150, l0=18, l1=20),
        2: dict(R=(52.0, 55.0), W=(31.0, 27.0), T=(8.0, 5.0), a0=104, a1=186, l0=26, l1=31),
        3: dict(R=(52.0, 56.0), W=(30.0, 48.0), T=(6.0, 62.0), a0=92, a1=138, l0=22, l1=23),
    }
    k = max(1.0, min(3.0, k))
    i = min(2, int(k))
    t = k - i
    a, b = S[i], S[i + 1] if i < 3 else S[3]
    out = {}
    for key in a:
        if isinstance(a[key], tuple):
            out[key] = lerp(a[key], b[key], t)
        else:
            out[key] = a[key] + (b[key] - a[key]) * t
    return out


def wind_wing(fig, st, M_, op, far=False, ph=0.0):
    """Une grande aile de VENT (sans contour noir, un liseré jade) : le bord d'attaque R → W → T, sept plumes d'air
    en feuilles qui en pendent, en éventail. M_ : un point de l'aile proche → le dessin (miroir pour la lointaine)."""
    if op <= 0.02:
        return ''
    R, W, T = st['R'], st['W'], st['T']
    edge = resample(bez(R, lerp(R, W, 0.6), lerp(W, T, 0.3), T, 30), 30)
    shapes = []
    n = 7
    for i in range(n):
        s = 0.3 + 0.7 * i / (n - 1)
        p = edge[int(s * 30)]
        a = st['a0'] + (st['a1'] - st['a0']) * i / (n - 1) + 3 * math.sin(ph + i * 0.9)
        ln = st['l0'] + (st['l1'] - st['l0']) * i / (n - 1)
        tip = add(p, unit(a), ln)
        sh = leaf(M_(p), M_(tip), 7.5, bend=1.4 * (-1 if far else 1), root=0.8, belly=1.05)
        gr = g_lin(fig, M_(p), M_(tip), [(0, WIND[1]), (0.55, WIND[2] if not far else WIND[3]), (1, WIND[3] if not far else WIND[4])])
        shapes.append((sh, gr, 0.92))
    # le bord d'attaque (les couvertures) : un ruban plein, plus large au poignet
    ws = [max(0.3, 7.0 * math.sin(math.pi * min(1, 0.15 + 0.85 * i / 30)) ** 0.6 * (1 - 0.5 * i / 30)) for i in range(31)]
    band = stroke_shape([M_(p) for p in edge], ws)
    gr = g_lin(fig, M_(R), M_(T), [(0, '#ffffff'), (0.6, WIND[1]), (1, WIND[2])])
    shapes.append((band, gr, 0.95))
    shapes.append((stroke_shape([M_(add(p, (0.6, -1.0))) for p in edge[2:-2]], [max(0.05, x * 0.3) for x in ws[2:-2]]), '#ffffff', 0.9))
    return outlined(shapes, ink=WIND[5], w=1.0, op=op)


def feather_ring(fig, c, rx, ry, ph, op, back, n=16, s=1.0):
    """L'anneau de plumes de vent autour d'elle (à plat : une ellipse). Sa moitié du fond passe derrière elle, celle de
    devant devant ; les plumes tournent le long de l'anneau."""
    if op <= 0.02:
        return ''
    shapes = []
    for i in range(n):
        th = ph + 2 * math.pi * i / n
        sn = math.sin(th)
        if (sn < 0) != back:
            continue
        p = (c[0] + rx * math.cos(th), c[1] + ry * sn)
        d = norm((-rx * math.sin(th), ry * math.cos(th)))
        L = (4.2 + 1.4 * (sn + 1) / 2) * s
        sh = leaf(add(p, d, -L * 0.5), add(p, d, L * 0.6), 3.4 * s * (0.8 + 0.25 * (sn + 1) / 2), bend=0.8)
        tone = (WIND[1], WIND[3]) if not back else (WIND[2], WIND[4])
        shapes.append((sh, g_lin(fig, add(p, (2, -2)), add(p, (-2, 2)), [(0, '#ffffff'), (0.5, tone[0]), (1, tone[1])]), 1))
    # le ruban d'air qui les porte
    a0, a1 = (190, 350) if back else (10, 170)
    pts = ring_pts(c, rx, ry, a0, a1, 36)
    ws = [max(0.05, 2.2 * s * math.sin(math.pi * i / 36) ** 0.6) for i in range(37)]
    band = stroke_shape(pts, ws)
    out = outlined([(band, g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])]), 0.9)], w=0.9, op=op * (0.7 if back else 0.95))
    out += outlined(shapes, w=0.9, op=op * (0.8 if back else 1))
    return out


def ring_arcs(fig, c, rx, ry, w, op, back, gaps=0.0, ph=0.0):
    """L'anneau qui s'élargit en descendant : un ruban effilé aux bouts, qui se défait en arcs (gaps 0..1)."""
    if op <= 0.02:
        return ''
    out = ''
    a0, a1 = (190, 350) if back else (10, 170)
    nseg = 1 if gaps < 0.05 else 3
    span = (a1 - a0) / nseg
    for j in range(nseg):
        s0 = a0 + j * span + span * gaps * 0.3 + 8 * math.sin(ph + j)
        s1 = a0 + (j + 1) * span - span * gaps * 0.3 + 8 * math.sin(ph + j)
        pts = ring_pts(c, rx, ry, s0, s1, 24)
        ws = [max(0.05, w * math.sin(math.pi * i / 24) ** 0.6) for i in range(25)]
        body = stroke_shape(pts, ws)
        core = stroke_shape([(x, y - 0.25 * w) for x, y in pts], [x * 0.38 for x in ws])
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
        out += outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=op * (0.75 if back else 1))
    return out


ARMOR = [  # où se posent les plumes de vent sur elle (repère : ce qui bouge avec elle), angle, taille
    ('UC', (55.0, 52.0), -30, 1.15), ('TOR', (80.0, 58.0), -15, 1.0), ('U', (55.0, 79.0), 20, 0.95),
    ('UC', (40.0, 78.0), 70, 1.1), ('TOR', (68.0, 64.0), 10, 0.9)]


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        lift = P['lift']
        # 1) la lance sonne sur le bord du bouclier : un éclat d'or, une onde qui part du bord
        k = env(tl, SP_CLANG - 10, SP_CLANG + 10, SP_CLANG + 50, SP_CLANG + 220)
        if k > 0:
            rim = ctx['rim']
            u = (tl - SP_CLANG) / 220
            fig.fx_front.append(sparkle(fig, rim, 4.4 * k, k, rot=12))
            for j in range(2):
                uu = max(0.0, u - 0.25 * j)
                if uu > 0:
                    pts, ws = lens_pts(rim, 4 + 16 * uu, 205 + 10 * j, 300 + 10 * j, 1.5 * (1 - uu))
                    fig.fx_front.append(outlined([(stroke_shape(pts, ws), GOLDFX[1], 1)], ink='#6a3a1a', w=0.8, op=(1 - uu) * 0.9))
        # 2) le vent se lève à ses pieds (de fines rafales qui montent en spirale)
        kg = env(tl, 280, 380, 560, 680)
        if kg > 0:
            for j in range(3):
                ph = tl / 120 + j * 2.1
                x0 = 66 + 22 * math.cos(ph)
                p0 = (x0, GR - 2 - lift)
                fig.fx_back.append(gust(fig, p0, add(p0, (6 * math.sin(ph), -8)), add(p0, (-4, -18)), add(p0, (2, -26)), 2.0,
                                        curl=2.6, s=1 if j % 2 else -1, tail=0.2, op=0.8 * kg))
        # 3) les grandes ailes de vent, dans son dos
        if P['wop'] > 0.02 and P['wing'] >= 0.99:
            st = wind_wing_state(P['wing'])
            BODYm = ctx['BODY']
            Mn = lambda p: mapp(ctx['UC'], p)
            Mf = lambda p: mapp(ctx['UC'], (71.75 + (71.75 - p[0]) * 0.62, p[1] - 2.0))
            ph = tl / 90
            fig.fx_back.insert(0, wind_wing(fig, st, Mf, P['wop'] * 0.9, far=True, ph=ph))
            fig.fx_back.append(wind_wing(fig, st, Mn, P['wop'], ph=ph + 1))
            del BODYm
        # 4) le décollage : l'air chasse la poussière au sol
        kt = env(tl, 560, 620, 700, 900)
        if kt > 0:
            u = (tl - 560) / 340
            for j, (dx, r) in enumerate(((-26, 4.2), (-12, 3.4), (14, 3.6), (30, 4.4))):
                fig.fx_front.append(puff(fig, 66 + dx * (0.7 + 0.8 * u), GR - 2.0 - 4 * u, r * (0.6 + 0.6 * u), op=kt * 0.9, k=j, dust=True))
        # 5) l'anneau de plumes de vent : il se forme depuis son dos, plein (arrêt sur l'image), puis part
        c = mapp(ctx['U'], (66.0, 84.0))
        kr = env(tl, SP_RING[0], SP_RING[0] + 80, SP_LAUNCH, SP_LAUNCH + 40)
        if kr > 0:
            grow = smooth((tl - SP_RING[0]) / 80)
            ph = tl / 160
            rx, ry = 26 + 16 * grow, 6.5 + 4.0 * grow
            fig.fx_back.append(feather_ring(fig, c, rx, ry, ph, kr, True, n=18, s=1.35))
            fig.fx_front.append(feather_ring(fig, c, rx, ry, ph, kr, False, n=18, s=1.35))
            fig.fx_back.insert(0, glow(fig, c, rx + 10, WIND[2], 0.35 * kr, ry + 26))
        # l'armure de plumes : des plumes de vent se posent sur elle, brillent, puis s'en vont en lueurs
        ka = env(tl, SP_RING[0] + 80, SP_RING[0] + 160, SP_LAUNCH + 100, SP_LAUNCH + 300)
        if ka > 0:
            for j, (fr, p, a, s) in enumerate(ARMOR):
                M_ = ctx[fr]
                q = mapp(M_, p)
                arr = smooth((tl - SP_RING[0] - 80 - 25 * j) / 90)
                q = add(q, (14 * (1 - arr) * (1 if j % 2 else -1), -10 * (1 - arr)))
                fig.fx_front.append(plume(fig, q, a + 40 * (1 - arr), s, op=ka * arr))
                kk = env(tl, SP_RING[0] + 150 + 30 * j, SP_RING[0] + 180 + 30 * j, SP_RING[0] + 200 + 30 * j, SP_RING[0] + 300 + 30 * j)
                if kk > 0:
                    fig.over.append(sparkle(fig, add(q, (1.2, -1.0)), 2.2 * kk, kk, rot=10, tones=(WIND[1], WIND[2])))
        # l'aura d'air (le liseré autour d'elle) quand l'anneau est plein ; le voile d'air
        kw = env(tl, SP_RING[0] + 60, SP_RING[0] + 120, SP_LAUNCH, SP_LAUNCH + 120)
        # 6) LANCEMENT : l'anneau s'élargit dans toutes les directions en descendant jusqu'au sol, se défait en arcs
        if SP_LAUNCH - 10 <= tl <= SP_LAUNCH + 620:
            u = smooth((tl - SP_LAUNCH + 10) / 420)
            cc = lerp(c, CEN, smooth(min(1, (tl - SP_LAUNCH + 10) / 180)))
            rx, ry = 42 + 112 * u, 10.5 + 18 * u
            op = 1 - smooth((tl - SP_LAUNCH - 260) / 360)
            gaps = smooth((tl - SP_LAUNCH - 160) / 300)
            fig.fx_back.append(ring_arcs(fig, cc, rx, ry, 4.2 * (1 - 0.5 * u), op, True, gaps, tl / 200))
            fig.fx_front.append(ring_arcs(fig, cc, rx, ry, 4.2 * (1 - 0.5 * u), op, False, gaps, tl / 200))
            # quelques plumes emportées par l'anneau
            for j in range(5):
                th = math.radians(30 + 72 * j + 10 * math.sin(j))
                q = (cc[0] + rx * 0.92 * math.cos(th), cc[1] + ry * 0.92 * math.sin(th) - 6 * u)
                fig.fx_front.append(plume(fig, q, 40 * j + 220 * u, 0.9, op=op * 0.9))
        # 7) le souffle qui soigne : des grains de lumière montent en spirale autour d'elle, sa silhouette s'éclaire
        kh = env(tl, SP_HEAL[0] - 20, SP_HEAL[0] + 90, SP_HEAL[1] - 120, SP_HEAL[1] + 160)
        if kh > 0:
            ch = mapp(ctx['U'], (68.0, 80.0))
            for j in range(9):
                t_ = ((tl - SP_HEAL[0]) / 520 + j / 9) % 1.0
                th = 2 * math.pi * (t_ * 1.4 + j * 0.37)
                q = (ch[0] + (20 - 8 * t_) * math.cos(th), ch[1] + 24 - 70 * t_ + 4 * math.sin(th))
                front = math.sin(th) > 0
                el = mote(fig, q, 0.8 + 0.5 * (1 - t_), kh * (1 - t_ ** 3))
                (fig.fx_front if front else fig.fx_back).append(el)
            p0 = (ch[0] - 20, ch[1] + 26)
            fig.fx_back.append(gust(fig, p0, add(p0, (40, -6)), add(p0, (44, -30)), add(p0, (14, -44)), 2.2, curl=3.0, s=-1,
                                    tail=smooth((tl - SP_HEAL[0]) / 400) * 0.6, op=0.8 * kh))
        # 8) le défi : la lueur rouge douce qui gonfle puis s'éteint (aucun trait, aucun anneau)
        kd = env(tl, SP_DEFI[0], SP_DEFI[0] + 60, SP_DEFI[0] + 280, SP_DEFI[1])
        sw = smooth((tl - SP_DEFI[0]) / 330)
        red = []
        if kd > 0:
            red = [(REDS, (1.0 + 2.2 * sw) * q, 0.075 * kd) for q in (3.6, 3.0, 2.5, 2.0, 1.6, 1.25, 0.95, 0.7)]
            fig.fx_back.insert(0, glow(fig, ctx['chest'], 40 + 12 * sw, REDS, 0.22 * kd, 52 + 12 * sw))
        auras = []
        if kw > 0:
            auras += [(WIND[2], q, 0.12 * kw) for q in (4.0, 3.0, 2.2, 1.5, 1.0)]
        if kh > 0:
            auras += [(WIND[1], q, 0.13 * kh) for q in (4.4, 3.2, 2.3, 1.6, 1.0)]
        fig.auras = auras + red
        veil = max(0.12 * kw, 0.22 * env(tl, SP_HEAL[0] + 40, SP_HEAL[0] + 120, SP_HEAL[0] + 180, SP_HEAL[1]))
        if veil > 0.01:
            fig.veil = ('#e6fcff', veil)
        if P['glow'] > 0.3:
            fig.fx_back.insert(0, glow(fig, ctx['shield'], 10 + 4 * P['glow'], GOLDFX[1], 0.25 * P['glow']))
    return f


def fx_glints(T):
    """Au repos, un éclat court sur l'acier et l'or (casque, umbo, fer)."""
    def f(fig, ctx):
        t = T % 3.2
        spots = [
            (0.2, lambda: mapp(ctx['HEAD'], (86.4, 25.0))),       # le casque
            (1.4, lambda: add(ctx['shield'], (1.4, -1.4))),       # l'umbo
            (2.4, lambda: ctx['tip']),                             # le fer
        ]
        for t0, pos in spots:
            k = env(t, t0, t0 + 0.1, t0 + 0.14, t0 + 0.3)
            if k > 0:
                fig.over.append(sparkle(fig, pos(), 2.2 * k, k, rot=8))
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


def shadow_layer(w, h, view, lift=0.0, floor_y=GR):
    """L'ombre au sol sous elle (elle rétrécit quand elle s'élève)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (67 - x0) * k
    s = max(0.5, 1 - lift / 50)
    ImageDraw.Draw(sh).ellipse([cx - 31 * k * s, fy - 3.0 * k * s, cx + 31 * k * s, fy + 3.0 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    a = ATTACK[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', a), ('idle', 0.7), ('attack', a), ('idle', 0.9),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
    out, T = [], 0.0
    for a_, d in seq:
        out.append((a_, T, T + d))
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
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    else:
        fx = [fx_glints(T)]
    return M.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-mira-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('mira'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du vent, le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'eldra.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (150, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (M.FEET[0] - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
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


def compose(pngs, lifts, w, h, view):
    bg = background(w, h, view)
    for p, lf in zip(pngs, lifts):
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view, lf))
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
        moments = [0.8, a_s + 0.12, a_s + 0.3, a_s + 0.42, a_s + 0.46, a_s + 0.55, a_s + 0.7, a_s + 0.86,
                   s_s + 0.19, s_s + 0.5, s_s + 0.62, s_s + 0.72, s_s + 0.9, s_s + 1.07, s_s + 1.25, s_s + 1.6]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, [r[1]['lift'] for r in res], 640, 360, VIEW)
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
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r[0] for r in res], VW, VH, 'a')
    compose(pngs, [r[1]['lift'] for r in res], VW, VH, VIEW)
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
