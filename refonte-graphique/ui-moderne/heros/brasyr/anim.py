# Brasyr vectoriel ANIMÉ (dragon-feu) : mêmes durées et mêmes moments que les animations d'Elvyn (../elvyn/anim.py) —
# repos (respiration, crinière, houppe, ceinture, pompon et flammes de la lame qui bougent, clignement), attaque de base
# « croissant de braise », attaque spéciale « souffle du dragon » — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/brasyr/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/brasyr/)
#   python3 refonte-graphique/ui-moderne/heros/brasyr/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode (comme Elvyn) : le dessin (brasyr.py) est fait de morceaux ; chaque image le redessine dans une POSE (bassin qui
# descend et genoux qui plient par deux os, pieds au sol ; buste qui respire et se penche depuis la taille ; tête,
# crinière, houppe, ceinture, pompon ; les deux mains suivent la hampe, les bras par deux os). Les poses clés sont
# reliées par des courbes douces sans dépassement (24 images par seconde). Les effets de feu (traînée de la lame,
# croissant de braise, souffle, langues de feu, braises, fumée) : dégradés, un seul contour, aucun flou.
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
import brasyr as E  # noqa: E402
from atelier import lock, sm, ribbon, limb, ellipse, f as fm  # noqa: E402

ROOT = E.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'brasyr')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-brasyr') + '/_images'
FPS = 24
GR = E.GRD
VIEW = (-41, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9) : la même qu'Elvyn
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes (comme Kael)
LAVA = E.LAVA
FOE = (177.0, 77.0)                  # l'ennemi (milieu du corps), le même qu'Elvyn

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


NUM = ['crouch', 'lean', 'tilt', 'mane', 'tail', 'tuft', 'sash', 'barb', 'glow', 'jaw', 'gx', 'gy', 'wang', 'gs', 'flame',
       'tassel', 'headx', 'heady', 'swell']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, mane=0, tail=0, tuft=0, sash=0, barb=0, glow=1.0, jaw=0, gx=E.G1_0[0], gy=E.G1_0[1],
             wang=E.WANG0, gs=E.GS, flame=1.0, tassel=0, headx=0, heady=0, swell=0)
    for key, v in k.items():
        if key == 'grip':
            d['gx'], d['gy'] = v
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
# 2) L'attaque de base « croissant de braise » : il arme la hallebarde au-dessus de l'épaule (il se redresse, recule le
# buste, les mains se rapprochent sur la hampe, la lame s'embrase), puis fauche d'un coup en diagonale vers l'avant en
# fléchissant la jambe avant : la lame laisse une traînée de feu et un croissant de braise part vers l'ennemi, où il
# éclate en langues de feu, braises et fumée. Il revient en garde.
ATTACK = [
    (0, {}),
    (130, dict(grip=(45.0, 64.0), wang=-44, gs=34, lean=-3, crouch=0.6, head=(-0.8, 0.4), tilt=-2, tail=1, tuft=1, sash=0.8,
               mane=0.6, barb=1, tassel=1.2, flame=1.2, glow=1.3)),
    (340, dict(grip=(43.0, 58.0), wang=-74, gs=22, lean=-6, crouch=1.2, head=(-1.4, 0.6), tilt=-4, tail=2, tuft=2, sash=1.2,
               mane=1, barb=1, tassel=1.6, flame=1.6, glow=1.8)),
    (395, dict(grip=(57.0, 70.0), wang=4, gs=30, lean=9, crouch=2.0, head=(1.6, 1.0), tilt=4, jaw=0.5, tail=-1.5, tuft=1,
               sash=-1.2, mane=-1.2, barb=-1.5, tassel=-1.8, flame=1.9, glow=2)),
    (470, dict(grip=(58.0, 71.0), wang=10, gs=30, lean=10, crouch=2.2, head=(1.8, 1.2), tilt=4.5, jaw=0.3, tail=-2, tuft=-1,
               sash=-1.4, mane=-1.2, barb=-2, tassel=-1.2, flame=1.6, glow=1.6)),
    (640, dict(grip=(56.0, 70.4), wang=4, gs=32, lean=8, crouch=1.8, head=(1.4, 0.8), tilt=3, tail=-1, tuft=-2, sash=-0.4,
               mane=-0.6, barb=-1, tassel=0.6, flame=1.2, glow=1.3)),
    (800, dict(grip=(53.0, 69.8), wang=-8, gs=36, lean=4, crouch=1.2, head=(0.8, 0.4), tail=0.6, tuft=-1, sash=0.6, mane=0.3,
               barb=0.5, tassel=1)),
    (960, dict(grip=(50.0, 69.2), wang=-19, gs=39, lean=1, crouch=0.7, tail=1, tuft=0.6, sash=0.3, mane=0.6, barb=1, tassel=0.4)),
    (1150, dict(tuft=0.5, sash=0.2, mane=0.2)),
    (1300, {}),
]
ATT_SWING = (330, 480)          # la traînée de feu de la lame
ATT_FIRE, ATT_HIT = 395, 545    # le croissant part, le croissant éclate

# 3) L'attaque spéciale « souffle du dragon » : il se dresse, relève la tête et aspire (la poitrine se gonfle, des braises
# tourbillonnent vers sa gueule, ses naseaux rougeoient, la lame flambe) ; il se jette en avant, gueule ouverte, et
# crache un long jet de feu qui file jusqu'à l'ennemi et l'enveloppe (gerbe de langues de feu, braises, fumée) ; puis
# le jet s'éteint de la gueule vers l'ennemi, il referme la gueule, de la fumée sort de ses naseaux.
SPECIAL = [
    (0, {}),
    (160, dict(grip=(47.0, 67.0), wang=-32, lean=-2, crouch=0.6, head=(-0.5, 0), tilt=-3, tail=1, tuft=1, sash=0.6, mane=0.6,
               barb=0.6, tassel=0.8, swell=0.4, glow=1.4)),
    (420, dict(grip=(46.0, 65.0), wang=-38, lean=-6, crouch=-0.6, head=(-1.4, -1.2), tilt=-13, tail=2, tuft=1.5, sash=1,
               mane=1, barb=1, tassel=1.2, swell=1.3, glow=1.8, flame=1.4)),
    (700, dict(grip=(46.0, 64.4), wang=-40, lean=-7, crouch=-0.8, head=(-1.6, -1.5), tilt=-15, tail=2, tuft=2, sash=1.2, mane=1,
               barb=1, tassel=1.4, swell=1.7, glow=2, flame=1.6)),
    (760, dict(grip=(49.0, 70.0), wang=-8, lean=8, crouch=1.4, head=(2.0, 0.8), tilt=4, jaw=1, tail=-1.5, tuft=1, sash=-1,
               mane=-1.4, barb=-1.6, tassel=-1.4, swell=0.2, glow=2, flame=1.8)),
    (1180, dict(grip=(49.4, 70.2), wang=-7, lean=8.6, crouch=1.6, head=(2.2, 1.0), tilt=5, jaw=1, tail=-2, tuft=-1, sash=-1.2,
                mane=-1.6, barb=-2, tassel=-1, glow=2, flame=1.8)),
    (1320, dict(grip=(49.0, 70.0), wang=-10, lean=7, crouch=1.4, head=(1.8, 0.8), tilt=3, jaw=0.6, tail=-1, tuft=-1.5, sash=-0.6,
                mane=-1, barb=-1, tassel=0.4, glow=1.6, flame=1.5)),
    (1560, dict(grip=(50.0, 69.0), wang=-24, lean=3, crouch=0.8, head=(0.6, 0.3), tilt=1, jaw=0, tail=0.6, tuft=0, sash=0.6,
                mane=0.3, barb=0.6, tassel=1, glow=1.3)),
    (1800, dict(lean=1, crouch=0.6, tail=1, tuft=1, sash=-0.4, mane=0.5, barb=0.5, tassel=-0.4)),
    (2050, dict(crouch=0.3, tail=-0.5, tuft=0.6, sash=-0.4, mane=-0.3, barb=-0.4)),
    (2250, dict(tuft=-0.3)),
    (2400, {}),
]
SP_GATHER = (60, 760)           # il aspire : des braises tourbillonnent vers sa gueule
SP_EMERGE = 760                 # le jet de feu sort de la gueule
SP_HIT = 1260                   # le feu enveloppe l'ennemi (éclat, gerbe)
SP_REACH = 1060                 # le front du jet atteint l'ennemi
SP_STOP = (1300, 1480)          # le jet s'éteint (de la gueule vers l'ennemi)


# ======================================================================== la respiration (en boucle, 2 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la crinière de flammes ondule plus fort (deux vagues par boucle) et la lame de la hallebarde rougeoie
    lentement. Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(wv=1.4, lame=0.5 - 0.5 * math.cos(u), pm=2 * u)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    cr = 0.4 * (0.5 - 0.5 * math.cos(u - 1.4))
    return dict(breath=br, crouch=cr, heady=0.3 * math.sin(u - 0.6), tilt=0.6 * math.sin(u - 0.9), mane=0.5 * math.sin(u - 1.2),
                tail=0.9 * math.sin(u), tuft=0.9 * math.sin(u - 0.9), sash=0.6 * math.sin(u - 1.9), barb=0.8 * math.sin(u - 1.6),
                tassel=0.7 * math.sin(u - 2.2), flame=0.12 * math.sin(2 * u + 0.4), glow=0.2 * (0.5 - 0.5 * math.cos(u - 2.2)),
                gy=1.0 * cr + 0.25 * math.sin(u - 1.0), gx=0.25 * cr, wang=0.6 * math.sin(u - 1.2))


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
    P['breath'] = w * idl['breath'] + 1.2 * P.pop('swell')
    P['grip'] = (P.pop('gx'), P.pop('gy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    sg = signe(T)
    P['wv'], P['lame'] = w * sg['wv'], w * sg['lame']
    P['ph'] = P['pm'] = sg['pm']     # la queue, les pans : la même phase, périodique sur 3 s
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return P


# ======================================================================== les effets de feu (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.4, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses d'abord, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, o in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl, '' if o == 1 else ' opacity="%g"' % o)
                  for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def tongue(fig, base, h, w, ang=-90.0, bend=0.0, op=1.0, ink=True):
    """Une langue de feu qui part de `base` dans la direction `ang` (degrés, y vers le bas ; -90 = vers le haut) : large
    et pâle à la base, fine et rouge au bout, en S (forme des flammes de Kael)."""
    if h < 0.6 or op <= 0.02:
        return ''
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    Pp = lambda s, o: (base[0] + u[0] * s + n[0] * o, base[1] + u[1] * s + n[1] * o)   # noqa: E731
    p0, p1, p2, p3 = Pp(0, 0), Pp(h * 0.33, bend * w * 0.5), Pp(h * 0.68, -bend * w * 0.45), Pp(h, bend * w * 0.15)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (p0[0] + (p[0] - p0[0]) * k, p0[1] + (p[1] - p0[1]) * k)            # noqa: E731
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.3 if ink else 0, op=op)


def ember(fig, x, y, r=0.7, op=1.0):
    """Une braise : un point brûlant et sa petite auréole (dégradé radial, aucun flou)."""
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, LAVA[2], 0.6 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def spark(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte de feu qui vole : ronde devant, effilée derrière (dans le sens de sa course)."""
    if op <= 0.02:
        return ''
    a = math.atan2(vy, vx) if (vx or vy) else -math.pi / 2
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.8, y - math.sin(a) * r * 2.8)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.35, r * 0.25), LAVA[0], 0.9)], w=1.0, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite (comme Kael)."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def fireball(fig, cx, cy, r, op=1.0, ink=True):
    """Une boule de feu (bouffée de flamme) : quelques boules réunies sous un contour, cœur pâle en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.72 * r, cy + 0.3 * r, 0.7 * r), (cx - 0.78 * r, cy + 0.32 * r, 0.66 * r), (cx + 0.1 * r, cy - 0.6 * r, 0.6 * r)]
    gr = g_rad(fig, (cx + 0.3 * r, cy - 0.35 * r), 1.7 * r, [(0, LAVA[0]), (0.3, LAVA[1]), (0.65, LAVA[2]), (1, LAVA[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.2"/>' % (fm(x), fm(y), fm(rr), FINK, FINK) for x, y, rr in balls) if ink else ''
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
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


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def blade_pts(P):
    """La pointe et le milieu du tranchant de la lame pour une pose (sans dessiner) : pour la traînée de feu."""
    G1, G2, d, n = E.weapon_frame(P)
    B0 = E.SHAFT[1] + 3.0
    tip = E.wpt(G1, d, n, B0 + 31.0, -5.0)
    mid = E.wpt(G1, d, n, B0 + 21.0, 5.6)
    base = E.wpt(G1, d, n, B0, 2.4)
    return tip, mid, base


def burst(fig, c, e, big=1.0, t=0.0):
    """La gerbe de feu sur l'ennemi : une grosse boule de feu, et des langues qui montent (le feu monte : pas une
    étoile de rayons), de tailles, de places et de courbures inégales."""
    if e <= 0.02:
        return
    fig.fx_back.append(fireball(fig, c[0], c[1] + 2, 7.5 * big * (0.5 + 0.5 * e)))
    for j, (dx, dy, ang, h, w, bd) in enumerate(((-1, 0, -92, 24, 8.0, 0.6), (-8, 3, -112, 15, 6.0, -0.7), (7, 2, -74, 18, 6.4, 0.7),
                                                 (-13, 6, -128, 9, 4.4, -0.5), (12, 6, -60, 10, 4.4, 0.5))):
        flick = 1 + 0.08 * math.sin(t / 30.0 + j * 2.1)
        (fig.fx_front if j in (0, 3, 4) else fig.fx_back).append(
            tongue(fig, (c[0] + dx * big, c[1] + dy * big), h * big * e * flick, w * big * (0.6 + 0.4 * e), ang=ang, bend=bd))
    fig.fx_front.append(fireball(fig, c[0] + 1, c[1] + 4, 4.5 * big * (0.5 + 0.5 * e), op=0.95))


# ---- l'attaque de base : la traînée de la lame et le croissant de braise

def fx_attack(tl):
    def f(fig, ctx):
        # la traînée de feu derrière la lame qui fauche (entre la pointe et le milieu du tranchant, sur les dernières images)
        if ATT_SWING[0] <= tl <= ATT_SWING[1] + 120:
            fade = 1.0 - smooth((tl - ATT_SWING[1]) / 120.0) if tl > ATT_SWING[1] else 1.0
            ts = [max(ATT_SWING[0], min(tl, ATT_SWING[1]) - k * 14) for k in range(9)]
            outer, inner = [], []
            for t_ in ts:
                tip, mid, base = blade_pts(pose_at(t_ / 1000.0, 'attack', 0.0))
                outer.append(tip)
                inner.append(mid)
            if math.dist(outer[0], outer[-1]) > 3:
                band = sm(outer + inner[::-1], sharp=(0, len(outer) - 1, len(outer)), t=0.6)
                g1 = g_lin(fig, outer[-1], outer[0], [(0, LAVA[4], 0), (0.45, LAVA[3], 0.7 * fade), (1, LAVA[2], 0.95 * fade)])
                fig.fx_back.append('<path d="%s" fill="%s"/>' % (band.d(), g1))
                rim = ribbon(outer, [1.6 * fade] + [1.4 * fade] * (len(outer) - 2) + [0.1])
                fig.fx_back.append('<path d="%s" fill="%s" opacity="%g"/>' % (rim.d(), LAVA[0], 0.85 * fade))
        # le croissant de braise : il part de la lame et file vers l'ennemi en tournant à peine
        if ATT_FIRE <= tl < ATT_HIT:
            s = smooth((tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)) * 0.85 + 0.15 * (tl - ATT_FIRE) / (ATT_HIT - ATT_FIRE)
            p0 = (114.0, 70.0)
            c = (p0[0] + (FOE[0] - p0[0]) * s, p0[1] + (FOE[1] - p0[1]) * s - 6 * math.sin(math.pi * s))
            R = 12.0 + 3 * s
            # un croissant ouvert vers l'arrière (vers le héros), plus épais au milieu, pointes effilées
            pts_o, pts_i = [], []
            for i in range(17):
                a = math.radians(-70 + 140 * i / 16)
                ww = 6.4 * math.sin(math.pi * i / 16) ** 0.8 + 0.2
                pts_o.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a) * 1.05))
                pts_i.append((c[0] + (R - ww) * math.cos(a) - 2.0, c[1] + (R - ww) * math.sin(a) * 1.05))
            cres = sm(pts_o + pts_i[::-1], sharp=(0, 16, 17, 33), t=0.7)
            core = sm([(c[0] + (R - 1.2) * math.cos(math.radians(-50 + 100 * i / 10)), c[1] + (R - 1.2) * math.sin(math.radians(-50 + 100 * i / 10)))
                       for i in range(11)] + [(c[0] + (R - 3.6) * math.cos(math.radians(50 - 100 * i / 10)) - 1.0, c[1] + (R - 3.6) * math.sin(math.radians(50 - 100 * i / 10)))
                                              for i in range(11)], sharp=(0, 10, 11, 21), t=0.7)
            gr = g_lin(fig, (c[0] - R, c[1]), (c[0] + R, c[1]), [(0, LAVA[4]), (0.5, LAVA[3]), (1, LAVA[2])])
            gc = g_lin(fig, (c[0] - R, c[1]), (c[0] + R, c[1]), [(0, LAVA[2]), (1, LAVA[0])])
            fig.fx_front.append(outlined([(cres, gr, 1), (core, gc, 0.95)], w=1.3))
            # les flammèches qui traînent derrière les pointes du croissant
            for j, (k, h) in enumerate(((0.2, 7.0), (0.5, 9.0), (0.8, 7.0))):
                a = math.radians(-70 + 140 * k)
                b = (c[0] + (R - 2.4) * math.cos(a) - 1.0, c[1] + (R - 2.4) * math.sin(a))
                fig.fx_back.append(tongue(fig, b, h * (0.8 + 0.2 * math.sin(tl / 25 + j)), 3.4, ang=180 + 8 * (j - 1), bend=0.5 * (1 - j)))
            for kk in range(4):
                fig.fx_front.append(ember(fig, c[0] - 8 - 6 * kk + 1.5 * math.sin(tl / 40 + kk), c[1] + 3 * math.sin(kk * 2.3 + tl / 60), 0.6, op=1 - kk * 0.2))
        # l'éclatement : la gerbe de feu, des gouttes de feu qui retombent, des braises qui montent, la fumée
        tau = (tl - ATT_HIT) / 1000.0
        if tau >= 0:
            c = FOE
            fl = env(tau, 0, 0.02, 0.05, 0.18)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="22" fill="%s"/>' % (fm(c[0]), fm(c[1]), g_rad(
                    fig, c, 22, [(0, LAVA[0], 0.85 * fl), (0.3, LAVA[2], 0.5 * fl), (1, LAVA[3], 0)])))
                fig.fx_front.append(fireball(fig, c[0], c[1], 6.0 * (0.6 + 0.4 * fl), op=fl))
            e = env(tau, 0, 0.06, 0.16, 0.42)
            if e > 0:
                burst(fig, c, e, 0.8, tl)
            for i, (vx, vy, r) in enumerate(((-60, -90, 1.2), (-90, -30, 1.0), (40, -110, 1.1), (80, -60, 0.9), (-20, -130, 1.0), (110, -20, 0.8))):
                if 0.03 < tau < 0.7:
                    x, y = ballistic(c, (vx, vy), 260, tau)
                    if y < GR - 1:
                        fig.fx_front.append(spark(fig, x, y, vx, vy + 260 * tau, r, op=min(1, (0.7 - tau) * 4)))
            for i, (dx, sp) in enumerate(((-6, 26), (5, 34), (12, 22), (-12, 30))):
                if 0.08 < tau < 0.75:
                    k = tau - 0.08
                    fig.fx_front.append(ember(fig, c[0] + dx + 1.5 * math.sin(k * 10 + i), c[1] - 6 - sp * k, 0.55, op=min(1, (0.75 - tau) * 4)))
            if 0.12 < tau < 0.75:
                k = (tau - 0.12) / 0.63
                fig.fx_back.append(smoke(fig, c[0] - 2, c[1] - 6 - 14 * k, 4.0 + 3 * k, op=0.75 * (1 - k)))
                fig.fx_back.append(smoke(fig, c[0] + 6, c[1] - 2 - 10 * k, 3.0 + 2 * k, op=0.6 * (1 - k)))
    return f


# ---- l'attaque spéciale : le souffle du dragon

def stream_shape(m, s0, s1, tl, wid=1.0):
    """Le jet de feu de la gueule (m) vers l'ennemi, de la fraction s0 à s1 du trajet : un ruban qui s'élargit en
    ondulant, bout avant arrondi (comme une langue de feu couchée)."""
    p1 = FOE
    mid = ((m[0] + p1[0]) / 2, (m[1] + p1[1]) / 2 - 8)

    def at(s):
        return ((1 - s) ** 2 * m[0] + 2 * (1 - s) * s * mid[0] + s * s * p1[0], (1 - s) ** 2 * m[1] + 2 * (1 - s) * s * mid[1] + s * s * p1[1])
    n = 18
    cen, ws = [], []
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        p = at(s)
        a, b = at(min(1, s + 0.01)), at(max(0, s - 0.01))
        L = math.dist(a, b) or 1
        nx, ny = -(a[1] - b[1]) / L, (a[0] - b[0]) / L
        wob = 1.2 * math.sin(s * 14 - tl / 45.0) * min(1, s * 4)
        cen.append((p[0] + nx * wob, p[1] + ny * wob))
        ws.append(wid * (2.2 + 15 * s ** 0.9) * (0.92 + 0.08 * math.sin(s * 23 + tl / 30.0)))
    return cen, ws, at


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        mouth = ctx['mouth']
        nos = ctx['nostril']
        # il aspire : des braises tourbillonnent vers sa gueule (de plus en plus près), les naseaux rougeoient
        ch = env(tl, SP_GATHER[0], SP_GATHER[0] + 160, SP_GATHER[1] - 80, SP_GATHER[1] + 20)
        if ch > 0:
            for i in range(12):
                st = SP_GATHER[0] + (i * 53) % 380
                dur = 360 + (i * 41) % 140
                u = (tl - st) / dur
                if 0 <= u <= 1:
                    a0 = math.radians(i * 137.5)
                    R0 = 26 + (i % 4) * 6
                    e_ = smooth(u)
                    R = R0 * (1 - e_)
                    a = a0 + 2.4 * e_
                    x = mouth[0] + 4 + R * math.cos(a)
                    y = mouth[1] + R * math.sin(a) * 0.8
                    fig.fx_front.append(ember(fig, x, y, 0.5 + 0.3 * (i % 3), op=min(1, u * 5) * ch))
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(nos[0]), fm(nos[1]), fm(4 + 2 * ch), g_rad(
                fig, nos, 4 + 2 * ch, [(0, LAVA[1], 0.8 * ch), (0.5, LAVA[2], 0.35 * ch), (1, LAVA[3], 0)])))
        # le jet de feu : il sort de la gueule et file jusqu'à l'ennemi, puis s'éteint de la gueule vers l'ennemi
        if SP_EMERGE <= tl < SP_STOP[1] + 40:
            s1 = smooth((tl - SP_EMERGE) / (SP_REACH - SP_EMERGE))
            s0 = smooth((tl - SP_STOP[0]) / (SP_STOP[1] - SP_STOP[0])) if tl > SP_STOP[0] else 0.0
            if s1 - s0 > 0.02:
                m = (mouth[0] + 1.0, mouth[1] + 0.6)
                cen, ws, at = stream_shape(m, s0, s1, tl)
                outer = limb(cen, ws)
                mid_ = limb(cen, [w * 0.62 for w in ws])
                core = limb(cen, [w * 0.3 for w in ws])
                go = g_lin(fig, cen[0], cen[-1], [(0, LAVA[2]), (0.5, LAVA[3]), (1, LAVA[4])])
                gm = g_lin(fig, cen[0], cen[-1], [(0, LAVA[1]), (0.6, LAVA[2]), (1, LAVA[3])])
                gc = g_lin(fig, cen[0], cen[-1], [(0, '#ffffff'), (0.5, LAVA[0]), (1, LAVA[1])])
                fig.fx_front.append(outlined([(outer, go, 1), (mid_.move(0.3, -0.4), gm, 0.95), (core.move(0.5, -0.6), gc, 0.9)], w=1.4))
                # des bouffées de feu sur les bords du jet (elles le rendent vivant, tailles et places inégales)
                for j in range(7):
                    s = s0 + (s1 - s0) * ((j * 0.37 + tl / 420.0) % 1.0)
                    p = at(s)
                    side = 1 if j % 2 else -1
                    r = (1.4 + 3.6 * s) * (0.8 + 0.2 * math.sin(j * 1.7 + tl / 50.0))
                    fig.fx_front.append(fireball(fig, p[0] + 0.6 * side, p[1] + side * (2 + 6 * s), r, op=0.95))
                # des braises qui s'échappent du jet
                for j in range(6):
                    s = s0 + (s1 - s0) * ((j * 0.29 + tl / 600.0) % 1.0)
                    p = at(s)
                    fig.fx_front.append(ember(fig, p[0] + 3 * math.sin(j * 2 + tl / 70), p[1] - 6 - 8 * ((tl / 500.0 + j * 0.3) % 1.0), 0.55))
        # le feu enveloppe l'ennemi : un éclat, une gerbe de langues de feu, des gouttes de feu, la fumée qui monte
        if tl >= SP_REACH - 20:
            tg = tl - SP_HIT
            X, Y = FOE
            fl = env(tl - SP_REACH, -20, 20, 60, 200) * 0.6 + env(tg, -20, 0, 40, 180)
            if fl > 0:
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(X), fm(Y), fm(70), g_rad(
                    fig, (X, Y), 70, [(0, '#ffffff', 0.7 * min(1, fl)), (0.18, LAVA[1], 0.5 * min(1, fl)), (0.5, LAVA[2], 0.15 * min(1, fl)), (1, LAVA[3], 0)])))
            sc = env(tl, SP_REACH, SP_REACH + 120, SP_HIT + 260, SP_HIT + 620)
            if sc > 0:
                burst(fig, (X, Y + 2), sc, 1.25, tl)
                for j, (dx, hh, ww, bd) in enumerate(((-11, 13, 5.6, 0.7), (10, 8, 4.4, -0.6), (19, 5, 3.4, 0.6))):
                    flick = 1 + 0.08 * math.sin(tl / 26.0 + j * 2.3)
                    (fig.fx_front if j == 0 else fig.fx_back).append(tongue(fig, (X + dx, GR), hh * sc * flick, ww * (0.6 + 0.4 * sc), bend=bd))
            for j, (vx, vy) in enumerate(((-70, -150), (60, -170), (-110, -80), (115, -95), (-25, -200), (30, -185), (-140, -30), (150, -40))):
                tau = (tg - 20 * (j % 3)) / 1000.0
                if 0 <= tau < 0.8:
                    x, y = ballistic((X, Y), (vx, vy), 300, tau)
                    if y < GR - 0.5:
                        fig.fx_front.append(spark(fig, x, y, vx, vy + 300 * tau, 1.3 if j % 2 else 1.0))
            fk = (tg - 140) / 1000.0
            if 0 < fk < 1.1:
                o = env(fk, 0, 0.15, 0.6, 1.1)
                for j, (dx, rr, sp) in enumerate(((-8, 5.0, 26), (6, 6.0, 34), (16, 4.0, 22), (-18, 3.6, 18))):
                    fig.fx_back.append(smoke(fig, X + dx + 4 * fk, Y - 10 - sp * fk, rr * (0.8 + 0.6 * fk), op=0.85 * o))
                for j, (dx, sp) in enumerate(((-10, 36), (6, 46), (18, 30), (-22, 26), (0, 54))):
                    fig.fx_front.append(ember(fig, X + dx + 2 * math.sin(fk * 8 + j), Y - 8 - sp * fk, 0.6, op=o))
        # la fumée qui sort des naseaux après le souffle
        tau = (tl - 1420) / 1000.0
        if 0 < tau < 0.9:
            for j in range(3):
                k = tau - j * 0.18
                if 0 < k < 0.6:
                    fig.fx_front.append(smoke(fig, nos[0] - 2 - 14 * k, nos[1] - 3 - 10 * k, 1.2 + 2.6 * k, op=0.8 * (1 - k / 0.6)))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre, une ombre douce
    sous le héros (comme la vidéo d'Elvyn)."""
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
    cx = (50 - x0) * k
    sd.ellipse([cx - 46 * k, fy - 3.0 * k, cx + 46 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def timeline():
    """La suite de la vidéo : repos ×2, attaque ×2, spéciale ×1 (comme Elvyn)."""
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
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    return E.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
        arg = sys.argv[sys.argv.index('--planche') + 1] if len(sys.argv) > sys.argv.index('--planche') + 1 else ''
        if arg:
            moments = [float(v) for v in arg.split(',')]
        else:
            moments = [1.0, a_s + 0.13, a_s + 0.34, a_s + 0.40, a_s + 0.47, a_s + 0.6,
                       s_s + 0.42, s_s + 0.7, s_s + 0.85, s_s + 1.0, s_s + 1.2, s_s + 1.3, s_s + 1.5, s_s + 1.7]
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
