# Garvin vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/garvin/build.py) —
# la respiration du rempart, l'attaque de base « Poing du rempart », l'attaque spéciale « Rempart en fusion » — dans
# le style lisse de l'interface (comme Kael : heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/garvin/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/garvin/)
#   python3 refonte-graphique/ui-moderne/heros/garvin/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#   (images de travail : dans $GARVIN_TMP, sinon un dossier temporaire du système ; jamais dans le dépôt)
#
# Méthode : chaque image redessine garvin.py dans une POSE (buste qui respire et se penche depuis les hanches, tête en
# retard, piliers qui plient, pieds à plat ; les deux bras suivent leur poignet par cinématique inverse et plient au
# vrai coude, le poing tourne avec l'avant-bras). C'est un rempart vivant : tout est lourd et lent — longues
# préparations, coups courts, arrêts sur l'image, retours lents ; sa lave bat comme un cœur ; il ne quitte jamais le
# sol. Poses clés et durées reprises du pixel art, reliées par des courbes douces sans dépassement, 24 images/s.
# Les effets (croissant de roche bordé de braise, dalles de basalte, fente de lave, éclats, gouttes, poussière,
# fumée, dôme de plaques, anneau de chaleur, lueur d'or du soin, lueur rouge du défi) : dégradés, un seul contour par
# objet, aucun flou ; jamais de rayons droits répétés.
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
import garvin as K  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'garvin')
TMP = os.environ.get('GARVIN_TMP') or os.path.join(tempfile.gettempdir(), 'garvin-anim')
FPS = 24
VIEW = (-26, -32, 284, 159.75)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
FINK = '#3a0c18'                     # le contour de la lave (comme Kael)
INK = '#1f1238'                      # le contour de la roche (comme le héros)
LAVA = K.LAVA
ROCK = K.ROCK
GOLD = ['#fffbe4', '#ffef9e', '#ffd860', '#f2b234']

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


PAIRS = {'head': ('headx', 'heady'), 'fw': ('fwx', 'fwy'), 'nw': ('nwx', 'nwy')}
SCAL = ['crouch', 'lean', 'tilt', 'glow', 'heat', 'gape', 'frot', 'nrot', 'ffront', 'fsw', 'heal', 'red', 'inhale']
NUM = SCAL + [k for v in PAIRS.values() for k in v]
BASE = dict(fw=K.FW0, nw=K.NW0)


def flat(k):
    d = {n: 0.0 for n in NUM}
    for key, v in dict(BASE, **k).items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Poing du rempart » (pixel : ATTAQUE, 1,9 s). Il lève le poing très haut (le buste part en arrière, il se
# grandit, la lave du bras s'allume) — longue attente — puis l'abat d'un coup devant lui, coude en l'air comme un
# gorille, et frappe le sol des phalanges : arrêt sur l'image. Il reste appuyé, puis relève lentement le poing en garde.
ATTACK = [
    (0, {}),
    (160, dict(crouch=0.8, lean=-1.0, fw=(112.0, 49.0), nw=(33.8, 88.6), glow=1.0, tilt=-1.0)),
    (520, dict(crouch=-1.0, lean=-3.0, fw=(115.0, 17.0), frot=-8, head=(-0.4, -1.0), tilt=-2.4, nw=(32.6, 88.0), glow=2.0)),
    (700, dict(crouch=-1.1, lean=-3.3, fw=(114.6, 15.6), frot=-10, head=(-0.5, -1.2), tilt=-2.8, nw=(32.4, 87.8), glow=2.2)),
    (738, dict(crouch=0.6, lean=1.2, fw=(131.0, 50.0), frot=-4, fsw=0.7, head=(0.0, 0.0), tilt=0.0, glow=2.2, gape=0.4)),
    (770, dict(crouch=3.0, lean=4.0, fw=(128.0, 89.6), frot=0, fsw=1.0, head=(0.6, 1.0), tilt=2.2, nw=(35.6, 89.6), glow=3.2, gape=1.0)),
    (1000, dict(crouch=3.0, lean=4.0, fw=(128.0, 89.8), fsw=1.0, head=(0.6, 1.1), tilt=2.2, nw=(35.6, 89.6), glow=2.6, gape=0.9)),
    (1270, dict(crouch=2.2, lean=3.0, fw=(127.0, 87.6), fsw=1.0, head=(0.4, 0.8), tilt=1.5, nw=(35.2, 89.4), glow=1.6, gape=0.3)),
    (1430, dict(crouch=1.8, lean=2.0, fw=(123.0, 74.0), fsw=0.5, glow=1.0, tilt=0.8)),
    (1600, dict(crouch=1.0, lean=1.0, fw=(117.0, 63.0), fsw=0.1, glow=0.5)),
    (1760, dict(crouch=0.4, fw=(115.6, 60.6))),
    (1920, {}),
]
ATTACK_HIT = 770          # le choc (ms)

# 3) « Rempart en fusion » (pixel : SPECIALE, 2,3 s ; sort d'équipe, rien ne part vers l'ennemi). Il se ramasse, sa
# lave monte, huit plaques de basalte s'arrachent du sol et forment un dôme autour de lui, qui chauffe au rouge puis à
# blanc. LANCEMENT (850 ms) : il se redresse d'un coup, le dôme s'ouvre, les plaques se posent debout en anneau autour
# de ses pieds, une onde de chaleur court au sol ; elles luisent puis rentrent dans le sol (fentes de lave). Le soin :
# ses fissures luisent d'or. Le défi : il écarte les bras puis frappe ses deux poings l'un contre l'autre devant sa
# poitrine (arrêt sur l'image, étincelles), une lueur rouge l'entoure, gonfle et s'éteint ; il retombe en garde.
CLASH_F = (101.0, 66.0)           # les poignets au moment du défi (repère du dessin)
CLASH_N = (64.0, 71.0)
SPECIAL = [
    (0, {}),
    (100, {}),
    (230, dict(crouch=1.0, fw=(114.0, 65.0), head=(0.0, 1.0), glow=1.0)),
    (350, dict(crouch=2.0, fw=(110.6, 68.0), head=(0.0, 1.2), glow=2.0, tilt=1.0, heat=0.2)),
    (680, dict(crouch=2.6, fw=(109.0, 69.0), head=(0.0, 1.6), glow=3.4, tilt=1.4, heat=0.7)),
    (800, dict(crouch=3.0, fw=(108.4, 70.0), head=(0.0, 2.0), glow=4.0, tilt=1.6, heat=1.0, gape=0.5)),
    (850, dict(crouch=-1.0, fw=(116.0, 51.0), frot=-8, head=(0.0, -1.2), glow=4.0, tilt=-2.0, heat=0.85, gape=1.3)),
    (1000, dict(crouch=-0.8, fw=(116.0, 52.0), frot=-8, head=(0.0, -1.0), glow=3.6, tilt=-1.8, heat=0.6, gape=1.1)),
    (1090, dict(crouch=1.6, fw=(115.8, 61.6), head=(0.0, 0.6), glow=3.0, heat=0.35, heal=1.0)),
    (1290, dict(crouch=1.0, fw=(115.4, 61.0), glow=2.2, heat=0.1, heal=1.0)),
    (1390, dict(crouch=0.6, fw=(115.2, 60.4), glow=1.4, heal=0.6)),
    (1480, dict(crouch=0.0, lean=-1.0, fw=(122.0, 50.0), frot=-10, fsw=0.3, nw=(27.0, 86.0), nrot=10, head=(0.0, -1.0), glow=1.2,
                ffront=1.0, heal=0.2)),
    (1540, dict(crouch=1.0, lean=0.0, fw=(110.0, 64.0), frot=0, fsw=1.0, nw=(52.0, 76.0), nrot=-20, glow=2.0, ffront=1.0)),
    (1580, dict(crouch=2.0, lean=1.0, fw=CLASH_F, frot=0, fsw=1.0, nw=CLASH_N, nrot=-34, head=(0.0, 1.0), glow=3.2, ffront=1.0,
                gape=0.9, red=1.0)),
    (1780, dict(crouch=2.0, lean=1.0, fw=(CLASH_F[0] + 0.3, CLASH_F[1]), frot=0, fsw=1.0, nw=(CLASH_N[0] - 0.3, CLASH_N[1]), nrot=-34,
                head=(0.0, 1.0), glow=2.4, ffront=1.0, gape=0.8, red=0.8)),
    (1890, dict(crouch=1.2, lean=1.0, fw=(108.0, 64.0), frot=0, fsw=1.0, nw=(56.0, 76.0), nrot=-20, glow=1.4, ffront=1.0, red=0.3)),
    (1990, dict(crouch=1.0, fw=(112.0, 64.0), frot=-6, nw=(38.0, 88.0), glow=0.8)),
    (2100, dict(crouch=0.4, fw=(115.0, 61.6))),
    (2300, {}),
]
SP_LAUNCH = 850
SP_CLASH = 1580


# ======================================================================== la respiration (en boucle)
IDLE = 2.33                          # un souffle (s) : le rythme lent du pixel art


def bump(x, c, w):
    return math.exp(-((x - c) / w) ** 2)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE
    ph = (T / IDLE) % 1
    br = 0.5 - 0.5 * math.cos(u)
    # la lave bat comme un cœur : « toum-TOUM » puis un long repos
    beat = 0.9 * bump(ph, 0.17, 0.035) + 1.7 * bump(ph, 0.27, 0.045)
    return dict(inhale=br, crouch=0.55 * (0.5 - 0.5 * math.cos(u - 2.7)), heady=0.4 * math.sin(u - 1.0),
                tilt=0.5 * math.sin(u - 1.2), fwy=0.7 * math.sin(u - 1.1), fwx=0.2 * math.sin(u - 1.6),
                nwy=0.3 * math.sin(u - 0.9), glow=beat, gape=0.15 + 0.15 * math.sin(u - 1.4))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
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
    P['breath'] = P.pop('inhale')
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['fw'] = (P.pop('fwx'), P.pop('fwy'))
    P['nw'] = (P.pop('nwx'), P.pop('nwy'))
    P['glow'] = max(0.0, P['glow'])
    P['heat'] = max(0.0, P['heat'])
    P['blink'] = 1.0 if (w > 0.95 and 1.55 <= (T % 4.6) < 1.65) else 0.0
    return P, tl


# ======================================================================== les effets (un seul contour, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ;
    une 4e valeur dans un élément = pas de silhouette pour lui (un reflet peint dedans)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def ember(fig, x, y, r=0.7, op=1.0, gold=False):
    if op <= 0.02:
        return ''
    C = GOLD if gold else LAVA
    glow = g_rad(fig, (x, y), r * 3.2, [(0, C[2], 0.55 * op), (1, C[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, C[0], op), (0.6, C[1], op), (1, C[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte de lave : ronde devant, effilée derrière (dans le sens de sa course)."""
    a = math.atan2(vy, vx)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.8, y - math.sin(a) * r * 2.8)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.35, r * 0.25), LAVA[0], 0.9, 'n')], w=1.1, op=op)


CHUNK = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]


def chunk(fig, x, y, s=1.6, rot=0.0, op=1.0, hot=False):
    """Un éclat de basalte (sa roche, éclairée en haut à droite) ; chaud : un cœur de braise."""
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in CHUNK]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, '#b8aa97'), (0.5, ROCK.base), (1, ROCK.deep)])
    items = [(sh, gr, 1)]
    if hot:
        items.append((ellipse(x - 0.15 * s, y + 0.2 * s, 0.45 * s, 0.35 * s), LAVA[2], 1, 'n'))
    return outlined(items, ink=INK, w=1.0, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite (comme Kael)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def dust(fig, cx, cy, r, op=1.0):
    """Un nuage de poussière de terre, posé au sol."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy - 0.4 * r, r), (cx + 0.9 * r, cy, 0.7 * r), (cx - 0.9 * r, cy + 0.1 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e2c4'), (0.55, '#cdb08e'), (1, '#8e7468')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4e3a48" stroke="#4e3a48" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


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


def rock_smear(fig, C, R, a0, a1, w, op=1.0):
    """La traînée du poing qui s'abat : un croissant de roche (gris), bordé de braise du côté du mouvement."""
    if abs(a1 - a0) < 4 or w < 0.4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + w * 0.5, a0, a1, w)
    rim = arc_band(C, R + w * 0.5, a0 + (a1 - a0) * 0.35, a1, w * 0.3)
    g1 = g_lin(fig, pa, pb, [(0, '#6a5e6c', 0.0), (0.5, '#8e8284', 0.7), (1, '#b8aa97', 0.95)])
    g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0.0), (0.6, LAVA[3], 0.9), (1, LAVA[1], 1)])
    return '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (op, body.d(), g1, rim.d(), g2)


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


def heat_cols(h):
    """La couleur d'une plaque qui chauffe : roche (0) → rouge (0,5) → blanc-jaune (1)."""
    if h < 0.02:
        return ['#b8aa97', ROCK.base, ROCK.deep]
    if h < 0.6:
        k = h / 0.6
        return [mix('#b8aa97', '#e8865a', k), mix(ROCK.base, '#8e3a34', k), mix(ROCK.deep, '#4a1420', k)]
    k = (h - 0.6) / 0.4
    return [mix('#ffb43a', '#fffbe4', k), mix('#cc3a12', '#ffb43a', k), mix('#6a1414', '#cc3a12', k)]


def mix(a, b, t):
    a = a.lstrip('#')
    b = b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(ca, cb))


def slab(fig, bx, w, h, tilt=0.0, heat=0.0, seed=0, op=1.0, by=None):
    """Une dalle de basalte qui se dresse du sol (base au sol, haut penché de `tilt`), une face éclairée, la braise
    au pied."""
    if h < 0.5 or op <= 0.02:
        return ''
    by = GR + 0.6 if by is None else by
    j = [0.0, 0.8, -0.6, 0.5][seed % 4]
    pts = [(bx - w / 2, by), (bx - w / 2 * 0.86 + tilt * h * 0.9, by - h * 0.82 + j), (bx - w * 0.1 + tilt * h, by - h),
           (bx + w / 2 * 0.8 + tilt * h * 0.95, by - h * 0.9 - j), (bx + w / 2, by)]
    sh = K.rk(pts, [0.3, 1.0, 1.2, 1.0, 0.3])
    c = heat_cols(heat)
    gr = g_lin(fig, (bx + w / 2 + tilt * h, by - h), (bx - w / 2, by), [(0, c[0]), (0.5, c[1]), (1, c[2])])
    face = K.rk([(bx - w * 0.1 + tilt * h, by - h + 0.4), (bx + w / 2 * 0.78 + tilt * h * 0.95, by - h * 0.9 - j + 0.4),
                 (bx + w / 2 - 0.4, by - 0.4), (bx + w * 0.12 + tilt * h * 0.3, by - h * 0.3)], 0.6)
    items = [(sh, gr, 1), (face, c[0], 0.5, 'n')]
    items.append((ribbon([(bx - w / 2 + 0.5, by - 0.6), (bx, by - 1.0 - 0.1 * h), (bx + w / 2 - 0.5, by - 0.6)], [0.2, 1.4, 0.2]), LAVA[2], 0.85, 'n'))
    return outlined(items, ink=INK, w=1.6, op=op)


def plate(fig, c, ang, L, T, heat=0.0, seed=0, op=1.0):
    """Une plaque de basalte du dôme : un éclat long et épais, irrégulier, qui chauffe au rouge puis à blanc."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    jit = [(0.0, 0.1), (0.1, -0.15), (-0.12, 0.05), (0.08, 0.12)][seed % 4]
    base = [(-0.5, -0.36 + jit[0]), (-0.05, -0.5), (0.42, -0.44 + jit[1]), (0.5, 0.06), (0.36, 0.5), (-0.2, 0.46 + jit[0]),
            (-0.48, 0.2)]
    pts = [(c[0] + L * x * ca - T * y * sa, c[1] + L * x * sa + T * y * ca) for x, y in base]
    sh = K.rk(pts, 0.8)
    col = heat_cols(heat)
    top = (c[0] + 0.5 * L * ca + 0.5 * T * sa, c[1] + 0.5 * L * sa - 0.5 * T * ca)
    gr = g_lin(fig, (c[0] + 6, c[1] - 6), (c[0] - 6, c[1] + 6), [(0, col[0]), (0.5, col[1]), (1, col[2])])
    face = [(c[0] + L * x * ca - T * y * sa, c[1] + L * x * sa + T * y * ca) for x, y in
            [(-0.36, -0.3), (0.28, -0.36), (0.42, -0.12), (-0.3, -0.04)]]
    items = [(sh, gr, 1), (K.rk(face, 0.6), col[0], 0.55, 'n')]
    if heat > 0.1:
        items.append((ribbon([(c[0] - 0.3 * L * ca, c[1] - 0.3 * L * sa), c, (c[0] + 0.3 * L * ca, c[1] + 0.3 * L * sa)],
                             [0.2, 1.2 + 1.2 * heat, 0.2]), LAVA[1] if heat > 0.6 else LAVA[2], min(1, heat * 1.6), 'n'))
    return outlined(items, ink=INK if heat < 0.5 else FINK, w=1.5, op=op)


def ground_crack(fig, x0, x1, heat, seed=0, w=1.0):
    """La fente de lave qui court au sol (elle refroidit : heat 1 → 0) ; une lueur sur le sol autour."""
    if x1 - x0 < 1 or heat <= 0.02:
        return ''
    n = max(3, int((x1 - x0) / 5))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.6 + (0.9 if (i + seed) % 2 else -0.3) * (0 < i < n)) for i in range(n + 1)]
    halo = ribbon(pts, [0.4] + [5.0 * w] * (n - 1) + [0.4])
    core = K.cribbon(pts, [0.2] + [1.6 * w] * (n - 1) + [0.2])
    hot = K.cribbon(pts, [0.1] + [0.7 * w] * (n - 1) + [0.1])
    gh = g_lin(fig, (x0, GR), (x1, GR), [(0, LAVA[2], 0.45 * heat), (1, LAVA[3], 0.12 * heat)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        halo.d(), gh, core.d(), LAVA[4], min(1, heat * 1.3), hot.d(), LAVA[1] if heat > 0.5 else LAVA[2], min(1, heat * 1.1))


def ring_band(fig, cx, cy, rx, ry, w, op=1.0, gold=False):
    """Une onde au sol : une ellipse creuse (dégradé de lave ou d'or), sans contour."""
    if op <= 0.02 or rx < 1:
        return ''
    outer = ellipse(cx, cy, rx, ry)
    inner = ellipse(cx, cy - w * 0.15, max(0.1, rx - w), max(0.1, ry - w * 0.3))
    sh = outer.hole(inner)
    C = GOLD if gold else LAVA
    gr = fig.rad(cx, cy, rx, ry, [(0, C[1], 0), (max(0.01, 1 - w / rx * 1.4), C[2], 0.2 * op), (1, C[1], 0.9 * op)])
    return '<path d="%s" fill="%s" fill-rule="evenodd"/>' % (sh.d(), gr)


def halo_sil(fig, color, op, widths=(6.0, 3.2)):
    """Une lueur douce autour de toute sa silhouette (sans flou) : la silhouette tracée large, en deux marches."""
    if op <= 0.02:
        return ''
    paths = []
    for p in fig.parts:
        tf = '' if p.M == K.mT(0, 0) else ' transform="matrix(%s)"' % ' '.join(fm(v) for v in p.M)
        paths.append((p.shape.d(), tf))
    out = ''
    for wd, o in ((widths[0], 0.22), (widths[1], 0.4)):
        out += '<g opacity="%g">%s</g>' % (o * op, ''.join(
            '<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (d, tf, color, color, fm(2 * wd)) for d, tf in paths))
    return out


def fist_points(ctx):
    W, a = ctx['far']['W'], math.radians(ctx['far']['ang'])
    return (W[0] + 10 * math.cos(a), W[1] + 10 * math.sin(a)), (W[0] + 20.4 * math.cos(a), W[1] + 20.4 * math.sin(a))


# ---- la respiration : fumée qui monte des épaules, braises des fêlures, un gravier qui tombe

def fx_idle(T, w):
    def f(fig, ctx):
        if w <= 0.02:
            return
        ph = (T / IDLE) % 1
        # deux filets de fumée qui montent des fêlures des épaules et se défont
        for (base, off) in ((ctx['shN'], 0.0), (ctx['shF'], 0.5)):
            k = (ph + off) % 1
            fig.fx_back.append(smoke(fig, base[0] + 2 * math.sin(k * 5 + off * 3), base[1] + 2 - 16 * k, 1.0 + 2.2 * k,
                                     op=w * 0.55 * env(k, 0, 0.15, 0.55, 1.0)))
        # des braises qui sortent des fêlures (épaule, bouche) et refroidissent en montant
        for i, (src, born, side) in enumerate(((ctx['shN'], 0.12, -1), (ctx['mouth'], 0.42, 1), (ctx['shF'], 0.7, 1), (ctx['chest'], 0.9, -1))):
            k = (ph - born) % 1
            if k < 0.45:
                kk = k / 0.45
                fig.fx_front.append(ember(fig, src[0] + side * 3 * kk + 0.8 * math.sin(kk * 9), src[1] + 4 - 14 * kk - 4 * kk * kk,
                                          0.55, op=w * (1 - kk)))
        # un gravier se détache sous le coude proche et tombe au sol
        k = (T / (2 * IDLE)) % 1
        if k < 0.3:
            kk = k / 0.3
            E = ctx['near']['E']
            y = E[1] + 6 + (GR - 1.5 - E[1] - 6) * kk * kk
            fig.fx_front.append(chunk(fig, E[0] - 2 + 2 * kk, min(GR - 1.2, y), 1.0, rot=kk * 300, op=w * (1 if kk < 0.9 else (1 - kk) * 10)))
    return f


# ---- l'attaque de base

HIT = {}
SLAM_CHUNKS = [(55, -120, 1.8, False), (95, -85, 1.5, True), (-35, -110, 1.6, False), (120, -55, 1.3, False),
               (25, -150, 1.2, True), (-60, -70, 1.3, False), (75, -135, 1.1, False)]
SLAM_DROPS = [(40, -150), (80, -110), (-20, -140), (110, -90), (-50, -100), (60, -170)]


def fx_attack(tl, prev):
    def f(fig, ctx):
        P = ctx['P']
        C, tip = fist_points(ctx)
        S = ctx['far']['S']
        # la traînée du poing qui s'abat (croissant de roche bordé de braise)
        if 700 < tl < 800 and prev:
            R = math.dist(S, C)
            a1 = math.degrees(math.atan2(C[1] - S[1], C[0] - S[0]))
            p0 = prev[0]
            a0 = math.degrees(math.atan2(p0[1] - S[1], p0[0] - S[0]))
            fig.fx_back.append(rock_smear(fig, S, R, a0, a1, 15, op=env(tl, 700, 725, 770, 800)))
        if tl >= ATTACK_HIT and 'c' not in HIT:
            HIT['c'] = (tip[0], GR)
        if 'c' not in HIT:
            return
        c = HIT['c']
        tau = (tl - ATTACK_HIT) / 1000.0
        # l'éclair du choc (arrêt sur l'image)
        fl = env(tl, ATTACK_HIT - 5, ATTACK_HIT + 10, ATTACK_HIT + 60, ATTACK_HIT + 200)
        if fl > 0:
            fig.fx_back.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1] - 4), fm(46), g_rad(
                fig, (c[0], c[1] - 4), 46, [(0, '#fffbe4', 0.85 * fl), (0.15, '#ffe68a', 0.5 * fl), (0.5, '#ffb43a', 0.15 * fl), (1, '#ff7a1e', 0)])))
        # la fente de lave qui court vers l'ennemi, puis refroidit
        run = min(1.0, max(0.0, (tl - ATTACK_HIT) / 160.0))
        heat = env(tl, ATTACK_HIT, ATTACK_HIT + 40, ATTACK_HIT + 420, ATTACK_HIT + 1100)
        fig.fx_back.append(ground_crack(fig, c[0] - 6, c[0] + 4 + 58 * (1 - (1 - run) ** 2), heat, 1, 1.0))
        # deux dalles de basalte se dressent de part et d'autre du poing, puis se rassoient
        hs = env(tl, ATTACK_HIT, ATTACK_HIT + 70, ATTACK_HIT + 360, ATTACK_HIT + 900)
        if hs > 0:
            fig.fx_back.append(slab(fig, c[0] - 11, 10, 16 * hs, -0.38, 0.0, 0))
            fig.fx_back.append(slab(fig, c[0] + 12, 11, 18 * hs, 0.42, 0.0, 1))
        # éclats de roche et gouttes de lave en cloche
        if tau < 0.9:
            for i, (vx, vy, s, hot) in enumerate(SLAM_CHUNKS):
                x, y = ballistic((c[0] + 2, c[1] - 3), (vx, vy), 340, tau)
                if y < GR - 0.8:
                    fig.fx_front.append(chunk(fig, x, y, s, rot=tau * 520 + i * 70, hot=hot))
            for i, (vx, vy) in enumerate(SLAM_DROPS):
                tt = tau - 0.02 * (i % 3)
                if 0 <= tt < 0.8:
                    x, y = ballistic((c[0] + 1, c[1] - 3), (vx, vy), 360, tt)
                    if y < GR - 0.5:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 360 * tt, 0.9 if i % 2 else 1.2))
        # la poussière roule au ras du sol, des deux côtés
        if 0 < tau < 1.0:
            k = tau / 1.0
            o = env(k, 0, 0.12, 0.45, 1.0)
            for j, (dx, rr) in enumerate(((-1, 3.6), (1, 4.2), (1, 2.8), (-1, 2.6))):
                sp = 26 if j < 2 else 40
                fig.fx_front.append(dust(fig, c[0] + dx * (6 + sp * (1 - (1 - k) ** 2)), GR - rr * 0.5, rr * (0.7 + 0.6 * k), op=0.9 * o))
        # la fente fume en refroidissant
        sk = (tl - ATTACK_HIT - 250) / 1000.0
        if 0 < sk < 1.0:
            o = env(sk, 0, 0.2, 0.5, 1.0)
            for j, (dx, rr, sp) in enumerate(((8, 2.6, 18), (24, 2.2, 14), (40, 1.8, 12))):
                fig.fx_back.append(smoke(fig, c[0] + dx + 3 * sk, GR - 3 - sp * sk, rr * (0.8 + 0.8 * sk), op=0.7 * o))
    return f


# ---- l'attaque spéciale

DOME_C = (66.0, GR)                  # le dôme : une demi-ellipse autour de lui
DOME_R = (70.0, 108.0)
NPL = 8
RING_C = (66.0, GR)                  # l'anneau au sol (90° = derrière lui, 270° = devant)
RING_R = (66.0, 9.0)
RING_A = [247.5, 202.5, 157.5, 112.5, 67.5, 22.5, 337.5, 292.5]


def dome_pt(i):
    a = math.radians(180 - (i + 0.5) * 180 / NPL)
    p = (DOME_C[0] + DOME_R[0] * math.cos(a), DOME_C[1] - DOME_R[1] * math.sin(a))
    tg = (-DOME_R[0] * math.sin(a), -DOME_R[1] * math.cos(a))
    return p, math.degrees(math.atan2(-tg[1], -tg[0])) % 180 - (0 if True else 0)


def ring_pt(th, r=1.0):
    a = math.radians(th)
    return (RING_C[0] + RING_R[0] * r * math.cos(a), RING_C[1] - RING_R[1] * r * math.sin(a))


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        heat = P['heat']
        # la lave monte : le sol rougeoie sous ses pieds
        gg = env(t, 150, 450, 900, 1300)
        if gg > 0:
            fig.under.append((64, GR - 2, 48 + 10 * gg, 10, '#ff7a1e', 0.35 * gg, None))
            fig.fx_back.append(ground_crack(fig, 22, 108, gg * 0.7, 2, 0.8))
        # le dôme : les plaques s'arrachent du sol et montent en arc autour de lui ; les joints se remplissent de lave
        if 200 <= t < SP_LAUNCH:
            ready = []
            for i in range(NPL):
                rank = abs(i - 3.5)                       # les plaques du bas partent les premières
                st = 230 + 45 * (3.5 - rank)
                p = max(0.0, min(1.0, (t - st) / 260.0))
                p = p * p * (3 - 2 * p)
                (dx, dy), ang = dome_pt(i)
                x0 = DOME_C[0] + DOME_R[0] * 1.08 * math.cos(math.radians(180 - (i + 0.5) * 180 / NPL))
                start = (x0, GR + 1.5)
                hump = 10 * math.sin(math.pi * p)
                out = (dx - DOME_C[0], dy - DOME_C[1])
                L_ = math.hypot(*out) or 1
                pos = (start[0] + (dx - start[0]) * p + out[0] / L_ * hump, start[1] + (dy - start[1]) * p + out[1] / L_ * hump)
                a = (90 if i < NPL / 2 else -90) * (1 - p) + ang * p
                if p > 0:
                    ready.append((pos, a, p))
                if 0 < p < 0.35:
                    fig.fx_back.append(dust(fig, start[0], GR - 1.5, 2.0 + 3 * p, op=1 - p / 0.35))
            mort = env(t, 420, 560, 850, 900)
            if mort > 0:
                a0, a1 = 180, 0
                pts = []
                for k in range(41):
                    a = math.radians(a0 + (a1 - a0) * k / 40)
                    pts.append((DOME_C[0] + DOME_R[0] * math.cos(a), DOME_C[1] - DOME_R[1] * math.sin(a)))
                band = ribbon(pts, [1.0] + [2.6 + 1.6 * heat] * 39 + [1.0])
                halo = ribbon(pts, [2.0] + [7.0 + 3.0 * heat] * 39 + [2.0])
                fig.fx_back.append('<path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
                    halo.d(), LAVA[3], 0.3 * mort, band.d(), LAVA[2] if heat < 0.7 else LAVA[1], mort))
            for i, (pos, a, p) in enumerate(ready):
                fig.fx_back.append(plate(fig, pos, a, 22, 11, heat=heat * p, seed=i))
        # LANCEMENT : l'éclair, le dôme s'ouvre, les plaques vont se poser debout en anneau autour de ses pieds
        fl = env(t, SP_LAUNCH - 10, SP_LAUNCH, SP_LAUNCH + 40, SP_LAUNCH + 200)
        if fl > 0:
            c = (66, 66)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(130), g_rad(
                fig, c, 130, [(0, '#fffbe4', 0.75 * fl), (0.2, '#ffe68a', 0.45 * fl), (0.55, '#ffb43a', 0.14 * fl), (1, '#ff7a1e', 0)])))
        if SP_LAUNCH <= t < 1700:
            # l'onde de chaleur qui court au sol en cercle
            k = (t - SP_LAUNCH) / 380.0
            if k < 1:
                fig.fx_back.append(ring_band(fig, RING_C[0], RING_C[1], 20 + 90 * k, 3 + 13 * k, 3.0 + 2 * k, op=1 - k))
            for i in range(NPL):
                (dx, dy), ang = dome_pt(i)
                th = RING_A[i]
                rp = ring_pt(th)
                front = math.sin(math.radians(th)) < 0
                depth = 1 + 0.12 * (-math.sin(math.radians(th)))
                v = max(0.0, min(1.0, (t - SP_LAUNCH - 10 * abs(i - 3.5)) / 150.0))
                if v < 1:
                    e = 1 - (1 - v) ** 2
                    out = unit2((dx - DOME_C[0], dy - (DOME_C[1] - 50)))
                    pos = (dx + (rp[0] - dx) * e + out[0] * 14 * math.sin(math.pi * v),
                           dy + (rp[1] - 7 * depth - dy) * e + out[1] * 14 * math.sin(math.pi * v))
                    a = ang + (90 - ang) * e
                    (fig.fx_front if front else fig.fx_back).append(plate(fig, pos, a, 22 - 8 * e, 11, heat=heat, seed=i))
                else:
                    # debout au sol, elle luit puis rentre dans le sol en laissant une fente de lave
                    hh = (14 * depth) * (1 - smooth(t, 1190, 1300))
                    glow_ = env(t, SP_LAUNCH + 150, 1040, 1150, 1300)
                    lay = fig.fx_front if front else fig.fx_back
                    if hh > 0.4:
                        lay.append(slab(fig, rp[0], 10 * depth, hh, 0.0, 0.12 + 0.4 * glow_, i, by=rp[1] + 0.6))
                    ck = env(t, 1180, 1260, 1380, 1700)
                    if ck > 0:
                        fig.fx_back.append(lava_dash(fig, rp, 5.5 * depth, ck))
        # le soin : une chaleur d'or monte autour de lui, ses fissures luisent
        hl = P.get('heal', 0.0)
        if hl > 0.02:
            fig.under.append((ctx['chest'][0], ctx['chest'][1] + 4, 50, 62, '#ffd860', 0.22 * hl, None))
            fig.fx_back.append(halo_sil(fig, '#ffc850', 0.45 * hl, (3.0, 1.6)))
            for j in range(9):
                k = ((t - 1000) / 600.0 + j * 0.13) % 1
                x = 26 + 82 * ((j * 0.618) % 1) + 2.5 * math.sin(k * 6 + j)
                y = GR - 6 - 80 * k
                fig.fx_front.append(ember(fig, x, y, 0.65, op=hl * (1 - k) * min(1, k * 6), gold=True))
        # le défi : étincelles au choc des poings, lueur rouge qui gonfle et s'éteint
        rd = P.get('red', 0.0)
        if rd > 0.02:
            fig.under.append((ctx['chest'][0], ctx['chest'][1], 58 + 10 * rd, 66 + 10 * rd, '#ff4a4a', 0.28 * rd, None))
            fig.fx_back.append(halo_sil(fig, '#ff5a50', 0.8 * rd, (4.4 + 1.6 * rd, 2.2)))
        tc = (t - SP_CLASH) / 1000.0
        if 0 <= tc < 0.5:
            Wf, Wn = ctx['far']['W'], ctx['near']['W']
            c = ((Wf[0] + Wn[0]) / 2, (Wf[1] + Wn[1]) / 2 - 1)
            fl2 = env(tc, 0, 0.01, 0.05, 0.2)
            if fl2 > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(26), g_rad(
                    fig, c, 26, [(0, '#fffbe4', 0.9 * fl2), (0.3, '#ffe68a', 0.5 * fl2), (1, '#ff7a1e', 0)])))
            for i, (vx, vy) in enumerate(((-60, -110), (70, -100), (-90, -40), (95, -50), (-20, -140), (30, -130), (110, -10), (-110, 0))):
                if tc < 0.45:
                    x, y = ballistic(c, (vx, vy), 260, tc)
                    fig.fx_front.append(ember(fig, x, y, 0.75 if i % 2 else 0.55, op=1 - tc / 0.45))
    return f


def unit2(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def smooth(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def lava_dash(fig, p, w, heat):
    """La fente de lave laissée au sol par une plaque qui rentre (elle refroidit)."""
    pts = [(p[0] - w, p[1] + 0.4), (p[0] - w * 0.3, p[1] + 0.9), (p[0] + w * 0.35, p[1] + 0.2), (p[0] + w, p[1] + 0.6)]
    halo = ribbon(pts, [0.3, 3.4, 3.4, 0.3])
    core = K.cribbon(pts, [0.2, 1.3, 1.3, 0.2])
    return '<path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        halo.d(), LAVA[3], 0.35 * heat, core.d(), LAVA[2] if heat > 0.5 else LAVA[4], min(1, heat * 1.3))


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael)."""
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
    return im


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre douce au sol sous le héros (entre ses pieds)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 48 * k, fy - 3.0 * k, cx + 48 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 0.3), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.2), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
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
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if tl < 300:
            HIT.clear()
        prev = []
        for dt in (0.05, 0.025):
            if T - dt >= t0:
                Pp, _ = pose_at(T - dt, act, t0)
                prev.append(fist_points(K.build(pose=Pp).ctx)[0])
        fx = [fx_attack(tl, prev)]
    elif act == 'special':
        fx = [fx_special(tl)]
    else:
        fx = [fx_idle(T, 1.0)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    """Rend les SVG en PNG (un seul navigateur)."""
    import json
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
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.6, a_s + 0.75, a_s + 0.8, a_s + 1.0, a_s + 1.4,
                            s_s + 0.4, s_s + 0.7, s_s + 0.86, s_s + 0.95, s_s + 1.1, s_s + 1.25, s_s + 1.45, s_s + 1.6, s_s + 1.85, s_s + 2.1]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        bg.alpha_composite(shadow_layer(640, 360, VIEW))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('GARVIN_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    bg.alpha_composite(shadow_layer(VW, VH, VIEW))
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
