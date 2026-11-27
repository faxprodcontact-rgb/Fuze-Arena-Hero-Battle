# Golem de lave vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/golem-lave/
# build.py) — la respiration du volcan, l'attaque de base « Coup de massue », l'attaque spéciale « Faille de magma » —
# dans le style lisse de l'interface (comme Kael et Garvin : heros/kael/anim.py, heros/garvin/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/golem-lave/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/golem-lave/)
#   python3 refonte-graphique/ui-moderne/monstres/golem-lave/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#   (images de travail : dans $GOLEM_TMP, sinon un dossier temporaire du système ; jamais dans le dépôt)
#
# Méthode : chaque image redessine golem-lave.py dans une POSE (le haut du corps respire par la bosse et bascule d'un
# bloc depuis les hanches, la tête suit avec du retard, les piliers plient, les pieds restent à plat ; le bras-massue
# suit son poignet par cinématique inverse et plie au vrai coude, la massue tourne autour du poignet ; le petit bras
# se balance avec du retard). C'est un colosse sans cou, lourd du haut : très longues préparations, impacts courts et
# tenus, retours lents ; il ne quitte jamais le sol. Poses clés et durées reprises du pixel art, reliées par des
# courbes douces sans dépassement, 24 images/s.
# Effets (bulle et fontaine du cratère, goutte de la griffe, traînée de la massue, flammes de la massue, poussière,
# éclats, gouttes, faille et geysers de lave, fumée) : dégradés, un seul contour par objet, aucun flou ; jamais de
# rayons droits répétés.
import importlib.util
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('golem', os.path.join(HERE, 'golem-lave.py'))
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)
from atelier import sm, ribbon, ellipse, lock, f as fm, mapp  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'golem-lave')
TMP = os.environ.get('GOLEM_TMP') or os.path.join(tempfile.gettempdir(), 'golem-lave-anim')
FPS = 24
VIEW = (-30, -40, 300, 168.75)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
FINK = '#3a0c18'                     # le contour de la lave
INK = '#1f1238'                      # le contour de la roche
LAVA = K.LAVA
ROCK = K.ROCK

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
SCAL = ['crouch', 'lean', 'tilt', 'glow', 'heat', 'gape', 'frot', 'a3', 'inhale', 'crater', 'drip', 'shake']
NUM = SCAL + [k for v in PAIRS.values() for k in v]
BASE = dict(fw=K.FW0, nw=K.NW0, a3=90.0, drip=0.35)


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
# 2) « Coup de massue » (pixel : ATTAQUE, 1,72 s). Il arrache la massue du sol et la soulève en arrière (il se cabre,
# le haut du corps bascule vers l'arrière) ; longue attente, massue haute derrière la bosse ; puis il bascule d'un bloc
# vers l'avant et l'abat devant lui (la massue passe par-dessus la bosse) : elle s'écrase au sol, tout tremble, la
# poussière roule au ras du sol, des éclats de roche et des gouttes de lave sautent. Impact tenu ; puis il traîne la
# massue en arrière et se redresse lentement. nw = où est le poignet ; a3 = l'axe de la massue (degrés, 90 = vers le
# bas ; il tourne dans le sens des aiguilles d'une montre : derrière, en haut, par-dessus, devant).
HIT_W = (56.0, 87.6)              # le poignet au moment du choc (la massue posée devant lui, à plat)
HIT_A = 430.0
ATTACK = [
    (0, {}),
    (140, dict(nw=(15.0, 80.0), a3=112.0, lean=-1.0, tilt=-1.0, crouch=0.8, head=(0.0, 0.8), fw=(113.0, 87.0), frot=6)),
    (270, dict(nw=(3.0, 50.0), a3=172.0, lean=-2.0, tilt=-2.0, crouch=-0.6, head=(-0.3, -0.6), fw=(111.6, 85.6), frot=10, glow=0.5)),
    (390, dict(nw=(9.0, 17.0), a3=236.0, lean=-2.6, tilt=-3.0, crouch=-1.2, head=(-0.4, -0.9), fw=(110.6, 84.4), frot=14, glow=1.0)),
    (750, dict(nw=(10.4, 14.6), a3=242.0, lean=-2.9, tilt=-3.4, crouch=-1.4, head=(-0.5, -1.0), fw=(110.4, 84.0), frot=15, glow=1.2)),
    (800, dict(nw=(52.0, 12.0), a3=330.0, lean=1.0, tilt=1.0, crouch=0.0, head=(0.0, 0.0), fw=(112.4, 86.0), frot=4, glow=1.4, gape=0.4)),
    (850, dict(nw=HIT_W, a3=HIT_A, lean=4.0, tilt=3.0, crouch=3.0, head=(0.7, 1.3), fw=(115.6, 90.6), frot=-8, glow=2.2, gape=1.0,
               shake=1.0)),
    (1050, dict(nw=(HIT_W[0] + 0.4, HIT_W[1] + 0.3), a3=HIT_A + 1, lean=4.0, tilt=3.2, crouch=3.0, head=(0.7, 1.4), fw=(115.0, 90.4),
                frot=-6, glow=1.6, gape=0.8)),
    (1200, dict(nw=(43.0, 88.0), a3=HIT_A + 10, lean=3.0, tilt=2.2, crouch=2.0, head=(0.5, 1.0), fw=(114.4, 89.4), frot=-3, glow=1.0,
                gape=0.4)),
    (1400, dict(nw=(29.0, 88.0), a3=HIT_A + 17, lean=1.2, tilt=1.0, crouch=1.0, head=(0.2, 0.5), glow=0.5)),
    (1720, dict(a3=450.0)),
]
ATTACK_HIT = 850

# 3) « Faille de magma » (pixel : SPECIALE, 2,3 s). Le volcan se réveille : le cratère bout, puis crache une fontaine
# de lave ; ses fêlures s'allument jusqu'au blanc. Il lève la massue tout droit au-dessus de l'épaule, près du
# cratère : la lave retombe dessus et l'embrase (massue incandescente, flammes). Longue attente. Puis il l'abat devant
# lui dans un croissant de feu : éclair, la massue fend le sol. Une faille de lave court au ras du sol vers l'ennemi
# et, sur son chemin, le sol éclate en trois geysers l'un après l'autre (roche arrachée, gouttes en cloche). Les
# geysers retombent en fumée, la faille refroidit (rouge, puis brun brûlé). Il traîne la massue et se redresse.
SPECIAL = [
    (0, dict(glow=1.0, crater=0.4)),
    (150, dict(nw=(15.0, 80.0), a3=112.0, lean=-1.0, tilt=-1.0, crouch=0.8, head=(0.0, 0.8), glow=1.6, crater=0.7, fw=(113.0, 87.0), frot=6)),
    (300, dict(nw=(5.0, 46.0), a3=180.0, lean=-1.6, tilt=-2.0, crouch=-0.4, head=(-0.2, -0.4), glow=2.2, crater=1.0, fw=(111.6, 85.6), frot=10)),
    (440, dict(nw=(25.0, 5.0), a3=262.0, lean=-1.8, tilt=-2.4, crouch=-1.0, head=(-0.3, -0.8), glow=2.8, heat=0.35, crater=1.0,
               fw=(110.8, 84.6), frot=14)),
    (740, dict(nw=(25.6, 3.6), a3=266.0, lean=-2.0, tilt=-2.6, crouch=-1.2, head=(-0.3, -1.0), glow=3.4, heat=1.0, crater=1.0,
               fw=(110.6, 84.4), frot=15, gape=0.6)),
    (940, dict(nw=(26.0, 3.0), a3=268.0, lean=-2.1, tilt=-2.8, crouch=-1.3, head=(-0.3, -1.0), glow=3.6, heat=1.0, crater=0.8,
               fw=(110.4, 84.2), frot=15, gape=0.8)),
    (990, dict(nw=(58.0, 14.0), a3=340.0, lean=1.0, tilt=1.0, crouch=0.0, head=(0.0, 0.0), glow=3.6, heat=1.0, crater=0.5,
               fw=(112.4, 86.0), frot=4, gape=1.0)),
    (1040, dict(nw=HIT_W, a3=HIT_A, lean=4.2, tilt=3.4, crouch=3.2, head=(0.7, 1.4), glow=4.0, heat=1.0, crater=0.3,
                fw=(115.6, 90.6), frot=-8, gape=1.3, shake=1.0)),
    (1250, dict(nw=(HIT_W[0] + 0.3, HIT_W[1] + 0.3), a3=HIT_A + 1, lean=4.2, tilt=3.4, crouch=3.2, head=(0.7, 1.4), glow=3.4, heat=0.8,
                fw=(115.2, 90.4), frot=-7, gape=1.0)),
    (1600, dict(nw=(HIT_W[0] + 0.6, HIT_W[1] + 0.4), a3=HIT_A + 2, lean=4.0, tilt=3.0, crouch=3.0, head=(0.6, 1.2), glow=2.4, heat=0.45,
                fw=(115.0, 90.2), frot=-6, gape=0.7)),
    (1830, dict(nw=(43.0, 88.0), a3=HIT_A + 10, lean=3.0, tilt=2.2, crouch=2.0, head=(0.5, 1.0), glow=1.6, heat=0.2, fw=(114.4, 89.4),
                frot=-3, gape=0.3)),
    (1990, dict(nw=(29.0, 88.0), a3=HIT_A + 17, lean=1.2, tilt=1.0, crouch=1.0, head=(0.2, 0.5), glow=1.0)),
    (2300, dict(a3=450.0)),
]
SP_HIT = 1040
GEYSERS = [(122.0, 1110), (172.0, 1220), (222.0, 1330)]     # où et quand le sol éclate (ms)

# ======================================================================== la respiration (en boucle)
IDLE = 2.2                           # un souffle (s) : lent et lourd


def bump(x, c, w):
    return math.exp(-((x - c) / w) ** 2)


def breath_at(T):
    return 0.5 - 0.5 * math.cos(2 * math.pi * T / IDLE)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE
    ph = (T / IDLE) % 1
    br = breath_at(T)
    lag = breath_at(T - 0.16)                    # le visage suit avec une image de retard
    beat = 0.8 * bump(ph, 0.42, 0.05) + 1.3 * bump(ph, 0.52, 0.06)      # la lave s'avive à l'inspiration
    # la bulle du cratère gonfle puis crève (une fois par souffle)
    cr = max(0.0, (ph - 0.15) / 0.5) if ph < 0.65 else 0.0
    # la goutte de la griffe : elle grossit pendant deux souffles, tombe, puis renaît
    q = (T / (2 * IDLE)) % 1
    drip = 0.25 + 0.75 * (q / 0.8) if q < 0.8 else max(0.0, (q - 0.9) / 0.1) * 0.25
    return dict(inhale=br, heady=0.9 * (br - lag) * 1.6, crater=cr, drip=drip - 0.35, glow=beat,
                fwx=0.5 * math.sin(u - 1.6), fwy=0.4 * math.sin(u - 1.2), frot=2.0 * math.sin(u - 1.8),
                gape=0.12 + 0.12 * math.sin(u - 1.0), crouch=0.35 * (0.5 - 0.5 * math.cos(u - 2.6)))


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
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
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
    P['crater'] = max(0.0, P['crater']) if w > 0.5 else 0.0
    P['drip'] = max(0.0, P['drip']) if w > 0.5 else 0.35
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % 4.4) < 1.40) else 0.0
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


def ember(fig, x, y, r=0.7, op=1.0):
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.2, [(0, LAVA[2], 0.55 * op), (1, LAVA[3], 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, LAVA[0], op), (0.6, LAVA[1], op), (1, LAVA[3], op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.2), glow, fm(x), fm(y), fm(r), core)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte de lave : ronde devant, effilée derrière (dans le sens de sa course)."""
    a = math.atan2(vy, vx)
    sp = min(1.0, math.hypot(vx, vy) / 40)
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * (1.4 + 1.6 * sp), y - math.sin(a) * r * (1.4 + 1.6 * sp))
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, LAVA[1]), (0.5, LAVA[2]), (1, LAVA[4])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.35, r * 0.25), LAVA[0], 0.9, 'n')], w=1.0, op=op)


CHUNK = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]


def chunk(fig, x, y, s=1.6, rot=0.0, op=1.0, hot=False):
    """Un éclat de roche volcanique (sa roche, éclairée en haut à droite) ; chaud : un cœur de braise."""
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in CHUNK]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, K.LIT), (0.5, ROCK.base), (1, ROCK.deep)])
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


def tongue(fig, base, h, w, bend=0.0, lean=0.0, op=1.0, ink=True, direction=-90.0):
    """Une langue de feu / un jet de lave : large et pâle à la base, fine et rouge au bout, en S."""
    if h < 0.6 or op <= 0.02:
        return ''
    a = math.radians(direction)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bx, by = base

    def P_(along, side):
        return (bx + ux * along + nx * side, by + uy * along + ny * side)
    p0 = P_(0, 0)
    p1 = P_(h * 0.33, bend * w * 0.5 + lean * h * 0.12)
    p2 = P_(h * 0.68, -bend * w * 0.45 + lean * h * 0.55)
    p3 = P_(h, lean * h)
    sh = lock(p0, p1, p2, p3, w, n=10, bulge=0.15)
    q = lambda p, k: (bx + (p[0] - bx) * k, by + (p[1] - by) * k)
    core = lock(p0, q(p1, 0.6), q(p2, 0.6), q(p3, 0.62), w * 0.55, n=8, bulge=0.1)
    gout = g_lin(fig, p0, p3, [(0, LAVA[1]), (0.35, LAVA[2]), (0.72, LAVA[3]), (1, LAVA[4])])
    gin = g_lin(fig, p0, q(p3, 0.62), [(0, LAVA[0]), (0.6, LAVA[1]), (1, LAVA[2])])
    return outlined([(sh, gout, 1), (core, gin, 0.95, 'n')], w=1.3 if ink else 0, op=op)


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


def club_smear(fig, C, R, a0, a1, w, hot=False, op=1.0):
    """La traînée de la massue qui s'abat : un croissant de roche bordé de braise (de feu pour la spéciale)."""
    if abs(a1 - a0) < 4 or w < 0.4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + w * 0.5, a0, a1, w)
    rim = arc_band(C, R + w * 0.5, a0 + (a1 - a0) * 0.3, a1, w * (0.55 if hot else 0.3))
    if hot:
        g1 = g_lin(fig, pa, pb, [(0, LAVA[4], 0.0), (0.5, LAVA[3], 0.75), (1, LAVA[2], 0.95)])
        g2 = g_lin(fig, pa, pb, [(0, LAVA[2], 0.0), (0.6, LAVA[1], 0.9), (1, LAVA[0], 1)])
    else:
        g1 = g_lin(fig, pa, pb, [(0, '#56404e', 0.0), (0.5, '#86645a', 0.7), (1, K.LIT, 0.95)])
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


def mix(a, b, t):
    return K.mix(a, b, max(0.0, min(1.0, t)))


def ground_crack(fig, x0, x1, heat, seed=0, w=1.0):
    """La faille de lave qui court au sol (elle refroidit : heat 1 → 0, puis brun brûlé) ; une lueur autour."""
    if x1 - x0 < 1:
        return ''
    n = max(3, int((x1 - x0) / 6))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.5 + (0.7 if (i + seed) % 2 else -0.2) * (0 < i < n)) for i in range(n + 1)]
    from outils import crpath
    c = crpath(pts, max(8, n * 3))
    m = len(c)
    halo = ribbon(c, [0.4] + [5.0 * w] * (m - 2) + [0.4])
    core = ribbon(c, [0.2] + [1.8 * w] * (m - 2) + [0.2])
    hot = ribbon(c, [0.1] + [0.8 * w] * (m - 2) + [0.1])
    burnt = '<path d="%s" fill="#5a2a2a" opacity="%g"/>' % (core.d(), 0.9 * (1 - min(1, heat * 2)))
    if heat <= 0.02:
        return burnt
    gh = g_lin(fig, (x0, GR), (x1, GR), [(0, LAVA[2], 0.45 * heat), (1, LAVA[3], 0.15 * heat)])
    return burnt + '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="%g"/><path d="%s" fill="%s" opacity="%g"/>' % (
        halo.d(), gh, core.d(), LAVA[4], min(1, heat * 1.4), hot.d(), LAVA[1] if heat > 0.5 else LAVA[2], min(1, heat * 1.2))


def geyser(fig, x, k, seed=0):
    """Un geyser de lave qui éclate du sol (k : 0 → 1 sur sa vie) : trois langues qui jaillissent, retombent."""
    out = []
    up = env(k, 0.0, 0.25, 0.45, 1.0)
    if up <= 0.01:
        return ''
    H = 30.0 * up
    out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(x), fm(GR), fm(10 * up + 2), fm(3.2 * up + 0.6), g_rad(fig, (x, GR), 10 * up + 2, [(0, LAVA[1], 0.8 * up), (1, LAVA[3], 0)])))
    j = [(-0.35, 0.7, -97), (0.35, 0.75, -83), (0.0, 1.0, -90)][:]
    for i, (dx, hk, ang) in enumerate(j):
        out.append(tongue(fig, (x + dx * 5, GR + 0.5), H * hk, 5.0 * (0.6 + 0.4 * up) * (0.8 if i < 2 else 1.0),
                          bend=0.5 * math.sin(k * 9 + i + seed), lean=0.06 * (i - 1), direction=ang))
    return ''.join(out)


# ---- la respiration : bulle du cratère, goutte de la griffe, braises

def fx_idle(T, w):
    def f(fig, ctx):
        if w <= 0.02:
            return
        ph = (T / IDLE) % 1
        cr = ctx['crater']
        # la bulle crève : deux gouttes sautent et retombent dans le cratère
        if 0.65 <= ph < 0.95:
            k = (ph - 0.65) / 0.3
            for vx, vy, r in ((-7.0, -16.0, 0.75), (6.0, -19.0, 0.65)):
                t = k * 1.6
                p = ballistic((cr[0] + 2.4, cr[1] - 0.6), (vx, vy), 24.0, t)
                if p[1] < cr[1] + 0.5:
                    fig.fx_front.append(drop(fig, p[0], p[1], vx, vy + 24.0 * t, r, op=w))
        # des braises qui montent du cratère et refroidissent
        for i, born in enumerate((0.1, 0.45, 0.8)):
            k = (ph - born) % 1
            if k < 0.5:
                kk = k / 0.5
                fig.fx_back.append(ember(fig, cr[0] - 6 + 6 * i + 2.5 * math.sin(kk * 6 + i), cr[1] - 2 - 16 * kk, 0.5, op=w * (1 - kk)))
        # la goutte de la griffe tombe, s'écrase au sol en grésillant
        q = (T / (2 * IDLE)) % 1
        tip = ctx['far']['tip']
        if 0.8 <= q < 0.9:
            k = (q - 0.8) / 0.1
            y = tip[1] + 3.5 + (GR - 1.2 - tip[1] - 3.5) * k * k
            if k < 0.92:
                fig.fx_front.append(drop(fig, tip[0], y, 0.0, 10 + 60 * k, 1.15, op=w))
        if 0.86 <= q < 1.0:
            k = (q - 0.86) / 0.14
            op = w * (1 - k)
            fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(tip[0]), fm(GR), fm(2.2 + 2 * k), fm(0.7 + 0.3 * k), g_rad(fig, (tip[0], GR), 3.0 + 2 * k, [(0, LAVA[2], 0.8 * op), (1, LAVA[4], 0)])))
            for sx in (-1, 1):
                p = ballistic((tip[0], GR - 0.5), (sx * 9, -12), 40.0, k * 0.5)
                if p[1] < GR:
                    fig.fx_front.append(ember(fig, p[0], p[1], 0.35, op=op))
            fig.fx_front.append(smoke(fig, tip[0] + 0.5, GR - 2 - 7 * k, 0.6 + 1.3 * k, op=op * 0.6))
    return f


# ---- l'attaque de base

def club_head(ctx):
    """Le centre de la massue (repère du dessin) : pour les traînées et les chocs."""
    return ctx['near']['club']


def fx_attack(tl, prev):
    def f(fig, ctx):
        S = ctx['near']['S']
        C = club_head(ctx)
        # la traînée de la massue qui passe par-dessus la bosse et s'abat
        if 760 < tl < 880 and prev:
            R = math.dist(S, C)
            a1 = math.degrees(math.atan2(C[1] - S[1], C[0] - S[0]))
            p0 = prev[0]
            a0 = math.degrees(math.atan2(p0[1] - S[1], p0[0] - S[0]))
            while a0 > a1:
                a0 -= 360
            a0 = max(a0, a1 - 150)
            fig.fx_back.append(club_smear(fig, S, R, a0, a1, 16.0, op=env(tl, 760, 790, 850, 880)))
        # le choc : poussière qui roule au ras du sol, éclats de roche, gouttes de lave, sol fendu
        if tl >= ATTACK_HIT - 5:
            t = (tl - ATTACK_HIT) / 1000
            base = ctx['near']['base']
            bx = base[0]
            fig.fx_back.append(ground_crack(fig, bx - 6, bx + 14 + 10 * min(1, t * 6), max(0.0, 1 - t * 1.6), seed=2, w=0.9))
            fl = env(tl, ATTACK_HIT - 5, ATTACK_HIT + 10, ATTACK_HIT + 40, ATTACK_HIT + 120)
            if fl > 0:
                fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                    fm(bx + 4), fm(GR - 2), fm(22), fm(9), g_rad(fig, (bx + 4, GR - 2), 22, [(0, LAVA[0], 0.75 * fl), (0.4, LAVA[1], 0.4 * fl), (1, LAVA[2], 0)])))
            for i, (dx, sp, r0) in enumerate(((-14, -1, 3.0), (-6, -1, 2.4), (16, 1, 3.2), (26, 1, 2.6))):
                k = min(1.0, t / 0.7)
                op = env(tl, ATTACK_HIT, ATTACK_HIT + 60, ATTACK_HIT + 300, ATTACK_HIT + 700)
                fig.fx_front.append(dust(fig, bx + 4 + dx + sp * 14 * k, GR - 1.0 - r0 * 0.4 - 2 * k, r0 * (0.6 + 0.8 * k), op=op))
            for i, (vx, vy, s_, hot) in enumerate(((-26, -44, 1.6, False), (30, -52, 1.4, True), (-12, -60, 1.2, False), (44, -36, 1.3, False),
                                                   (8, -64, 1.1, True))):
                p = ballistic((bx + 4, GR - 3), (vx, vy), 160.0, t)
                if p[1] < GR - 0.8 and t < 0.6:
                    fig.fx_front.append(chunk(fig, p[0], p[1], s_, rot=t * 500 * (1 if vx > 0 else -1), hot=hot))
            for i, (vx, vy) in enumerate(((-20, -56), (24, -64), (40, -46), (-34, -40))):
                p = ballistic((bx + 4, GR - 3), (vx, vy), 150.0, t)
                if p[1] < GR - 0.5 and t < 0.6:
                    fig.fx_front.append(drop(fig, p[0], p[1], vx, vy + 150 * t, 0.85))
    return f


# ---- l'attaque spéciale

def fx_special(tl, prev):
    def f(fig, ctx):
        cr = ctx['crater']
        P = ctx['P']
        S = ctx['near']['S']
        # le cratère bout puis crache une fontaine de lave (gouttes en cloche)
        fo = env(tl, 120, 420, 900, 1150)
        if fo > 0:
            h = 6 + 16 * fo + 2 * math.sin(tl / 40)
            for i, (dx, hk, ang) in enumerate(((-3.0, 0.7, -100), (3.0, 0.75, -80), (0.0, 1.0, -90))):
                fig.fx_back.append(tongue(fig, (cr[0] + dx, cr[1] + 1.0), h * hk, 4.6 * (0.6 + 0.4 * fo),
                                          bend=0.4 * math.sin(tl / 70 + i), lean=0.05 * (i - 1), direction=ang))
            for i in range(7):
                k = ((tl - 150) / 520 + i / 7) % 1
                vx = (-14, 10, -6, 16, -18, 4, 12)[i]
                p = ballistic((cr[0] + 0.5 * vx * 0.1, cr[1] - 2), (vx, -36 - 4 * (i % 3)), 64.0, k * 1.15)
                if p[1] < cr[1] + 6:
                    fig.fx_front.append(drop(fig, p[0], p[1], vx, -36 + 64 * k * 1.15, 0.8, op=fo))
        # la massue embrasée : des flammes qui l'enveloppent pendant l'attente
        fl = env(tl, 380, 600, 990, 1300)
        if fl > 0:
            MC = ctx['near']['MC']
            a3 = P['a3']
            for i, (pt, hk) in enumerate((((10.6, 96.0), 0.8), ((21.6, 89.6), 1.0), ((36.2, 94.0), 0.75), ((6.0, 104.0), 0.6), ((40.0, 104.0), 0.55))):
                b = mapp(MC, pt)
                d = -90.0 if tl < 990 else a3 + 180
                fig.fx_front.append(tongue(fig, b, (7 + 3 * math.sin(tl / 50 + i * 1.7)) * hk * fl, 3.6 * fl,
                                           bend=0.5 * math.sin(tl / 60 + i), lean=-0.15, direction=d, op=min(1, fl * 1.3)))
        # le croissant de feu de la massue qui s'abat
        C = club_head(ctx)
        if 950 < tl < 1080 and prev:
            R = math.dist(S, C)
            a1 = math.degrees(math.atan2(C[1] - S[1], C[0] - S[0]))
            p0 = prev[0]
            a0 = math.degrees(math.atan2(p0[1] - S[1], p0[0] - S[0]))
            while a0 > a1:
                a0 -= 360
            a0 = max(a0, a1 - 170)
            fig.fx_back.append(club_smear(fig, S, R, a0, a1, 20.0, hot=True, op=env(tl, 950, 990, 1040, 1080)))
        if tl >= SP_HIT - 5:
            t = (tl - SP_HIT) / 1000
            base = ctx['near']['base']
            bx = base[0] + 4
            # l'éclair du choc
            fl = env(tl, SP_HIT - 5, SP_HIT + 10, SP_HIT + 50, SP_HIT + 160)
            if fl > 0:
                fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                    fm(bx), fm(GR - 4), fm(34), fm(16), g_rad(fig, (bx, GR - 4), 34, [(0, LAVA[0], 0.9 * fl), (0.35, LAVA[1], 0.55 * fl), (1, LAVA[2], 0)])))
            # la faille qui court vers l'ennemi, puis refroidit
            run = min(1.0, t / 0.32)
            x1 = bx + (240 - bx) * (1 - (1 - run) ** 2)
            heat = 1.0 if tl < 1650 else max(0.0, 1 - (tl - 1650) / 600)
            fig.fx_back.append(ground_crack(fig, bx - 8, x1, heat, seed=1, w=1.2))
            # poussière et éclats au pied de la massue
            for i, (dx, sp, r0) in enumerate(((-14, -1, 3.2), (-6, -1, 2.6), (14, 1, 3.0))):
                k = min(1.0, t / 0.7)
                op = env(tl, SP_HIT, SP_HIT + 60, SP_HIT + 300, SP_HIT + 700)
                fig.fx_front.append(dust(fig, bx + dx + sp * 14 * k, GR - 1.0 - r0 * 0.4 - 2 * k, r0 * (0.6 + 0.8 * k), op=op))
            # les trois geysers, l'un après l'autre ; ils retombent en fumée
            for gi, (gx, gt) in enumerate(GEYSERS):
                k = (tl - gt) / 520
                if 0 <= k < 1:
                    fig.fx_front.append(geyser(fig, gx, k, seed=gi))
                    tt = (tl - gt) / 1000
                    for j, (vx, vy, s_) in enumerate(((-16, -60, 1.5), (18, -66, 1.3), (6, -76, 1.1))):
                        p = ballistic((gx, GR - 2), (vx, vy), 150.0, tt)
                        if p[1] < GR - 0.8:
                            fig.fx_front.append(chunk(fig, p[0], p[1], s_, rot=tt * 600 * (1 if vx > 0 else -1), hot=(j == 1)))
                    for j, (vx, vy) in enumerate(((-22, -70), (26, -76), (-8, -88), (14, -84))):
                        p = ballistic((gx, GR - 6), (vx, vy), 150.0, tt)
                        if p[1] < GR - 0.5:
                            fig.fx_front.append(drop(fig, p[0], p[1], vx, vy + 150 * tt, 0.95))
                sk = (tl - gt - 300) / 900
                if 0 <= sk < 1:
                    fig.fx_back.append(smoke(fig, gx + 2 * sk, GR - 4 - 18 * sk, 1.6 + 3.2 * sk, op=0.85 * env(sk, 0, 0.15, 0.5, 1.0)))
                    fig.fx_back.append(smoke(fig, gx - 3 + 1 * sk, GR - 2 - 10 * sk, 1.2 + 2.0 * sk, op=0.7 * env(sk, 0.1, 0.25, 0.55, 1.0)))
    return f


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
    """L'ombre douce au sol sous le monstre (de la massue au pied lointain)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (57 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 58 * k, fy - 3.0 * k, cx + 58 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
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
    if act in ('attack', 'special'):
        prev = []
        for dt in (0.05, 0.025):
            if T - dt >= t0:
                Pp, _ = pose_at(T - dt, act, t0)
                prev.append(club_head(K.build(pose=Pp).ctx))
        fx = [fx_attack(tl, prev)] if act == 'attack' else [fx_special(tl, prev)]
    else:
        fx = [fx_idle(T, 1.0)]
    # le sol tremble au choc : la scène entière bouge de quelques dixièmes de pixel, et s'amortit
    hit = ATTACK_HIT if act == 'attack' else SP_HIT if act == 'special' else None
    v = view
    if hit is not None and 0 <= tl - hit < 260:
        k = (tl - hit) / 260
        amp = (1.4 if act == 'special' else 1.0) * (1 - k) ** 2
        v = (view[0] + amp * math.sin(tl / 11.0), view[1] + amp * 0.8 * math.cos(tl / 9.0), view[2], view[3])
    return K.build(ow=ow, pose=P, fx=fx, frame=v).svg(), P


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
    subprocess.run(['node', os.path.join(K.HEROS, 'rendu-lot.cjs'), jp], check=True)
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
        moments = extra or [1.0, a_s + 0.14, a_s + 0.27, a_s + 0.5, a_s + 0.8, a_s + 0.86, a_s + 1.0, a_s + 1.3,
                            s_s + 0.3, s_s + 0.6, s_s + 0.9, s_s + 1.0, s_s + 1.05, s_s + 1.2, s_s + 1.4, s_s + 1.9]
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
        out = os.environ.get('GOLEM_PLANCHE', os.path.join(TMP, 'planche.png'))
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
