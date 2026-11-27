# Le grand boss de feu vectoriel ANIMÉ (refonte des monstres, 27/11/2026) : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/dragon/build.py) — respiration, attaque de base « Coup de griffe », attaque spéciale
# « Tempête de feu » — dans le style lisse de l'interface (même méthode que ../../heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/dragon/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/dragon/)
#   python3 refonte-graphique/ui-moderne/monstres/dragon/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (dragon.py) est fait de morceaux posés par un squelette : l'arrière du corps reste planté, l'avant
# (poitrail, épaules, cou) avance, recule ou se cabre autour des hanches, et le corps se déforme en douceur entre les
# deux (aucune couture) ; la tête tourne autour de la nuque, la mâchoire autour de sa charnière ; les pattes sont posées
# par cinématique inverse (les pieds restent collés au sol) ; la patte avant proche se lève pour le coup de griffe ; les
# ailes s'ouvrent par leur squelette (bras, coude, poignet, trois doigts). Poses clés du pixel art, mêmes temps lourds
# (longue préparation, coup très court, retour lent), reliées par des courbes douces sans dépassement (24 images/s).
# Effets dans le même style : dégradés, un seul contour, aucun flou SVG, jamais de rayons droits répétés.
#   Repos : il respire lentement (le dos et les épaules montent, le four s'avive), la tête suit avec retard, le bout des
#   ailes traîne, la queue se balance, un filet de fumée sort de la narine à l'expiration, il cligne.
#   Coup de griffe : il reporte son poids en arrière, lève la patte avant haut devant le poitrail (griffes ouvertes),
#   tient, puis la rabat d'un coup en arc devant lui (croissant de braise), frappe le sol (poussière, éclats) ; sur le
#   héros visé, trois griffures de lave courbes se tracent, brillent puis refroidissent en braises.
#   Tempête de feu : il se ramasse, se cabre, DÉPLOIE ses ailes, le four chauffe jusqu'au blanc, des braises montent, la
#   fumée sort des naseaux, des flammes lèchent la gueule ; il jette la tête vers le ciel et crache une boule de feu qui
#   monte en tournant (coup d'ailes) ; une pluie de blocs de lave enflammés tombe en biais sur le héros ; gerbe de
#   flammes, lave et roche projetées, le feu brûle encore puis se défait en fumée ; il replie ses ailes et se repose.
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
import dragon as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, mapp, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'dragon')
TMP = os.environ.get('VECTO_TMP', '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-dragon') + '/_anim'
LAVA = K.LAVA
FPS = 24
VIEW = (-60, -56, 537, 302)          # la scène de la vidéo, en pixels du dessin (16/9) : l'aile grande ouverte y tient
VW, VH = 1280, 720
FINK = '#3a0c18'                     # le contour des flammes et de la lave
GR = K.GRD
TARGET = (383.0, 236.0)              # les pieds du héros visé (même écart qu'au combat : 255 pixels du dessin)
HIT_C = (TARGET[0] + 2, TARGET[1] - 52)   # le milieu du héros (là où tombent les griffures)

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


PAW0 = (K.LEG_N_FRONT['A'][0], K.LEG_N_FRONT['A'][1], 0.0, 1.0)
NUM = ['fx', 'fy', 'fr', 'sq', 'hx', 'hy', 'ht', 'jaw', 'tail', 'wu', 'flap', 'lagx', 'lagy', 'heat', 'px', 'py', 'pf', 'ps',
       'pon']


def flat(k):
    d = dict(fx=0, fy=0, fr=0, sq=0, hx=0, hy=0, ht=0, jaw=0, tail=0, wu=0, flap=0, lagx=0, lagy=0, heat=0,
             px=PAW0[0], py=PAW0[1], pf=PAW0[2], ps=PAW0[3], pon=0)
    for key, v in k.items():
        if key == 'paw':
            d['px'], d['py'], d['pf'], d['ps'] = v
            d['pon'] = 1
        elif key == 'lag':
            d['lagx'], d['lagy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) « Coup de griffe » (pixel : ATTAQUE, ≈ 1,3 s) : poids en arrière, patte avant levée haut devant le poitrail, plante
# vers l'ennemi, griffes ouvertes ; elle tient ; puis elle s'abat en arc devant lui et frappe le sol ; il tient ; retour.
ATTACK = [
    (0, {}),
    (180, dict(fx=-2, fr=-1.0, hx=-0.4, hy=0.2, ht=-0.8, jaw=2, heat=0.6, paw=(176, 198, -40, 1.1), lag=(1, 0.5), tail=0.6)),
    (380, dict(fx=-3.2, fr=-2.6, hx=-0.8, hy=-0.4, ht=-2.0, jaw=5, heat=1.2, paw=(199, 153, -82, 1.6), lag=(1.6, 1), tail=1)),
    (560, dict(fx=-3.4, fr=-2.8, hx=-0.9, hy=-0.5, ht=-2.2, jaw=5.5, heat=1.4, paw=(201, 150, -86, 1.65), lag=(1.8, 1.1), tail=1)),
    (640, dict(fx=1.2, fr=0.4, hx=0.2, hy=0.4, ht=0.2, jaw=7, heat=1.2, paw=(208, 184, -30, 1.3), lag=(-1, -0.5), tail=0)),
    (700, dict(fx=3.6, fr=2.0, hx=0.6, hy=1.2, ht=1.8, jaw=8, heat=1.0, paw=(197, 214, 4, 1.0), lag=(-2.2, -1.2), tail=-1)),
    (900, dict(fx=3.4, fr=1.9, hx=0.6, hy=1.2, ht=1.7, jaw=7, heat=0.9, paw=(197, 214, 4, 1.0), lag=(-1.6, -0.8), tail=-1)),
    (1080, dict(fx=1.8, fr=0.8, hx=0.3, hy=0.6, ht=0.8, jaw=3.5, heat=0.5, paw=(186, 206, -12, 1.0), lag=(0.6, 0.3), tail=-0.4)),
    (1260, dict(fx=0.3, hy=0.1, jaw=1, heat=0.2, paw=(171, 214, 0, 1.0))),
    (1400, {}),
]
ATTACK_HIT = 700

# 3) « Tempête de feu » (pixel : SPECIALE, ≈ 3,7 s).
SPECIAL = [
    (0, {}),
    (260, dict(sq=3, fr=1.6, fx=-1, hy=1.5, ht=3, jaw=-4, heat=1, wu=0.12, lag=(1.5, 1), tail=1)),
    (420, dict(sq=2.4, fr=0, fx=-1.5, hy=0.5, ht=0, jaw=0, heat=1.4, wu=0.35, tail=1)),
    (720, dict(sq=-0.5, fr=-8.5, fx=-2.5, fy=-2.5, hx=-1, hy=-3, ht=-12, jaw=8, heat=2.6, wu=0.95, flap=-6, tail=1.5)),
    (1050, dict(sq=-0.6, fr=-9.2, fx=-2.6, fy=-2.8, hx=-1.2, hy=-3.4, ht=-14, jaw=9, heat=3, wu=1.0, flap=-14, tail=1.5)),
    (1180, dict(sq=-0.8, fr=-10, fx=-2.0, fy=-3, hx=-0.5, hy=-5, ht=-30, jaw=16, heat=3, wu=1.0, flap=-4, tail=1)),
    (1300, dict(sq=0.4, fr=-8, fx=-1.5, fy=-2.5, hx=0, hy=-4, ht=-26, jaw=14, heat=2.4, wu=1.0, flap=18, tail=0)),
    (1520, dict(sq=0.2, fr=-7, fx=-1.5, fy=-2.2, hx=0, hy=-3, ht=-16, jaw=8, heat=2.0, wu=1.0, flap=4, tail=0.4)),
    (2450, dict(sq=0, fr=-6, fx=-1.2, fy=-2, hy=-2.4, ht=-10, jaw=7, heat=1.6, wu=0.95, flap=-4, tail=0.6)),
    (3000, dict(sq=1.4, fr=-1, fx=-0.4, fy=-0.4, hy=0.6, ht=1, jaw=2, heat=0.8, wu=0.2, flap=0, lag=(1.2, 1.4), tail=0.2)),
    (3350, dict(sq=0.6, heat=0.3, wu=0.0, lag=(0.4, 0.5))),
    (3700, {}),
]
SP_SPIT = 1180            # la boule de feu part
SP_RAIN = (2050, 2300)    # les blocs de lave arrivent sur le héros (premier, dernier)


# ======================================================================== la respiration (en boucle, 2,6 s)

def idle_offsets(T):
    u = 2 * math.pi * T / 2.6
    br = 0.5 - 0.5 * math.cos(u)
    return dict(br=br, hy=0.25 * math.sin(u - 0.9), ht=0.3 * math.sin(u - 1.1), jaw=0.6 * math.sin(u - 0.6),
                tail=1.2 * math.sin(u * 0.5 + 0.4), lagx=0.6 * math.sin(u - 1.6), lagy=0.8 * math.sin(u - 1.6),
                heat=0.5 * br, fx=0.15 * math.sin(u - 0.3))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w, act, tl = 1.0, None, 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['br'] = w * idl['br']
    P['lag'] = (P.pop('lagx'), P.pop('lagy'))
    on = P.pop('pon')
    paw = (P.pop('px'), P.pop('py'), P.pop('pf'), P.pop('ps'))
    P['paw'] = paw if on > 0.01 else None
    P['ph'] = 2 * math.pi * T
    P['blink'] = 1.0 if (w > 0.95 and 1.9 <= (T % 4.4) < 1.98) else 0.0
    P['wu'] = max(0.0, P['wu'])
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=FINK, w=1.5, op=1.0):
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, _, _ in shapes_fills if _ is not None) if w > 0 else ''
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0.0, min(1.0, op)), sil, col)


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True, up=(0.0, -1.0)):
    """Une langue de feu : large et pâle à la base, fine et rouge au bout, en S (vers `up`)."""
    if h < 0.6 or op <= 0.02:
        return ''
    bx, by = base
    ux, uy = up
    nx, ny = -uy, ux
    P_ = lambda a, b: (bx + ux * a + nx * b, by + uy * a + ny * b)
    p0 = (bx, by)
    p1 = P_(h * 0.33, bend * w * 0.5 + lean * h * 0.12)
    p2 = P_(h * 0.68, -bend * w * 0.45 + lean * h * 0.55)
    p3 = P_(h, lean * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95)], w=1.4 if ink else 0, op=op)


def ember(fig, x, y, r=0.8, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, LAVA[2], 0.6 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte de lave : ronde devant, effilée derrière (dans le sens de sa course)."""
    a = math.atan2(vy, vx)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.8, y - math.sin(a) * r * 2.8)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.35, r * 0.25), LAVA[0], 0.9)], w=1.1, op=op)


def chunk(fig, x, y, s=1.6, rot=0.0, op=1.0, hot=0.0):
    """Un éclat de roche (sa roche, éclairée en haut à droite), une fêlure de lave quand il est chaud."""
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, K.ROCK.light), (0.5, K.ROCK.base), (1, K.ROCK.deep)])
    parts = [(sh, gr, 1)]
    if hot > 0.05:
        v = [(x - s * 0.6 * c, y - s * 0.6 * si), (x, y), (x + s * 0.5 * si, y - s * 0.5 * c)]
        parts.append((ribbon(v, [0.1, s * 0.32, 0.1]), LAVA[2], min(1, hot)))
    return outlined(parts, ink=K.FIG_INK if hasattr(K, 'FIG_INK') else '#1f1238', w=1.0, op=op)


def smoke(fig, cx, cy, r, op=1.0):
    """Une bouffée de fumée : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#f2e8e6'), (0.5, '#c4b2bc'), (1, '#86708a')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def dust(fig, cx, cy, r, op=1.0):
    """Un nuage de poussière (au sol) : comme la fumée, en tons de pierre chaude."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.9 * r, cy + 0.3 * r, 0.7 * r), (cx - 0.9 * r, cy + 0.3 * r, 0.75 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, '#eed8bc'), (0.5, '#b8987e'), (1, '#7a6070')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3656" stroke="#4a3656" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


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


def rnd(i, k=0):
    """Un hasard fixe (le même à chaque rendu)."""
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)


# ---- les repères de la tête (gueule, narine) et de la patte

def lerp_(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def head_pt(ctx, p):
    return mapp(ctx['R'].HEAD, p)


def jaw_pt(ctx, p):
    return mapp(ctx['R'].JAW, p)


# ---- le repos : un filet de fumée sort de la narine à l'expiration

def fx_idle(T):
    def f(fig, ctx):
        u = (T % 2.6) / 2.6
        nose = head_pt(ctx, (251.5, 95.0))
        for k in range(3):
            s_ = (u - 0.55 - 0.08 * k)
            if 0 < s_ < 0.5:
                a = s_ / 0.5
                fig.fx_front.append(smoke(fig, nose[0] + 2 + 9 * a + 1.5 * math.sin(a * 5 + k), nose[1] - 2 - 14 * a,
                                          0.9 + 2.0 * a, op=0.55 * (1 - a) * min(1, a * 5)))
    return f


# ---- l'attaque de base : le croissant de la griffe, la poussière, les griffures sur le héros

def fx_attack(tl):
    def f(fig, ctx):
        pts = ctx['paw']
        A = pts['A']
        # le croissant de braise derrière les griffes pendant le coup (de la patte levée au sol)
        k = env(tl, 580, 640, 690, 780)
        if k > 0:
            C = (172.0, 198.0)
            a1 = math.degrees(math.atan2(A[1] - C[1], A[0] - C[0])) + 8
            R = math.dist(C, A) + 12
            a0 = a1 - 70 * min(1, (tl - 560) / 120)
            body = arc_band(C, R, a0, a1, 10.0)
            rim = arc_band(C, R + 1.2, a0, a1, 2.6)
            pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
            pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
            g1 = g_lin(fig, pa, pb, [(0, LAVA[3], 0), (0.5, LAVA[2], 0.6 * k), (1, LAVA[1], 0.9 * k)])
            g2 = g_lin(fig, pa, pb, [(0, LAVA[4], 0), (0.6, LAVA[3], 0.85 * k), (1, LAVA[0], k)])
            fig.fx_front.append('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2))
        # l'impact au sol : poussière et éclats devant la patte
        if tl >= ATTACK_HIT:
            t = (tl - ATTACK_HIT) / 1000
            x0 = 224.0
            for j in range(3):
                r = 2.5 + 9 * (1 - math.exp(-t * 6)) * (0.7 + 0.3 * j)
                fig.fx_front.append(dust(fig, x0 - 10 + 11 * j, GR - 2 - 2.5 * t * 10 * (0.4 + 0.2 * j), r * 0.75,
                                         op=0.8 * env(tl, ATTACK_HIT, ATTACK_HIT + 40, ATTACK_HIT + 200, ATTACK_HIT + 600)))
            for j in range(4):
                p = ballistic((x0 - 4 + 4 * j, GR - 3), (14 + 18 * rnd(j, 1), -48 - 26 * rnd(j, 2)), 180, t)
                if p[1] < GR:
                    fig.fx_front.append(chunk(fig, p[0], p[1], 1.9 + 0.7 * rnd(j, 3), rot=t * 500 * (1 + j), op=1))
        # sur le héros visé : trois griffures de lave courbes, qui se tracent, brillent, refroidissent
        if tl >= ATTACK_HIT - 20:
            fig.fx_front.append(claw_marks(fig, tl - (ATTACK_HIT - 20)))
    return f


def claw_marks(fig, t):
    out = []
    cx, cy = HIT_C
    for j, (dx, L, w) in enumerate(((-10.0, 36.0, 3.4), (0.0, 44.0, 3.9), (10.0, 35.0, 3.3))):
        d0 = 22 * j
        r = max(0.0, min(1.0, (t - d0) / 90))
        if r <= 0:
            continue
        hot = 1 - max(0.0, min(1.0, (t - 260 - d0) / 420))
        op = 1 - max(0.0, min(1.0, (t - 520 - d0) / 280))
        if op <= 0.02:
            continue
        a0 = (cx + dx + 10, cy - L / 2)
        pts = []
        for i in range(13):
            s_ = i / 12 * r
            pts.append((a0[0] - 26 * s_ + 5 * math.sin(math.pi * s_), a0[1] + L * s_))
        ws = [0.2] + [w * math.sin(math.pi * (i / 12)) ** 0.6 + 0.3 for i in range(1, 12)] + [0.2]
        halo = ribbon(pts, [x * 2.4 for x in ws])
        core = ribbon(pts, ws)
        hotc = ribbon(pts, [x * 0.42 for x in ws])
        out.append('<g opacity="%g"><path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
            op, halo.d(), LAVA[3], 0.35 * hot + 0.1, core.d(), LAVA[4] if hot > 0.3 else '#6a1a22', hotc.d(),
            LAVA[0] if hot > 0.6 else (LAVA[2] if hot > 0.2 else LAVA[4])))
        # les étincelles au bout de la griffure qui se trace
        if 0 < r < 1:
            p = pts[-1]
            out.append(ember(fig, p[0] - 1.5, p[1] + 1, 0.9))
        elif hot > 0:
            for k in range(2):
                u = (t - 120 - d0 - 60 * k) / 600
                if 0 < u < 1:
                    p = pts[int(4 + 4 * k)]
                    out.append(ember(fig, p[0] + 3 * u, p[1] - 10 * u, 0.7, op=1 - u))
    return ''.join(out)


# ---- l'attaque spéciale

def fireball(fig, c, r, ang, v, op=1.0):
    """La boule de feu : un coeur blanc, des langues de feu qui tournent autour et traînent derrière (vitesse v)."""
    out = []
    sp = math.hypot(*v) or 1
    back = (-v[0] / sp, -v[1] / sp)
    for k in range(5):
        a = math.radians(ang + 72 * k)
        off = (math.cos(a) * r * 0.55, math.sin(a) * r * 0.55)
        base = (c[0] + off[0], c[1] + off[1])
        dirn = (back[0] * 0.8 + off[0] / r * 0.6, back[1] * 0.8 + off[1] / r * 0.6)
        L = math.hypot(*dirn) or 1
        out.append(tongue(fig, base, r * (1.6 + 0.6 * math.sin(a * 2 + ang * 0.05)), r * 0.9, bend=0.6 * math.sin(a),
                          op=op, up=(dirn[0] / L, dirn[1] / L)))
    ball = ellipse(c[0], c[1], r, r)
    gr = g_rad(fig, (c[0] + r * 0.25, c[1] - r * 0.25), r * 1.1, [(0, LAVA[0]), (0.35, LAVA[1]), (0.7, LAVA[2]), (1, LAVA[3])])
    out.append(g_glow(fig, c, r * 3.0, 0.5 * op))
    out.append(outlined([(ball, gr, 1)], w=1.5, op=op))
    return ''.join(out)


def g_glow(fig, c, r, op):
    gid = g_rad(fig, c, r, [(0, LAVA[2], op), (0.5, LAVA[3], op * 0.4), (1, LAVA[3], 0)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), gid)


def lava_block(fig, c, s, rot, v, op=1.0):
    """Un bloc de lave enflammé qui tombe : sa traînée de flammes derrière lui, le bloc de roche fendu de lave."""
    sp = math.hypot(*v) or 1
    back = (-v[0] / sp, -v[1] / sp)
    out = [g_glow(fig, c, s * 3.2, 0.45 * op)]
    for k, (o, h) in enumerate(((-0.4, 3.4), (0.35, 2.8), (0.0, 4.2))):
        base = (c[0] + back[1] * o * s, c[1] - back[0] * o * s)
        out.append(tongue(fig, base, s * h, s * 1.3, bend=0.5 * (k - 1), op=op, up=back))
    out.append(chunk(fig, c[0], c[1], s, rot=rot, op=op, hot=1.0))
    return ''.join(out)


RAIN = [  # (instant de l'impact en ms, décalage en x au sol, taille)
    (SP_RAIN[0], -12.0, 5.8), (SP_RAIN[0] + 120, 10.0, 5.2), (SP_RAIN[1], -1.0, 6.6)]
RAIN_V = (190.0, 520.0)        # la vitesse des blocs (ils tombent en biais, venus du haut, côté dragon)


def fx_special(tl):
    def f(fig, ctx):
        R = ctx['R']
        chest = mapp(R.F, (192, 150))
        # la charge : des braises montent du four ; la fumée sort des naseaux ; des flammes lèchent la gueule
        ch = env(tl, 300, 650, 1150, 1400)
        if ch > 0:
            for j in range(9):
                u = ((tl - 300) / 1000 * (0.7 + 0.4 * rnd(j, 5)) + rnd(j, 6)) % 1.0
                x = chest[0] - 18 + 36 * rnd(j, 7) + 6 * math.sin(u * 6 + j)
                y = chest[1] + 20 - 70 * u
                fig.fx_front.append(ember(fig, x, y, 0.7 + 0.4 * rnd(j, 8), op=ch * (1 - u) * min(1, u * 6)))
            nose = head_pt(ctx, (251.5, 95.0))
            for k in range(3):
                u = ((tl - 300) / 700 + k / 3) % 1.0
                fig.fx_front.append(smoke(fig, nose[0] + 3 + 10 * u, nose[1] - 3 - 16 * u, 1.0 + 2.6 * u, op=0.6 * ch * (1 - u)))
            m0 = jaw_pt(ctx, (236, 112))
            m1 = head_pt(ctx, (240, 110))
            for k in range(3):
                b = ((m0[0] + m1[0]) / 2 - 6 + 7 * k, (m0[1] + m1[1]) / 2)
                fig.fx_front.append(tongue(fig, b, (9 + 3 * math.sin(tl / 70 + k * 2)) * ch, 4.8 * ch, bend=0.6 * math.sin(tl / 90 + k),
                                           up=(0.55, -0.83), op=ch))
        # la boule de feu : elle part de la gueule et monte en tournant au-dessus des héros
        if SP_SPIT - 20 <= tl <= SP_SPIT + 700:
            t = (tl - SP_SPIT) / 1000
            if 'p0' not in SPIT:
                SPIT['p0'] = lerp_(head_pt(ctx, (244, 110)), jaw_pt(ctx, (244, 111)), 0.5)
            p0 = SPIT['p0']
            p = ballistic(p0, (150, -310), 120, max(0, t))
            v = (150, -310 + 120 * max(0, t))
            r = 6 + 8 * min(1, max(0, t) * 5)
            fig.fx_front.append(fireball(fig, p, r, tl * 0.9, v, op=1.0))
        # la pluie de blocs de lave sur le héros
        for j, (ti, dx, s) in enumerate(RAIN):
            t = (tl - ti) / 1000
            if -0.62 < t < 0:
                hit = (TARGET[0] + dx, GR - 2)
                c = (hit[0] + RAIN_V[0] * t, hit[1] + RAIN_V[1] * t)
                fig.fx_front.append(lava_block(fig, c, s, tl * 0.6 + 90 * j, RAIN_V))
            if 0 <= t < 1.4:
                fig.fx_front.append(impact(fig, (TARGET[0] + dx, GR), t, j, s))
        # le feu qui brûle encore sur le héros (la brûlure), puis la fumée
        b = env(tl, SP_RAIN[0] + 60, SP_RAIN[0] + 260, SP_RAIN[1] + 700, SP_RAIN[1] + 1250)
        if b > 0:
            for k in range(5):
                x = TARGET[0] - 22 + 11 * k
                h = (17 + 7 * math.sin(tl / 85 + k * 1.7) + 6 * rnd(k, 9)) * b
                fig.fx_front.append(tongue(fig, (x, GR), h, 6.4 * b, bend=0.7 * math.sin(tl / 110 + k), lean=0.15 * math.sin(tl / 150 + k), op=1))
        sm_ = env(tl, SP_RAIN[1] + 300, SP_RAIN[1] + 650, SP_RAIN[1] + 1000, SP_RAIN[1] + 1380)
        if sm_ > 0:
            for k in range(4):
                u = ((tl - SP_RAIN[1] - 300) / 900 + k / 4) % 1.0
                fig.fx_front.append(smoke(fig, TARGET[0] - 10 + 7 * k + 5 * math.sin(u * 4 + k), GR - 10 - 46 * u, 2 + 4 * u,
                                          op=0.65 * sm_ * (1 - u) * min(1, u * 5)))
    return f


SPIT = {}


def impact(fig, p, t, j, s):
    """L'impact d'un bloc : gerbe de flammes courbes, lave et roche projetées, sol qui rougeoie."""
    out = []
    k = env(t * 1000, 0, 40, 220, 700)
    if k > 0:
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(p[0]), fm(p[1] - 0.5), fm(24 * k + 6), fm(4.2), g_rad(fig, p, 24 * k + 6, [(0, LAVA[1], 0.9 * k), (1, LAVA[3], 0)])))
        for i, (o, h, w, ln) in enumerate(((-14, 20, 6.6, -0.5), (-5, 34, 8.4, -0.15), (6, 29, 7.6, 0.2), (15, 17, 6.0, 0.55))):
            hh = h * k * (0.9 + 0.2 * math.sin(t * 30 + i))
            out.append(tongue(fig, (p[0] + o, p[1]), hh, w * k, bend=0.6 * math.sin(i + t * 12), lean=ln))
    for i in range(4):
        pp = ballistic((p[0], p[1] - 3), ((-30 + 22 * i) * (0.8 + 0.4 * rnd(i, j)), -70 - 40 * rnd(i, j + 3)), 260, t)
        if pp[1] < p[1] and t < 0.8:
            if i % 2:
                out.append(drop(fig, pp[0], pp[1], (-30 + 22 * i), -70 + 260 * t, r=1.6))
            else:
                out.append(chunk(fig, pp[0], pp[1], 2.0, rot=t * 600 + i * 40, hot=1 - t))
    return ''.join(out)


# ======================================================================== la scène

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus, une dalle d'un bord à l'autre, une ombre douce sous le boss et
    sous le héros."""
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
    for cx_, rx in ((120, 118), (TARGET[0], 30)):
        cx = (cx_ - x0) * k
        sd.ellipse([cx - rx * k, fy - 4 * k, cx + rx * k, fy + 4 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
    return im


def hero_layer(w, h, view):
    """Le héros visé (Kael vectoriel, retourné vers le dragon), à la même échelle, posé à sa place."""
    x0, y0, vw, vh = view
    k = w / vw
    src = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', 'assassins-2.webp')).convert('RGBA')
    fw, fh, ffx, ffy = 133, 122, 67, 120        # sa table VECTO
    s = (fh * k) / src.height
    im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    lay = Image.new('RGBA', (w, h))
    px = (TARGET[0] - x0) * k - (fw - ffx) * k
    py = (TARGET[1] - y0) * k - ffy * k
    lay.alpha_composite(im, (round(px), round(py)))
    return lay


def timeline():
    seq = [('idle', 3.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.2),
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
    if act == 'attack':
        fx = [fx_attack((T - t0) * 1000)]
    elif act == 'special':
        fx = [fx_special((T - t0) * 1000)]
    else:
        SPIT.clear()
        fx = [fx_idle(T)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        moments = [0.5, 1.6, a_s + 0.38, a_s + 0.6, a_s + 0.66, a_s + 0.72, a_s + 0.85, a_s + 1.1,
                   s_s + 0.26, s_s + 0.72, s_s + 1.05, s_s + 1.2, s_s + 1.35, s_s + 1.55, s_s + 1.68, s_s + 1.76,
                   s_s + 1.9, s_s + 2.2, s_s + 2.7, s_s + 3.1]
        if len(sys.argv) > 2:
            moments = [float(x) for x in sys.argv[2].split(',')]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        hero = hero_layer(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(hero)
            im.alpha_composite(Image.open(p))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, '..', 'planche.png')
        sheet.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    bg.alpha_composite(hero_layer(VW, VH, VIEW))
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
