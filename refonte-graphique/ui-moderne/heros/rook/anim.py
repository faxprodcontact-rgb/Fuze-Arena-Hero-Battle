# Rook, le chevalier noir vectoriel ANIMÉ (nouveau héros du 26/11, à la place du phénix) : repos, attaque de base,
# attaque spéciale, dans le style lisse de l'interface, à 24 images par seconde (même méthode que Kael : ../kael/anim.py).
# Mêmes durées et mêmes moments de lancement que les animations de l'ancien Rook (attaque : 1,2 s, élan à 450 ms,
# départ à 545 ms, coup à 700 ms ; spéciale : 2,02 s, effet à 590 ms, sommet à 1250 ms ; repos en boucle de 1,6 s).
#
#   python3 refonte-graphique/ui-moderne/heros/rook/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/rook/
#   python3 refonte-graphique/ui-moderne/heros/rook/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (rook.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et se
# penche depuis les hanches, le heaume suit, le bras proche est placé par cinématique inverse (épaule → coude → poing,
# le coude plie toujours du bon côté), l'épée suit le poing, le bras lointain reste le poing sur la hanche, les pieds
# restent plantés. Les flammes de la lame et de l'aura dansent sans arrêt et se couchent derrière le geste.
#  - Repos : respiration lourde (le buste et les épaulières montent, le heaume suit avec retard), la cape, le tabard
#    et la queue du cimier se balancent, les braises du heaume battent doucement, les flammes dansent, braises au sol.
#  - Attaque « Taille de braise » : il arme l'épée haut derrière lui (la lame s'embrase), puis l'abat d'un grand
#    arc de haut en bas vers l'avant (un croissant de feu suit la lame) ; l'arc de feu se détache et file vers
#    l'ennemi (départ 545 ms) et l'enflamme (700 ms) ; il revient en garde.
#  - Spéciale « Serment de cendre » (pouvoir d'équipe) : il lève l'épée vers le ciel (l'aura monte, les braises du
#    heaume flambent), puis la plante devant lui (590 ms) : l'aura s'embrase en un anneau de feu rouge sang et or qui
#    court au sol autour de lui, des flammes montent de l'anneau (sommet à 1250 ms), puis tout retombe ; il retire
#    l'épée et revient au calme. Rien ne vise l'ennemi.
# Effets : dégradés, un seul contour, courbes ; aucun flou SVG ; jamais de rayons droits répétés.
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
import rook as R  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import lerp, tongue_shape  # noqa: E402

ROOT = R.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'rook')
TMP = os.environ.get('ROOK_TMP', os.path.join(HERE, '_images'))
SCRATCH = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-rook-chevalier'
FPS = 24
VIEW = (-22, -24, 272, 153)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = R.GRD
FOE = (214.0, GR - 30)               # l'ennemi (milieu du corps), devant lui
FIRE = R.FIRE
BLOODF = ['#fff0d8', '#ffd27a', '#ff9a3a', '#e2402e', '#a8142c', '#5a0a1e']    # le feu rouge sang et or (spéciale)
FINK = R.FINK


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


BASE = dict(crouch=0, lean=0, headx=0, heady=0, tilt=0, gx=R.G0[0], gy=R.G0[1], ang=R.ANG0, bend=1, fhx=R.FH0[0],
            fhy=R.FH0[1], fire=0, aura=1, eyes=1)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'G':
            d['gx'], d['gy'] = v
        elif key == 'FH':
            d['fhx'], d['fhy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# L'attaque de base « Taille de braise » : il arme l'épée haut derrière l'épaule (la lame pointe vers le haut et
# l'arrière, le buste recule, la lame s'embrase), tenue ; puis il l'abat d'un grand arc (la lame passe au-dessus de sa
# tête et descend devant lui vers l'ennemi, le buste plonge en avant) ; l'arc de feu se détache (545) et frappe (700) ;
# il revient en garde. Les angles de la lame tournent toujours dans le même sens (ils dépassent 360 sans saut).
ATTACK = [
    (0, {}),
    (110, dict(crouch=0.6, G=(43.0, 81.0), ang=150, fire=0.3)),
    (260, dict(crouch=1.6, lean=-2.5, head=(-0.4, -0.3), tilt=-2, G=(41.0, 52.0), ang=212, bend=-1, fire=1.2)),
    (400, dict(crouch=2.0, lean=-3.4, head=(-0.6, -0.5), tilt=-3, G=(41.0, 43.0), ang=232, bend=-1, fire=1.9)),
    (450, dict(crouch=2.0, lean=-3.5, head=(-0.6, -0.5), tilt=-3, G=(41.5, 42.0), ang=235, bend=-1, fire=2.0)),
    (500, dict(crouch=1.2, lean=-0.5, head=(0, -0.4), tilt=-1, G=(49.0, 44.0), ang=268, bend=-0.6, fire=2.3)),
    (545, dict(crouch=1.2, lean=2.5, head=(0.6, 0), tilt=2, G=(62.0, 58.0), ang=345, bend=0.2, fire=2.6)),
    (615, dict(crouch=3.0, lean=5.0, head=(1.0, 0.4), tilt=3, G=(75.0, 68.0), ang=398, bend=0.7, fire=2.4)),
    (700, dict(crouch=3.0, lean=5.0, head=(1.0, 0.4), tilt=3, G=(75.0, 70.5), ang=406, bend=0.8, fire=2.0)),
    (860, dict(crouch=1.6, lean=3.0, head=(0.6, 0.2), tilt=1.5, G=(62.0, 81.0), ang=462, bend=1, fire=1.2)),
    (1000, dict(crouch=0.5, lean=1.0, G=(49.0, 84.5), ang=488, fire=0.5)),
    (1200, dict(ang=498)),
]
A_BEAT, A_LAUNCH, A_HIT = 450, 545, 700

# L'attaque spéciale « Serment de cendre » : il lève l'épée droit vers le ciel à côté du heaume (la lame tourne par
# l'arrière), l'aura monte, les braises du heaume flambent ; tenue ; il l'abat devant lui et la plante (590) :
# l'anneau de feu rouge sang et or part de l'épée et court au sol autour de lui, des flammes en montent (sommet 1250),
# puis tout retombe ; il retire l'épée (1660) et revient au calme.
SPECIAL = [
    (0, {}),
    (100, dict(crouch=0.8, G=(43.0, 82.0), ang=150, aura=1.2)),
    (300, dict(crouch=0.6, lean=-1.5, head=(0, -0.6), tilt=-3, G=(45.0, 36.0), ang=255, bend=-1, fire=1.6, aura=1.6, eyes=1.5)),
    (420, dict(crouch=0.2, lean=-2.0, head=(0, -0.8), tilt=-4, G=(46.0, 30.5), ang=268, bend=-1, fire=2.4, aura=2.0, eyes=1.8)),
    (500, dict(crouch=0.2, lean=-2.0, head=(0, -0.8), tilt=-4, G=(46.5, 30.0), ang=272, bend=-1, fire=2.8, aura=2.1, eyes=2.0)),
    (560, dict(crouch=2.4, lean=3.0, head=(0.4, 0.4), tilt=2, G=(62.0, 74.0), ang=440, bend=0.6, fire=2.8, aura=1.8, eyes=2.0)),
    (590, dict(crouch=3.2, lean=3.6, head=(0.6, 0.6), tilt=3, G=(66.0, 80.0), ang=450, bend=1, fire=2.6, aura=3.0, eyes=2.0)),
    (700, dict(crouch=2.6, lean=3.0, head=(0.4, 0.2), tilt=1, G=(66.0, 80.0), ang=450, bend=1, fire=2.2, aura=3.0, eyes=2.0)),
    (1250, dict(crouch=2.4, lean=2.4, head=(0.2, -0.4), tilt=-1, G=(66.0, 80.0), ang=450, bend=1, fire=2.4, aura=3.2, eyes=2.0)),
    (1470, dict(crouch=2.2, lean=2.2, G=(66.0, 80.0), ang=450, bend=1, fire=1.6, aura=2.2, eyes=1.6)),
    (1660, dict(crouch=1.8, lean=1.6, G=(64.0, 78.0), ang=452, bend=1, fire=1.0, aura=1.6, eyes=1.3)),
    (1760, dict(crouch=0.8, lean=0.6, G=(55.0, 80.0), ang=474, bend=1, fire=0.6, aura=1.3, eyes=1.1)),
    (2020, dict(ang=498)),
]
S_HEAL, S_REZ = 590, 1250


# ======================================================================== la respiration (boucle de 1,6 s)

# Depuis le 27/11 : boucle du repos de 3 s (IDLE_T), la respiration lourde y revient deux fois (IDLE_N) ; le feu
# (ph) y fait 3 tours (1 par seconde ; 1,1 s avant), tous ses rythmes sont des multiples de 1/3 : la boucle se referme.
IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros (1,6 s avant le 27/11)
IDLE_N = 2       # respirations par boucle (une toutes les 1,5 s)
FIRE_N = 3       # tours du feu par boucle


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la lame en feu s'embrase lentement (les flammes montent et rougeoient plus fort, le tranchant
    s'éclaire) puis retombe. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus
    (heros/repos.py : les flammes de la lame dansent aussi, bph ; l'aura des pieds reste immobile)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(fire=1.0 * (0.5 - 0.5 * math.cos(u)), bph=FIRE_N * u)


def idle_offsets(T):
    """La respiration lourde : le buste monte, il se tasse un peu à l'expiration, le heaume suit avec retard,
    la main de l'épée bouge à peine, les braises du heaume battent doucement."""
    u = 2 * math.pi * IDLE_N * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    d = dict(crouch=0.5 * (0.5 - 0.5 * math.cos(u + math.pi)) ** 2, heady=-0.35 * math.sin(u - 1.0),
             tilt=0.5 * math.sin(u - 1.3), gy=0.4 * math.sin(u - 0.6), ang=1.2 * math.sin(u - 0.9),
             fhy=0.3 * math.sin(u - 0.5), eyes=0.12 * math.sin(u * 2))
    return d, br


def raw_pose(T, action=None, t0=0.0):
    w = 1.0
    act = None
    tl = 0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    # le frémissement de la tenue (la lame armée tremble d'un rien)
    if action == 'attack' and 260 <= tl <= 450:
        P['ang'] += 0.7 * math.sin(tl / 1000.0 * 2 * math.pi * 22)
    if action == 'special' and 300 <= tl <= 500:
        P['ang'] += 0.6 * math.sin(tl / 1000.0 * 2 * math.pi * 20)
    P['_w'] = w                                              # le poids du repos (pour le signe, pose_at)
    return P, w * br, tl


def tip_of(P):
    """Le bout de la lame (repère du dessin), à peu près : pour la vitesse des flammes."""
    a = math.radians(P['ang'] + P['lean'] * 1.1)
    return (P['gx'] + 40 * math.cos(a), P['gy'] + 40 * math.sin(a))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours ; les flammes, la cape,
    le tabard et la queue du cimier réagissent à la vitesse."""
    P, br, tl = raw_pose(T, action, t0)
    Pp, _, _ = raw_pose(T - 1 / 24, action, t0)
    t1, t0_ = tip_of(P), tip_of(Pp)
    vx, vy = (t1[0] - t0_[0]) * 24, (t1[1] - t0_[1]) * 24          # pixels par seconde
    tx = max(-4.0, min(4.0, -vx / 60.0))
    ty = max(-3.0, min(3.0, vy / 80.0))
    dl = (P['lean'] - Pp['lean']) * 24
    u = 2 * math.pi * IDLE_N * T / IDLE_T
    sg = signe(T)                                            # le signe du repos : la lame s'embrase (anim.signe)
    out = dict(breath=br, crouch=P['crouch'], lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'],
               ph=sg['bph'], fire=max(0.0, P['fire']) + P['_w'] * sg['fire'], trail=(tx, ty), aura=max(0.0, P['aura']),
               eyes=max(0.0, P['eyes']), G=(P['gx'], P['gy']), ang=P['ang'], bend=max(-1.0, min(1.0, P['bend'])),
               FH=(P['fhx'], P['fhy']), fbend=-1.0,
               cpl=0.9 * math.sin(u - 1.2) - 0.5 * P['lean'] - 0.06 * dl, cpr=0.7 * math.sin(u - 1.6) - 0.4 * P['lean'] - 0.05 * dl,
               pq=0.8 * math.sin(u - 1.8) - 0.25 * P['tilt'] - 0.05 * dl, pg=0.6 * math.sin(u - 1.4) - 0.3 * P['lean'],
               stretch=min(1.5, math.hypot(vx, vy) / 260.0))
    return out


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, pal=FIRE, ink=FINK, iw=1.2):
    """Une langue de feu : large et pâle à la base, fine et rouge (ou rouge sang) au bout, en S."""
    if h < 0.8 or op <= 0.02:
        return ''
    sh = tongue_shape(base, h, w, bend, lean)
    core = tongue_shape((base[0], base[1] + 0.2), h * 0.55, w * 0.52, bend * 0.6, lean)
    bx, by = base
    gout = g_lin(fig, (bx, by), (bx + lean * h, by - h), [(0, pal[1]), (0.35, pal[2]), (0.72, pal[3]), (1, pal[4])])
    gin = g_lin(fig, (bx, by), (bx + lean * h * 0.55, by - h * 0.55), [(0, pal[0]), (0.6, pal[1]), (1, pal[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], ink=ink, w=iw, op=op)


def ember(fig, x, y, r=0.7, op=1.0, pal=FIRE):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, pal[2], 0.55 * op), (1, pal[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, pal[0], op), (0.6, pal[1], op), (1, pal[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#e8dde4'), (0.5, '#b4a2b0'), (1, '#76607c')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#3e2c4a" stroke="#3e2c4a" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def arc_band(C, R_, a0, a1, w, taper=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper)
        outer.append((C[0] + R_ * math.cos(a), C[1] + R_ * math.sin(a)))
        inner.append((C[0] + (R_ - ww) * math.cos(a), C[1] + (R_ - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def fire_arc(fig, C, R_, a0, a1, w, op=1.0):
    """Le croissant de feu qui suit la lame : un arc qui s'élargit vers la lame (pointe effilée derrière), bordé de
    petites langues sur son dos, cœur clair, un seul contour."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    body = arc_band(C, R_ + 1.0, a0, a1, w)
    core = arc_band(C, R_ - w * 0.18, a0 + (a1 - a0) * 0.25, a1, w * 0.45)
    pa = (C[0] + R_ * math.cos(math.radians(a0)), C[1] + R_ * math.sin(math.radians(a0)))
    pb = (C[0] + R_ * math.cos(math.radians(a1)), C[1] + R_ * math.sin(math.radians(a1)))
    g1 = g_lin(fig, pa, pb, [(0, FIRE[4]), (0.45, FIRE[3]), (1, FIRE[2])])
    g2 = g_lin(fig, pa, pb, [(0, FIRE[2]), (0.6, FIRE[1]), (1, FIRE[0])])
    return outlined([(body, g1, 1), (core, g2, 0.95)], w=1.1, op=op)


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


# ---- l'attaque de base

def wave(fig, c, k, op=1.0):
    """L'arc de feu détaché qui file vers l'ennemi : un croissant vertical (bombé vers l'avant) bordé de langues qui se
    couchent vers l'arrière, cœur clair ; il grandit un peu en volant."""
    if op <= 0.02:
        return ''
    Rr = 16 + 5 * k
    C = (c[0] - Rr * 0.8, c[1])
    # le croissant : plein au milieu, effilé aux deux bouts
    outer, inner = [], []
    for i in range(33):
        t = i / 32
        a = math.radians(-62 + 124 * t)
        ww = (8.0 + 2.0 * k) * math.sin(math.pi * t) ** 0.8
        outer.append((C[0] + Rr * math.cos(a), C[1] + Rr * math.sin(a)))
        inner.append((C[0] + (Rr - ww) * math.cos(a), C[1] + (Rr - ww) * math.sin(a)))
    body = sm(outer + inner[::-1], sharp=(0, 32, 33, 65), t=0.6)
    core = sm([(C[0] + (Rr - 0.8) * math.cos(math.radians(-50 + 100 * i / 24)), C[1] + (Rr - 0.8) * math.sin(math.radians(-50 + 100 * i / 24))) for i in range(25)]
              + [(C[0] + (Rr - 0.8 - 3.0 * math.sin(math.pi * i / 24) ** 0.8) * math.cos(math.radians(-50 + 100 * i / 24)),
                  C[1] + (Rr - 0.8 - 3.0 * math.sin(math.pi * i / 24) ** 0.8) * math.sin(math.radians(-50 + 100 * i / 24))) for i in range(24, -1, -1)],
              sharp=(0, 24, 25, 49), t=0.6)
    # deux traînées de feu derrière le croissant, couchées à l'horizontale (il file vers la droite), fondues avec lui
    from outils import fuse
    tails = []
    for j, (aa, L, w0) in enumerate(((-24, 28, 6.4), (24, 21, 5.4), (0, 16, 4.6))):
        a = math.radians(aa)
        b0 = (C[0] + (Rr - 4) * math.cos(a), C[1] + (Rr - 4) * math.sin(a))
        wv = math.sin(k * 18 + j * 2)
        tails.append(lock(b0, (b0[0] - L * 0.3, b0[1] - 1.6 + wv), (b0[0] - L * 0.65, b0[1] + 1.4 - wv),
                          (b0[0] - L, b0[1] - 1.0 + 0.8 * wv), w0, bulge=0.2))
    body, _ = fuse([body] + tails, smooth=0.6, sharp_deg=40)
    out = []
    g1 = g_lin(fig, (C[0] + Rr, C[1] - Rr), (C[0] - 16, C[1] + 4), [(0, FIRE[2]), (0.4, FIRE[3]), (1, FIRE[4])])
    return ''.join(out) + outlined([(body, g1, 1), (core, FIRE[1], 0.95)], w=1.2, op=op)


HIT = {}


def fx_attack(tl, prev):
    def f(fig, ctx):
        sw = ctx['sword']
        G, ang = sw['G'], sw['ang']
        L = R.GUARD_D + R.BL * sw['st']
        # le croissant de feu qui suit la lame quand elle va vite (de l'angle d'il y a 70 ms à l'angle actuel)
        a1 = ang
        a0 = prev
        while a0 > a1 + 180:
            a0 -= 360
        while a0 < a1 - 180:
            a0 += 360
        if 470 <= tl <= 700 and abs(a1 - a0) > 14:
            fig.fx_back.append(fire_arc(fig, G, L - 1, a0, a1, 9.0, op=1.0))
        # l'arc de feu détaché : il part de la lame (545), file vers l'ennemi et le frappe (700)
        if A_LAUNCH <= tl < A_HIT:
            k = (tl - A_LAUNCH) / (A_HIT - A_LAUNCH)
            st = HIT.get('start', (86.0, 70.0))
            c = (st[0] + (FOE[0] - st[0]) * ease(k) ** 0.9, st[1] + (FOE[1] - st[1]) * k)
            fig.fx_front.append(wave(fig, c, k))
            for j in range(4):
                kk = max(0.0, k - 0.08 * (j + 1))
                cx = st[0] + (FOE[0] - st[0]) * ease(kk) ** 0.9
                fig.fx_front.append(ember(fig, cx - 6, st[1] + (FOE[1] - st[1]) * kk + (j - 1.5) * 4, 0.6, op=0.8))
        tau = (tl - A_HIT) / 1000.0
        if tau >= 0:
            c = FOE
            e = env(tau, 0, 0.05, 0.14, 0.45)
            if e > 0:
                fig.under.append((c[0], c[1], 22 * e, 22 * e, FIRE[3], 0.35 * e, None))
                fig.fx_front.append(tongue(fig, (c[0] - 2, c[1] + 8), 20 * e, 7.5, bend=1.0, lean=0.25))
                fig.fx_front.append(tongue(fig, (c[0] + 5, c[1] + 9), 13 * e, 5.2, bend=-0.8, lean=0.6))
                fig.fx_front.append(tongue(fig, (c[0] - 8, c[1] + 9), 11 * e, 4.6, bend=-1.0, lean=-0.4))
            for i, (vx, vy) in enumerate(((50, -80), (80, -25), (20, -100), (65, 20), (-30, -70), (40, -50), (90, -55))):
                if tau < 0.7:
                    x, y = ballistic(c, (vx, vy), 140, tau)
                    fig.fx_front.append(ember(fig, x, y, 0.75 if i % 2 else 0.55, op=max(0, 1 - tau / 0.7)))
            if 0.15 < tau < 0.5:
                k = (tau - 0.15) / 0.35
                fig.fx_back.append(smoke(fig, c[0] + 3 + 2 * k, c[1] - 6 - 12 * k, 2.4 + 3.2 * k, op=0.85 * (1 - k)))
                fig.fx_back.append(smoke(fig, c[0] - 4 - 2 * k, c[1] - 1 - 8 * k, 1.8 + 2.4 * k, op=0.7 * (1 - k)))
    return f


# ---- l'attaque spéciale

def ring(fig, c, rx, ry, hmax, ph, op, lst_back, lst_front, w=3.0):
    """L'anneau de feu rouge sang et or, posé au sol (une ellipse aplatie) : la moitié lointaine derrière lui, la
    moitié proche devant ; des flammes douces dansent sur son dessus (des vagues inégales, jamais des dents)."""
    if op <= 0.02 or rx < 1:
        return
    for half, lst in ((0, lst_back), (1, lst_front)):
        a0, a1 = (180, 360) if half == 0 else (0, 180)
        top, bot = [], []
        for i in range(0, 61):
            ad = a0 + (a1 - a0) * i / 60
            ar = math.radians(ad)
            x = c[0] + rx * math.cos(ar)
            y = c[1] + ry * math.sin(ar)
            wv = max(0.0, math.sin(ar * 5 + ph + 0.8 * math.sin(ar * 3))) ** 1.6
            h = w * 0.5 + hmax * wv * (0.75 + 0.25 * math.sin(ar * 4 + 1.3))
            top.append((x + 0.3 * h * math.cos(ar + 1.2), y - h))
            bot.append((x, y + w * 0.5))
        band = sm(top + bot[::-1], sharp=(0, 60, 61, 121), t=0.8)
        core = sm([(p[0], (p[1] + q[1]) / 2 + 0.3) for p, q in zip(top, bot)] + bot[::-1], sharp=(0, 60, 61, 121), t=0.8)
        gr = g_lin(fig, (c[0], c[1] - ry - hmax), (c[0], c[1] + ry + w), [(0, BLOODF[4]), (0.35, BLOODF[3]), (0.7, BLOODF[2]), (1, BLOODF[1])])
        gc = g_lin(fig, (c[0], c[1] - ry), (c[0], c[1] + ry), [(0, BLOODF[1]), (1, BLOODF[0])])
        lst.append(outlined([(band, gr, 1), (core, gc, 0.9)], ink=FINK, w=0.9, op=op * (0.9 if half == 0 else 1)))


# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : anneau rouge sang d'un seul tenant aux crêtes
# continues, flammes fondues en une silhouette, sans contour sombre ; même rythme, mêmes instants qu'avant)
import effets_pro as E  # noqa: E402


def fx_special(tl):
    def f(fig, ctx):
        sw = ctx['sword']
        P = ctx['P']
        # la montée : des braises montent autour de lui pendant qu'il lève l'épée
        ch = env(tl, 120, 300, 560, 700)
        if ch > 0:
            for i in range(5):
                fr = (i * 0.618) % 1
                x0 = 30 + 72 * fr
                sp = 0.6 + 0.4 * ((i * 0.37) % 1)
                k = ((tl / 1000.0) * sp * 1.4 + (i * 0.29) % 1) % 1
                y = GR - 4 - 70 * k
                x = x0 + 3 * math.sin(k * 6 + i)
                fig.fx_front.append(E.etincelle(fig, x, y, 0, -70, 0.6, 'sang', op=ch * (1 - k) * min(1, k * 5)))
        # l'épée plantée : la lueur et la fente du sol à la pointe
        if sw.get('planted'):
            tp = sw['tip']
            e = env(tl, 560, 600, 1600, 1760)
            fig.under.append((tp[0], GR, 10 + 6 * e, 3 + 1.5 * e, FIRE[3], 0.5 * e, None))
            fig.fx_back.append(E.fissure(fig, [(tp[0] - 10 * e, GR + 0.4), (tp[0], GR + 0.6), (tp[0] + 10 * e, GR + 0.4)], 2.6, 'sang',
                                         op=min(1, 1.2 * e), glow=e))
        # l'éclair de l'impact (590) : une fleur de flammes à la pointe
        fl = env(tl, S_HEAL - 10, S_HEAL + 30, S_HEAL + 80, S_HEAL + 260)
        if fl > 0:
            tp = sw['tip']
            fig.under.append((tp[0], GR - 6, 30 * fl, 18 * fl, BLOODF[2], 0.45 * fl, None))
            fig.fx_front.append(E.flamme(fig, (tp[0], GR + 0.5), [(-3, 13 * fl, 6.0, 1.0, -0.5), (3, 11 * fl, 5.4, -1.0, 0.6)], 'sang'))
        # l'anneau : il part de l'épée et s'élargit autour de lui ; ses flammes montent jusqu'au sommet (1250)
        if tl >= S_HEAL:
            k = (tl - S_HEAL) / 400.0
            e = ease(k)
            c = (66.0, GR)
            rx = 8 + 46 * e
            ry = rx * 0.17
            up = env(tl, S_HEAL, 900, S_REZ + 60, 1700)
            hmax = 3 + 7 * e + 9 * env(tl, 950, S_REZ, S_REZ + 60, 1600)
            op = min(1.0, (tl - S_HEAL) / 60.0) * (1.0 if tl < 1550 else max(0.0, 1 - (tl - 1550) / 300))
            bk, fr = E.anneau(fig, c, rx, ry, hmax * (0.5 + 0.5 * up) + 2, P['ph'] * 1.4 * 60, 'sang', op=op)
            fig.fx_back.append(bk)
            fig.fx_front.append(fr)
            # la lueur rouge sang et or autour de lui
            fig.under.append((66, GR - 20, 44 * up + 10, 34 * up + 6, BLOODF[3], 0.22 * up, None))
            # les grandes flammes qui montent de l'anneau, devant et derrière lui (au sommet)
            top = env(tl, 900, S_REZ, S_REZ + 80, 1620)
            if top > 0:
                back, front = [], []
                for j, (aa, hh, ww) in enumerate(((200, 18, 6.0), (240, 24, 7.0), (290, 22, 6.6), (330, 17, 5.6),
                                                  (20, 15, 5.4), (90, 12, 5.0), (150, 16, 5.6))):
                    ar = math.radians(aa)
                    base = (c[0] + rx * math.cos(ar), c[1] + ry * math.sin(ar) + 0.5)
                    h = hh * top * (0.85 + 0.15 * math.sin(P['ph'] * 2 + j * 1.7))
                    (back if 180 <= aa <= 360 else front).append((base, h, ww * 1.3, math.sin(P['ph'] + j), -90 + 9 * math.cos(ar)))
                fig.fx_back.append(E.langues(fig, back, 'sang', op=min(1.0, top * 1.4)))
                fig.fx_front.append(E.langues(fig, front, 'sang', op=min(1.0, top * 1.4)))
            # des braises d'or qui montent de l'anneau
            if 0.05 < up:
                for i in range(6):
                    a = math.radians(i * 360 / 6 + 13)
                    k2 = ((tl - S_HEAL) / 700.0 + (i * 0.37) % 1) % 1
                    x = c[0] + rx * math.cos(a) + 2 * math.sin(k2 * 6 + i)
                    y = c[1] + ry * math.sin(a) - 46 * k2
                    lst = fig.fx_back if math.sin(a) < 0 else fig.fx_front
                    lst.append(E.etincelle(fig, x, y, 0, -60, 0.65, 'or', op=up * (1 - k2) * min(1, k2 * 6)))
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
    # l'ombre au sol sous lui
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 36 * k, fy - 3.0 * k, cx + 36 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    seq = [('idle', 3.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def frame_at(T, segs):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    return act, t0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = frame_at(T, segs)
    P = pose_at(T, act, t0)
    fx = []
    if act:
        tl = (T - t0) * 1000
        if act == 'attack':
            if 'start' not in HIT:
                Ph = pose_at(t0 + A_LAUNCH / 1000.0, act, t0)
                sw = R.build(pose=Ph).ctx['sword']
                tp = sw['tip']
                HIT['start'] = (tp[0] + 6, (tp[1] + sw['G'][1]) / 2)
            Pp = pose_at(T - 0.07, act, t0)
            prev = Pp['ang'] + Pp['lean'] * 1.1
            fx.append(fx_attack(tl, prev))
        else:
            fx.append(fx_special(tl))
    return R.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1], best[2]


SPRITE_FEET = (64, 116)          # les pieds dans la grille du dessin pixel art (pose : 128 × 120)


def np_alpha(im):
    import numpy as np
    a = np.array(im)
    key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
    a[key, 3] = 0
    return Image.fromarray(a)


def pixel_frames(name):
    """Les images d'une animation pixel art du combat (encore celles du phénix : ses GIF de contrôle, fond clair
    retiré), à l'échelle 1, avec leurs durées et la place du dessin de la pose dans ces images."""
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-rook-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        out.append((np_alpha(im), g.info.get('duration', 100)))
    if name == 'pose':
        return out, (0, 0)
    g0 = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-rook-pose.gif'))
    g0.seek(0)
    sprite = g0.convert('RGBA')
    sprite = sprite.resize((sprite.width // 4, sprite.height // 4), Image.NEAREST)
    ref = out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(np_alpha(sprite), bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du feu, le pixel art du combat (encore le
    phénix) à gauche et le chevalier vectoriel à droite, à la même échelle : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (100, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (64 - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    HIT.clear()
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)], PW, PH, 'b')
    HIT.clear()
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
        layer.paste(big, (round(feet[0] - (ox + SPRITE_FEET[0]) * SC), round(feet[1] - (oy + SPRITE_FEET[1]) * SC)), big)
        left.alpha_composite(layer)
        left = left.resize((PW, PH), Image.NEAREST)
        right = crop.resize((PW, PH), Image.NEAREST)
        right.alpha_composite(Image.open(p))
        fr = Image.new('RGBA', (VW, VH), (24, 16, 40, 255))
        y = (VH - PH) // 2
        fr.paste(left, (0, y))
        fr.paste(right, (VW - PW, y))
        d = ImageDraw.Draw(fr)
        d.text((16, y - 22), 'combat actuel (pixel art) : encore le phenix', fill=(255, 220, 120))
        d.text((VW - PW + 16, y - 22), 'nouveau chevalier (vectoriel)', fill=(255, 220, 120))
        q = os.path.join(TMP, 'c%04d.png' % i)
        fr.convert('RGB').save(q)
        out.append(q)
    return out, n


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
        moments = [0.4, 1.2, a_s + 0.26, a_s + 0.45, a_s + 0.5, a_s + 0.545, a_s + 0.6, a_s + 0.72,
                   s_s + 0.3, s_s + 0.45, s_s + 0.56, s_s + 0.62, s_s + 0.9, s_s + 1.25, s_s + 1.6, s_s + 1.8]
        args = [x for x in sys.argv[2:] if not x.startswith('--')]
        if args:
            moments = [float(x) for x in args]
        svgs = [frame_svg(T, segs) for T in moments]
        pngs = render(svgs, 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(SCRATCH, exist_ok=True)
        dst = os.path.join(SCRATCH, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    HIT.clear()
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, p in enumerate(pngs):
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
    if '--sans-jeu' in sys.argv:
        names2, n2 = [], 0
    else:
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
