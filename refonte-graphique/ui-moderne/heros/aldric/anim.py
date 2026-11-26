# Aldric vectoriel ANIMÉ (refonte de tous les héros, 26/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/aldric/build.py) — respiration de moine, attaque de base « Anneau lancé », attaque
# spéciale « Roue de feu » — mais dans le style lisse de l'interface, sur le modèle de Kael (../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/aldric/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/aldric/)
#   python3 refonte-graphique/ui-moderne/heros/aldric/anim.py --planche [instants…]  # une planche d'images clés (contrôle)
#
# Méthode : le dessin (aldric.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette : buste qui
# respire et se penche depuis les hanches, tête, pans du bandeau et de la ceinture qui ondulent ; les deux bras sont
# placés par cinématique inverse depuis les poignets, les jambes depuis les chevilles, pieds au sol ; le pied lointain
# tourne pour le coup de pied). Les poses clés reprennent celles du pixel art (mêmes gestes vifs de jeune moine :
# armé tenu, détente sèche, appuis courts) et sont reliées par des courbes douces sans dépassement (24 images par
# seconde). L'anneau en vol est redessiné à chaque image (il tourne dans son plan, couché à plat). Les effets (traînée
# de braises, langues de feu, roue de feu, anneau de flammes, braises, fumée) sont dessinés dans le même style :
# dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits répétés.
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
import aldric as K  # noqa: E402
from atelier import Figure, lock, sm, ribbon, ellipse, f as fm, mapp  # noqa: E402
from outils import matmix, lerp, rot, poly_of, geom_shape  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'aldric')
TMP = os.environ.get('ALDRIC_TMP', os.path.join(HERE, '_images'))
LAVA = K.LAVA
FPS = 24
VIEW = (14, -10, 256, 144)           # la scène de la vidéo, en pixels du dessin (16/9) : lui à gauche, l'ennemi à droite
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour du feu
SINK = '#4a3656'                     # le contour de la fumée
GR = K.GRD
ENEMY = (224.0, 80.0)                # là où se tient l'ennemi (le centre de l'explosion)

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


PAIRS = {'head': ('headx', 'heady'), 'fw': ('fwx', 'fwy'), 'nw': ('nwx', 'nwy'), 'fa': ('fax', 'fay')}
SCAL = ['crouch', 'lean', 'tilt', 'tail', 'pg', 'fsh', 'ffront', 'frot', 'ringF', 'rF_sy', 'rF_spin', 'rF_rot', 'rF_da',
        'nrot', 'ringN', 'fext', 'foot', 'hot', 'shift', 'lift', 'breath']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: K.REST[n] for n in SCAL}
    for key, (a, b) in PAIRS.items():
        d[a], d[b] = K.REST[key]
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        elif key in d:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés)
# Points en pixels du dessin (grille du pixel art + 0,5).

# 2) L'attaque de base « Anneau lancé » : il ramène le bras tendu en travers de la poitrine, l'anneau couché à plat
# contre l'épaule proche, le buste tourné, ramassé (anticipation tenue). Détente sèche : le bras fouette vers l'ennemi,
# l'anneau part à plat en tournoyant, une traînée de braises courbe derrière lui ; il frappe l'ennemi (éclat de feu),
# file au-delà, fait le tour (boucle aplatie, comme un disque qui revient) et revient plus bas dans la main tendue ; il
# le rattrape (petit éclat), le bras amortit, retour en garde.
ARMED = dict(fw=(77.0, 56.5), fsh=1.0, ffront=1, rF_sy=0.42, rF_da=-66, rF_rot=-4, crouch=2, lean=-2.2, head=(-0.4, 1),
             tilt=-2, tail=1, pg=-1, nw=(46.8, 79.8))
ATTACK = [
    (0, {}),
    (60, dict(fw=(90.0, 58.4), fsh=0.6, ffront=0, rF_sy=0.75, rF_da=-25, crouch=0.8, lean=-0.8, head=(0, 0.5), tail=0.6, pg=-0.5)),
    (95, dict(ARMED, fw=(82.0, 57.2), fsh=0.9, ffront=1, rF_sy=0.5, rF_da=-50, crouch=1.6, lean=-1.8)),
    (170, dict(ARMED)),
    (300, dict(ARMED, fw=(76.4, 56.8), crouch=2.2, lean=-2.5, head=(-0.5, 1.1))),
    (322, dict(fw=(90.0, 56.2), fsh=0.55, ffront=0, rF_sy=0.45, crouch=0.6, lean=0.8, head=(0.4, 0.3), tilt=1, tail=-0.6, pg=0.5)),
    (345, dict(fw=(101.0, 56.2), fsh=0.0, ringF=0, crouch=0, lean=2.0, head=(1, 0), tilt=2, tail=-1.2, pg=1)),
    (420, dict(fw=(100.6, 56.8), ringF=0, lean=1.6, head=(1, 0), tilt=1.5, tail=-1, pg=1)),
    (560, dict(fw=(100.2, 57.0), ringF=0, lean=1.0, head=(0.5, 0), tilt=0.5, tail=0, pg=0)),
    (660, dict(fw=(100.0, 57.2), ringF=0, lean=1.0, tail=0.6, pg=0)),
    (684, dict(fw=(99.6, 57.4), ringF=1, rF_sy=0.6, lean=1.0, tail=0.4)),
    (760, dict(fw=(95.6, 58.2), ringF=1, rF_sy=0.92, crouch=1, lean=-1, head=(0, 0.8), tail=-0.6, pg=-0.8)),
    (880, dict(fw=(96.8, 57.4), crouch=0.8, lean=-0.2, head=(0, 0.3), tail=0.2, pg=0.3)),
    (1080, {}),
]
T_RELEASE, T_HIT, T_CATCH = 334, 470, 684
# la boucle du vol : une ellipse aplatie, l'aller en haut, le retour en bas (pixel : LOOP_C, LOOP_RX, LOOP_RY)
LOOP_C, LOOP_RX, LOOP_RY = (182.0, 58.0), 70.0, 11.0
FLIGHT = [(T_RELEASE, 168.0), (380, 118.0), (425, 80.0), (T_HIT, 50.0), (540, -10.0), (590, -72.0), (640, -130.0),
          (T_CATCH, -178.0)]

# 3) L'attaque spéciale « Roue de feu » : il se ramasse, souffle retenu : les deux anneaux chauffent à blanc et
# s'embrasent dans ses mains. Détente : il lance les deux anneaux en l'air ; ils montent en tournant et se rejoignent en
# une roue de feu. Il monte le genou ; la roue redescend devant lui ; coup de pied de face : la roue file en roulant
# vers l'ennemi (queue de flammes) et explose en anneau de flammes (arrêt sur l'image) ; les deux anneaux rebondissent
# vers lui en refroidissant, il les rattrape et revient en garde ; la fumée se défait sur l'ennemi.
GUARD = dict(ringF=0, ringN=0)
CHAMBER = dict(fa=(96.0, 91.0), fext=0.55, foot=22)
HALF = dict(fa=(91.0, 99.5), fext=0.25, foot=10)
KICK = dict(fa=(108.0, 77.0), fext=1.0, foot=-78)
SPECIAL = [
    (0, {}),
    (110, dict(crouch=1, lean=-1, head=(0, 0.8), tail=0.8, pg=-0.6, hot=1.0)),
    (300, dict(crouch=2, lean=-2, breath=1, head=(0, 1), tail=1, pg=-1, hot=2.0, fw=(96.8, 57.2), nw=(47.2, 80.2))),
    (345, dict(crouch=2.2, lean=-2.2, breath=1, head=(0, 1.1), tail=1, pg=-1, hot=2.0, fw=(96.4, 57.6), nw=(47.0, 80.6))),
    (380, dict(GUARD, fw=(98.0, 40.6), fsh=0.7, nw=(55.0, 64.0), crouch=-0.6, lean=1.2, head=(0, -0.8), tilt=-3, tail=-1.2,
               pg=1, hot=2.0, frot=-20, nrot=-30)),
    (440, dict(GUARD, crouch=0, lean=0, tail=-1, pg=1, hot=2.0, **HALF)),
    (520, dict(GUARD, crouch=0, lean=-1, tail=0, pg=1, hot=2.0, **CHAMBER)),
    (650, dict(GUARD, crouch=0, lean=-1.2, tail=0.2, pg=1, hot=2.0, **dict(CHAMBER, fa=(96.6, 90.4)))),
    (690, dict(GUARD, crouch=0, lean=-2.0, head=(-0.6, 0), tilt=-2, tail=-1.2, pg=2, hot=2.0, **KICK)),
    (760, dict(GUARD, crouch=0, lean=-1.6, head=(-0.4, 0), tilt=-1, tail=-1, pg=1.5, hot=2.0, **KICK)),
    (830, dict(GUARD, crouch=0, lean=-0.6, tail=-0.6, pg=1, hot=1.6, **CHAMBER)),
    (900, dict(GUARD, crouch=1, lean=0, head=(0, 0.8), tail=0, pg=0, hot=1.2)),
    (1000, dict(GUARD, crouch=1, head=(0, 0.6), tail=0.6, pg=-0.6, hot=1.0)),
    (1180, dict(GUARD, crouch=0.4, tail=0.6, pg=-0.6, hot=0.6)),
    (1225, dict(ringF=1, ringN=1, crouch=0.4, tail=0.4, hot=0.5)),
    (1330, dict(crouch=1, lean=-1, head=(0, 0.8), tail=-0.6, pg=-0.8, fw=(95.8, 58.0), hot=0.25)),
    (1480, dict(crouch=0.4, lean=0, head=(0, 0.2), tail=0, pg=0, hot=0.0)),
    (1700, {}),
]
SP_TOSS, SP_KICK, SP_BOOM, SP_CATCH = 361, 690, 860, 1225


# ======================================================================== la respiration (en boucle, 2 s)

def idle_offsets(T):
    """Posture de moine concentré : le souffle soulève le buste (tête, épaules, bras tendu et anneau), puis à
    l'expiration il se pose sur ses genoux ; la tête suit en retard ; les pans du bandeau flottent, ceux de la ceinture se
    balancent à peine."""
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.55 * (0.5 - 0.5 * math.cos(u - 2.6)), heady=0.3 * math.sin(u - 0.9),
                tilt=-0.5 * math.sin(u - 1.0), tail=0.7 * math.sin(u - 1.5), pg=0.6 * math.sin(u + 0.4))


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
        w = min(1.0, max(0.0, 1 - tl / 150), max(0.0, (tl - (dur - 250)) / 250))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or keyed([(0, {})], 0)
    P = {}
    for n in SCAL:
        P[n] = src[n] + w * idl.get(n, 0.0)
    P['head'] = (src['headx'], src['heady'] + w * idl['heady'])
    P['fw'] = (src['fwx'], src['fwy'])
    P['nw'] = (src['nwx'], src['nwy'])
    P['fa'] = (src['fax'], src['fay'])
    P['breath'] = min(1.0, src['breath'] + w * idl['breath'])
    P['ph'] = 2 * math.pi * T * 0.9 + (1.2 * T if act else 0)
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % 4.0) < 1.39) else 0.0
    P['ffront'] = 1.0 if P['ffront'] > 0.5 else 0.0
    P['ringF'] = 1.0 if P['ringF'] > 0.5 else 0.0
    P['ringN'] = 1.0 if P['ringN'] > 0.5 else 0.0
    # un reflet fait le tour du tranchant de l'anneau levé, puis passe sur l'anneau de la hanche
    c = T % 2.0
    P['gl'] = -160 + 200 * (c / 0.7) if c < 0.7 else None
    P['gn'] = -150 + 160 * ((c - 0.9) / 0.5) if 0.9 <= c < 1.4 else None
    if act:
        P['gl'] = P['gn'] = None
    return P, tl


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


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True, cool=False):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S. lean : elle penche (x par unité de h)."""
    if h < 0.6:
        return ''
    bx, by = base
    p0 = (bx, by)
    p1 = (bx + bend * w * 0.5 + lean * h * 0.12, by - h * 0.33)
    p2 = (bx - bend * w * 0.45 + lean * h * 0.55, by - h * 0.68)
    p3 = (bx + lean * h, by - h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    if cool:
        gout = g_lin(fig, p0, p3, [(0, LAVA[2]), (0.5, LAVA[3]), (1, LAVA[5])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[1]), (1, LAVA[3])])
    else:
        gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
        gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.2 if ink else 0, op=op)


def tongue_dir(fig, base, d, h, w, bend=0.0, op=1.0):
    """Une langue de feu qui part dans une direction quelconque (d : vecteur unité)."""
    if h < 0.6:
        return ''
    bx, by = base
    nx, ny = -d[1], d[0]
    p0 = (bx, by)
    p1 = (bx + d[0] * h * 0.33 + nx * bend * w * 0.5, by + d[1] * h * 0.33 + ny * bend * w * 0.5)
    p2 = (bx + d[0] * h * 0.68 - nx * bend * w * 0.45, by + d[1] * h * 0.68 - ny * bend * w * 0.45)
    p3 = (bx + d[0] * h, by + d[1] * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    core = lock(p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), w * 0.5, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.4, LAVA[2]), (0.75, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, p2, [(0, LAVA[0]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.1, op=op)


def ember(fig, x, y, r=0.7, op=1.0, hot=True):
    if op <= 0.02:
        return ''
    c1, c2, c3 = (LAVA[0], LAVA[1], LAVA[3]) if hot else (LAVA[2], LAVA[3], LAVA[5])
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, c1, op), (0.6, c2, op), (1, c3, op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f4e8e6'), (0.5, '#c8b0b8'), (1, '#8a6c84')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0):
    """Une volute de fumée qui s'enroule (un ruban courbe qui s'affine), sous un contour doux."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f4e8e6'), (0.6, '#c8b0b8'), (1, '#8a6c84')])
    return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)


def pop(fig, c, r, facing=0.0, op=1.0, cool=False):
    """Un éclat d'impact en nuage de feu : un coeur et des lobes arrondis (plus gros vers « facing »), un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    stops = [(0, LAVA[0]), (0.35, LAVA[1]), (0.65, LAVA[2]), (0.88, LAVA[3]), (1, LAVA[4])] if not cool else \
        [(0, LAVA[1]), (0.5, LAVA[2]), (0.85, LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, stops)
    shapes = [(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes]
    return outlined(shapes, w=1.3, op=op)


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


def trim(pts, c, r):
    """La traînée part du bord de l'anneau (jamais de son trou) : on retire les points trop près du centre."""
    out = [p for p in pts if math.dist(p, c) > r]
    return out


def fire_ribbon(fig, pts, w0, op=1.0, hot=True, tip=0.4):
    """Une traînée de feu le long d'une ligne (du plus chaud, contre l'objet, au bout qui s'efface) : un ruban plein
    qui s'effile, bordé d'un liseré clair ; aucun contour (c'est une lueur qui suit)."""
    n = len(pts)
    if n < 3 or op <= 0.02:
        return ''
    ws = [max(0.12, w0 * (1 - i / (n - 1)) ** 0.85) for i in range(n)]
    ws[-1] = 0.1
    body = ribbon(pts, [tip] + ws[1:])
    core = ribbon(pts, [tip * 0.5] + [w * 0.45 for w in ws[1:]])
    a, b = pts[0], pts[-1]
    if hot:
        g1 = g_lin(fig, a, b, [(0, LAVA[1], op), (0.35, LAVA[2], 0.9 * op), (0.75, LAVA[3], 0.6 * op), (1, LAVA[4], 0)])
        g2 = g_lin(fig, a, b, [(0, LAVA[0], op), (0.5, LAVA[1], 0.8 * op), (1, LAVA[2], 0)])
    else:
        g1 = g_lin(fig, a, b, [(0, LAVA[2], op), (0.5, LAVA[3], 0.7 * op), (1, LAVA[5], 0)])
        g2 = g_lin(fig, a, b, [(0, LAVA[1], op), (1, LAVA[3], 0)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, core.d(), g2)


# ---- l'anneau hors de la main (en vol) : le même dessin que dans la main (atelier), posé par-dessus

_SUB = [0]


def ring_fx(fig, C, sx, sy, rot_, spin, hot=0.0, layer='front', glint=None):
    """Un anneau en vol, dessiné comme dans la main (un seul contour, ombrage de bronze), ajouté aux effets."""
    _SUB[0] += 1
    sub = Figure(fig.x0, fig.y0, fig.w, fig.h, ow=fig.ow)
    sub.n = 100000 * _SUB[0]
    mat = matmix(K.BRONZE, K.BRONZE_HOT, 0.5 * hot)
    K.chakram(sub, 'fly', C, sx, sy, rot_, spin, mat, glint, cast=0)
    svg = sub.svg()
    defs = svg[svg.index('<defs>') + 6:svg.index('</defs>')]
    body = svg[svg.index('</defs>') + 7:svg.rindex('</svg>')]
    fig.defs.append(defs)
    (fig.fx_front if layer == 'front' else fig.fx_back).append(body)


def ring_glow(fig, C, r, op):
    """La lueur d'un anneau chauffé à blanc (un dégradé, derrière lui)."""
    if op <= 0.02:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(C[0]), fm(C[1]), fm(r), g_rad(fig, C, r, [
        (0, LAVA[2], 0), (0.42, LAVA[2], 0), (0.6, '#ff8a2a', 0.24 * op), (0.8, '#ff7a1e', 0.1 * op), (1, LAVA[3], 0)]))


# ---- l'attaque de base

def loop_pt(th):
    a = math.radians(th)
    return (LOOP_C[0] + LOOP_RX * math.cos(a), LOOP_C[1] - LOOP_RY * math.sin(a))


def flight(tl):
    """L'angle de l'anneau sur la boucle à l'instant tl (ms)."""
    return monotone([k[0] for k in FLIGHT], [k[1] for k in FLIGHT], tl)


def fx_attack(tl, held_c):
    def f(fig, ctx):
        # la détente : un croissant de feu à hauteur de main (le chemin de l'anneau, de l'épaule à la main tendue)
        e = env(tl, T_RELEASE - 14, T_RELEASE, T_RELEASE + 40, T_RELEASE + 110)
        if e > 0:
            A_ = ctx['far_w']
            B_ = mapp(ctx['UC'], (64.0, 56.0))
            from atelier import bez
            pts = bez((A_[0] + 2, A_[1] - 0.5), (A_[0] - 10, A_[1] + 7), (B_[0] + 12, B_[1] + 7), B_, 30)
            cut = int(len(pts) * min(1.0, 0.35 + 0.65 * e))
            fig.fx_front.append(fire_ribbon(fig, pts[:cut], 4.6, op=e))
        # l'anneau en vol, sa traînée de braises qui suit la boucle
        if T_RELEASE <= tl < T_CATCH:
            th = flight(tl)
            c = loop_pt(th)
            k0 = min(1.0, (tl - T_RELEASE) / 40)
            if k0 < 1:                                   # il part de la main : on glisse de la main à la boucle
                c = lerp(held_c, c, k0 * k0 * (3 - 2 * k0))
            k1 = max(0.0, (tl - (T_CATCH - 50)) / 50)
            if k1 > 0:                                   # il revient dans la main
                c = lerp(c, held_c, k1 * k1 * (3 - 2 * k1))
            back_span = min(70.0, th - flight(max(T_RELEASE, tl - 70)) + 1e-3)
            pts = [loop_pt(th + back_span * i / 24) for i in range(25)]
            pts = trim([c] + pts[1:], c, 8.5)
            fig.fx_back.append(fire_ribbon(fig, pts, 4.6, op=1.0))
            for j in range(4):
                s_ = 0.3 + 0.17 * j
                x, y = loop_pt(th + back_span * s_)
                fig.fx_back.append(ember(fig, x + 1.5 * math.sin(j * 2.1 + tl / 40), y + 2 + 5 * s_, 0.55 if j else 0.75,
                                         op=1 - 0.6 * s_, hot=s_ < 0.6))
            spin = -2.2 * (tl - T_RELEASE)               # il tournoie (degrés)
            sy = 0.42 + 0.5 * k1
            ring_fx(fig, c, 1.0, sy, 0, spin, hot=0.25)
        # l'impact sur l'ennemi : éclat de feu, braises en gerbe, une bouffée de fumée
        tau = (tl - T_HIT) / 1000.0
        if tau >= 0:
            c = loop_pt(FLIGHT[3][1])
            e = env(tau, 0, 0.03, 0.09, 0.26)
            if e > 0:
                fig.fx_front.append(pop(fig, (c[0] + 3, c[1] - 1), 6.0 * (0.6 + 0.4 * e), facing=10, op=e))
                fig.fx_back.append(tongue(fig, (c[0] + 4, c[1] + 2), 9 * e, 4.0, bend=0.8, lean=0.5))
            for i, (vx, vy, big) in enumerate(((30, -34, 1), (44, -14, 0), (22, -46, 0), (50, 2, 1), (12, -24, 0), (36, 12, 0))):
                if tau < 0.6:
                    x, y = ballistic(c, (vx * 1.3, vy * 1.3), 110, tau)
                    if y < GR - 1:
                        fig.fx_front.append(ember(fig, x, y, 0.7 if big else 0.5, op=max(0, 1 - tau / 0.6), hot=tau < 0.3))
            if 0.08 < tau < 0.7:
                k = (tau - 0.08) / 0.62
                fig.fx_back.append(smoke(fig, c[0] + 8 + 4 * k, c[1] - 6 - 9 * k, 2.2 + 2.2 * k, op=0.8 * (1 - k)))
                fig.fx_back.append(curl(fig, (c[0] + 12 + 3 * k, c[1] - 1 - 8 * k), 2.8 + 1.2 * k, 160 + 120 * k, 260, 1.7, op=0.75 * (1 - k)))
        # rattrapé : un petit éclat contre la main, deux braises qui retombent
        tc = (tl - T_CATCH) / 1000.0
        if 0 <= tc < 0.4:
            w_ = ctx['far_w']
            e = env(tc, 0, 0.02, 0.05, 0.14)
            if e > 0:
                fig.fx_front.append(pop(fig, (w_[0] + 7, w_[1] + 5), 2.6 * (0.6 + 0.4 * e), facing=200, op=e))
            for i, (vx, vy) in enumerate(((-18, -20), (16, -26))):
                x, y = ballistic((w_[0] + 8, w_[1] + 2), (vx, vy), 110, tc)
                fig.fx_front.append(ember(fig, x, y, 0.5, op=max(0, 1 - tc / 0.4), hot=False))
    return f


# ---- l'attaque spéciale

def hot_ring_flames(fig, C, sx, sy, level, t, seed=0, front=True):
    """Les anneaux s'embrasent dans les mains : des langues de feu montent du haut de l'anneau, des braises montent."""
    if level <= 0.02:
        return
    R = K.RR
    for j, (a, hk) in enumerate(((-150, 0.7), (-110, 1.0), (-70, 0.85), (-30, 0.6))):
        aa = math.radians(a + 6 * math.sin(t / 90 + j + seed))
        b = (C[0] + R * sx * math.cos(aa) * 1.04, C[1] + R * sy * math.sin(aa) * 1.04 + 0.6)
        wob = math.sin(t / 55.0 + j * 1.9 + seed)
        h = (5 + 6 * level) * hk * (1 + 0.15 * wob)
        (fig.fx_front if (front and j % 2) else fig.fx_back).append(
            tongue(fig, b, h, 2.6 + 1.0 * level, bend=0.8 * wob, lean=0.15 * math.cos(aa)))
    for i in range(3):
        k = ((t / 700.0) + i * 0.33 + seed * 0.1) % 1
        x = C[0] + (i - 1) * 5 + 1.5 * math.sin(k * 7 + i)
        y = C[1] - R * sy - 2 - 14 * k
        fig.fx_front.append(ember(fig, x, y, 0.5 + 0.15 * (i % 2), op=level / 2 * (1 - k)))


def arc_band(C, R, a0, a1, w, n=28):
    """Un croissant le long d'un arc autour de C, de a0 (fin) à a1 (plein) ; degrés, y vers le bas."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** 0.8)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def fire_wheel(fig, C, ph, orbit=8.0, size=1.0, trail=0.0, t=0.0):
    """La roue de feu : les deux anneaux chauffés à blanc tournent l'un autour de l'autre (autour de C, angle ph) ;
    autour d'eux, deux croissants de flammes qui suivent leur ronde ; trail : elle file vers la droite (une queue de
    flammes derrière elle, à gauche)."""
    R = (orbit + K.RR + 3) * size
    for k in (0, 180):
        a0 = ph + k
        band = arc_band(C, R, a0 + 150, a0, 6.5 * size)
        gr = g_lin(fig, (C[0] + R * math.cos(math.radians(a0 + 150)), C[1] + R * math.sin(math.radians(a0 + 150))),
                   (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0))),
                   [(0, LAVA[4]), (0.5, LAVA[2]), (1, LAVA[0])])
        fig.fx_back.append(outlined([(band, gr, 1)], w=1.2))
    if trail:
        for i, (dy, ln, wd, bd) in enumerate(((-6, 0.75, 5.0, 0.9), (1, 1.0, 7.0, -0.6), (7, 0.6, 4.2, -1.0))):
            wob = math.sin(t / 50.0 + i * 2)
            d = (-1, -0.12 * (dy / 7) - 0.15)
            L = math.hypot(*d)
            fig.fx_back.append(tongue_dir(fig, (C[0] - R * 0.5, C[1] + dy * size), (d[0] / L, d[1] / L),
                                          trail * ln * (1 + 0.12 * wob), wd * size, bend=bd))
    for k in (0, 180):
        a = math.radians(ph + k)
        rc = (C[0] + orbit * size * math.cos(a), C[1] + orbit * size * math.sin(a) * 0.9)
        ring_fx(fig, rc, size, size, 0, ph * 2.2 + k, hot=2.0)
    for j in range(5):
        a = math.radians(ph * 0.7 + j * 72 + 20 * math.sin(j))
        r = R + 2 + 2.5 * ((j * 0.37) % 1) * 3
        fig.fx_front.append(ember(fig, C[0] + r * math.cos(a), C[1] + r * math.sin(a), 0.6 if j < 2 else 0.45))


def flame_ring(fig, C, R, w, t, gap=0.0, seed=0, cool=0.0, op=1.0):
    """L'anneau de flammes de l'explosion : un anneau épais, blanc à l'intérieur, rouge au bord, le bord extérieur en
    lobes arrondis (des bouffées, pas des rayons) ; gap > 0 : il se défait en arcs."""
    from shapely.geometry import Polygon
    N = 120
    outer, inner = [], []
    for i in range(N):
        a = 2 * math.pi * i / N
        lobe = 1.6 * abs(math.sin(a * 4.5 + seed)) * (w / 8) + 0.5 * math.sin(a * 7 + t / 60.0)
        outer.append((C[0] + (R + w / 2 + lobe) * math.cos(a), C[1] + (R + w / 2 + lobe) * math.sin(a)))
        ri = R - w / 2 + 0.6 * math.sin(a * 3 + seed)
        inner.append((C[0] + ri * math.cos(a), C[1] + ri * math.sin(a)))
    g = Polygon(outer, [inner]).buffer(0)
    if gap > 0:
        for j in range(4):
            a0 = j * 90 + 30 * seed + 20
            half = 45 * gap
            pts = [C] + [(C[0] + 3 * R * math.cos(math.radians(a0 + 2 * half * i / 8 - half)),
                          C[1] + 3 * R * math.sin(math.radians(a0 + 2 * half * i / 8 - half))) for i in range(9)]
            g = g.difference(Polygon(pts))
        g = g.buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    parts = list(g.geoms) if hasattr(g, 'geoms') else [g]
    stops = [(0, LAVA[0]), (max(0.01, (R - w / 2) / (R + w)), LAVA[0]), (min(0.99, R / (R + w)), LAVA[1] if cool < 0.5 else LAVA[2]),
             (min(0.995, (R + w * 0.45) / (R + w)), LAVA[2] if cool < 0.5 else LAVA[3]), (1, LAVA[4])]
    gr = g_rad(fig, C, R + w, stops)
    shapes = []
    for p in parts:
        if p.is_empty or p.area < 1:
            continue
        sh = geom_shape(p, sharp_deg=70, simplify=0.05)
        if sh is not None:
            shapes.append((sh, gr, 1))
    if shapes:
        fig.fx_back.append(outlined(shapes, w=1.4, op=op))


def scorch(fig, x, w, heat):
    """Le sol brûlé sous l'explosion : une tache de braise qui refroidit (ellipse couchée, un dégradé)."""
    if w <= 0:
        return
    cy = GR + 0.6
    fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(cy), fm(w), fm(w * 0.12), g_rad(
        fig, (x, cy), w, [(0, LAVA[2] if heat > 0.5 else '#7a2a26', 0.9), (0.55, '#7a2a26', 0.7), (1, '#3a1626', 0)])))


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        t = tl
        UC, U = ctx['UC'], ctx['U']
        # les anneaux s'embrasent dans les mains (avant le lancer, et une braise au rattrapé)
        if t < SP_TOSS and ctx['ringF']:
            lv = min(2.0, P['hot'])
            for key, M_, sd in (('ringF', UC, 0), ('ringN', U, 3)):
                r = ctx[key]
                C = mapp(M_, r['C'])
                fig.fx_back.append(ring_glow(fig, C, 16, lv / 2))
                hot_ring_flames(fig, C, r['sx'], r['sy'], lv, t, seed=sd, front=(key == 'ringF'))
        # le lancer : les deux anneaux montent en tournant et se rejoignent
        if SP_TOSS <= t < 480:
            k = (t - SP_TOSS) / (480 - SP_TOSS)
            e = k * (2 - k)
            pa = lerp((112.0, 50.0), (110.0, 22.0), e)
            pb = lerp((50.0, 86.0), (116.0, 25.0), e ** 0.8)
            kp = max(0.0, k - 0.3)
            ep = kp * (2 - kp)
            prevs = (lerp((112.0, 50.0), (110.0, 22.0), ep), lerp((50.0, 86.0), (116.0, 25.0), ep ** 0.8))
            for p, prev, ph in ((pa, prevs[0], 40), (pb, prevs[1], 160)):
                pts = trim([lerp(p, prev, i / 16) for i in range(17)], p, 9.0)
                fig.fx_back.append(fire_ribbon(fig, pts, 4.0, op=1 - 0.5 * k))
                ring_fx(fig, p, 1.0, 1.0 - 0.3 * math.sin(k * 3), 0, ph - 3 * (t - SP_TOSS), hot=2.0)
        # la roue de feu : au-dessus, devant lui ; elle redescend ; le coup de pied ; elle file vers l'ennemi
        if 440 <= t < SP_BOOM:
            WK = [(440, (113.0, 23.0), 0.75, 0), (650, (123.0, 40.0), 1.0, 0), (SP_KICK, (122.0, 66.0), 1.0, 0),
                  (760, (160.0, 70.0), 1.05, 22), (820, (196.0, 76.0), 1.1, 30), (SP_BOOM, ENEMY, 1.1, 30)]
            ts = [w_[0] for w_ in WK]
            cx = monotone(ts, [w_[1][0] for w_ in WK], t)
            cy = monotone(ts, [w_[1][1] for w_ in WK], t)
            sz = monotone(ts, [w_[2] for w_ in WK], t)
            tr = monotone(ts, [w_[3] for w_ in WK], t)
            fire_wheel(fig, (cx, cy), 3.2 * (t - 440), orbit=7.0, size=sz, trail=tr, t=t)
        # le pied frappe la roue : un éclat blanc et or contre la plante, le chemin du pied en croissant de feu
        tk = (t - SP_KICK) / 1000.0
        if -0.03 <= tk < 0.13:
            foot = ctx['fleg'][2]
            e = env(tk, -0.03, 0.0, 0.04, 0.13)
            fig.fx_front.append(pop(fig, (foot[0] + 8, foot[1] - 6), 4.6 * (0.6 + 0.4 * e), facing=-20, op=e))
            from atelier import bez
            B_ = mapp(ctx['ROOT'], (95.0, 90.0))
            pts = bez((foot[0] + 3, foot[1]), (foot[0] - 2, foot[1] + 10), (B_[0] + 8, B_[1] + 6), B_, 24)
            fig.fx_back.append(fire_ribbon(fig, pts, 5.0, op=e))
        # l'explosion : l'anneau de flammes jaillit sur l'ennemi, s'élargit et se défait ; le sol brûlé
        tb = (t - SP_BOOM) / 1000.0
        if tb >= 0:
            X, Y = ENEMY
            if tb < 0.5:
                R = 12 + 18 * (1 - math.exp(-tb / 0.12))
                w = 9 * (1 - tb / 0.5) + 1.5
                gap = max(0.0, (tb - 0.12) / 0.38)
                if gap < 0.95:
                    flame_ring(fig, (X, Y), R, w, t, gap=gap, seed=2, cool=gap, op=1 - 0.3 * gap)
            if tb < 0.12:
                fig.fx_front.append(pop(fig, (X, Y), 7 * (1 - tb / 0.12) + 2, facing=0))
            if tb < 0.6:
                hh = 14 * env(tb, 0, 0.05, 0.2, 0.6)
                for j, (dx, s_) in enumerate(((-9, 0.7), (0, 1.0), (10, 0.75), (-3, 0.55))):
                    wob = math.sin(t / 45.0 + j * 1.7)
                    fig.fx_back.append(tongue(fig, (X + dx, GR - 0.5), hh * s_ * (1 + 0.15 * wob), 4.6 * s_ + 1.4,
                                              bend=0.7 * wob, lean=0.1 * dx / 10))
            scorch(fig, X, 22 * min(1, tb / 0.1 + 0.3) * (1 - max(0, tb - 0.6) / 1.2), 1 - tb)
            for i, (vx, vy) in enumerate(((-26, -50), (22, -62), (-12, -70), (34, -38), (-36, -30), (8, -56))):
                if tb < 0.8:
                    x, y = ballistic((X, Y), (vx * 1.2, vy * 1.2), 120, tb)
                    if y < GR - 1:
                        fig.fx_front.append(ember(fig, x, y, 0.7 if i % 2 else 0.5, op=max(0, 1 - tb / 0.8), hot=tb < 0.35))
            if 0.12 < tb < 1.2:
                k = (tb - 0.12) / 1.08
                fig.fx_back.append(smoke(fig, X - 3 + 4 * k, Y - 26 - 14 * k, 4 + 3 * k, op=0.85 * (1 - k)))
                fig.fx_back.append(smoke(fig, X + 9 + 3 * k, Y - 18 - 10 * k, 3 + 2 * k, op=0.7 * (1 - k)))
                fig.fx_back.append(curl(fig, (X + 15, Y - 22 - 8 * k), 3.6 + 1.2 * k, 200 + 100 * k, 280, 2.0, op=0.75 * (1 - k)))
        # les deux anneaux rebondissent vers lui en tournoyant et refroidissent
        if SP_BOOM + 60 <= t < SP_CATCH:
            k = (t - SP_BOOM - 60) / (SP_CATCH - SP_BOOM - 60)
            e = k * k * (3 - 2 * k)
            hf = mapp(UC, ctx['ringF']['C']) if ctx['ringF'] else mapp(UC, K.RC_F)
            hn = mapp(U, ctx['ringN']['C']) if ctx['ringN'] else mapp(U, K.RC_N)
            for p0, p1, lift, ph in (((214.0, 66.0), hf, 20.0, 0), ((218.0, 96.0), hn, 10.0, 90)):
                p = lerp(p0, p1, e)
                p = (p[0], p[1] - lift * math.sin(math.pi * e))
                pv = lerp(p0, p1, max(0, e - 0.12))
                pv = (pv[0], pv[1] - lift * math.sin(math.pi * max(0, e - 0.12)))
                pts = trim([lerp(p, pv, i / 14 * 1.4) for i in range(15)], p, 8.0)
                fig.fx_back.append(fire_ribbon(fig, pts, 3.2, op=1 - 0.6 * e, hot=e < 0.5))
                ring_fx(fig, p, 1.0, 0.75 + 0.25 * e, 0, ph - 2.6 * (t - SP_BOOM), hot=max(0.0, 1.6 * (1 - e)))
        # rattrapés : petits éclats aux deux mains
        tc = (t - SP_CATCH) / 1000.0
        if 0 <= tc < 0.15:
            e = env(tc, 0, 0.02, 0.05, 0.15)
            for key, M_ in (('ringF', UC), ('ringN', U)):
                if ctx[key]:
                    C = mapp(M_, ctx[key]['C'])
                    fig.fx_front.append(pop(fig, (C[0] - 6, C[1] + 4), 2.4 * (0.6 + 0.4 * e), facing=200, op=e, cool=True))
    return f


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
    return im


def shadow_layer(w, h, view, shift, lift, floor_y=GR):
    """L'ombre douce au sol sous le héros."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    sd = ImageDraw.Draw(sh)
    cx = (68 + shift - x0) * k
    s = max(0.45, 1 - lift / 40)
    sd.ellipse([cx - 30 * k * s, fy - 2.6 * k * s, cx + 30 * k * s, fy + 2.6 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 4.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


HELD = {}


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
        # là où l'anneau revient : sa place dans la main au moment du rattrapé
        if 'c' not in HELD:
            Ph, _ = pose_at(t0 + T_CATCH / 1000.0, act, t0)
            cx = K.build(pose=Ph).ctx
            HELD['c'] = mapp(cx['UC'], cx['ringF']['C'])
        fx = [fx_attack(tl, HELD['c'])]
    elif act == 'special':
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
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, 2.2, a_s + 0.06, a_s + 0.2, a_s + 0.33, a_s + 0.36, a_s + 0.44, a_s + 0.5, a_s + 0.6,
                            a_s + 0.69, a_s + 0.76, s_s + 0.2, s_s + 0.38, s_s + 0.45, s_s + 0.6, s_s + 0.7, s_s + 0.79,
                            s_s + 0.9, s_s + 1.05, s_s + 1.15, s_s + 1.24, s_s + 1.4]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P['shift'], P['lift']))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P['shift'], P['lift']))
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
