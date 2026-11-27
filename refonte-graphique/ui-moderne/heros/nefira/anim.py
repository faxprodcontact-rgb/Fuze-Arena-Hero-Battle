# Néfira vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/minotaure/build.py)
# — respiration, attaque de base « Scarabée d'or », attaque spéciale « Pyramide des sables » (sort d'équipe) — dans le
# style lisse de l'interface, à 24 images par seconde (même méthode que Kael et Soyane : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/nefira/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/nefira/
#   python3 refonte-graphique/ui-moderne/heros/nefira/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (nefira.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et
# se penche depuis les hanches, la tête suit avec un léger retard, les deux ailes tournent autour de leur racine (elles
# se lèvent) et s'ouvrent (les rémiges s'écartent en éventail, chacune autour de sa propre racine), le bras lointain est
# placé par cinématique inverse depuis le poing qui tient la croix de vie (le coude tourne sur un arc : rien ne se
# décroche), la croix tourne autour du poing ; pendentif, boucle d'oreille et bas de la robe suivent avec retard.
# Les poses clés et les durées reprennent celles du pixel art.
# Effets dans le même style : sable doré et or en volutes, bouffées et grains (dégradés, sans contour), le scarabée d'or
# (un objet : un seul contour, comme le héros), la pyramide de lumière translucide (arêtes d'or, faces à peine
# teintées) ; aucun flou SVG ; jamais de rayons droits répétés. La spéciale est un sort d'équipe : tout naît sur elle et
# s'étend EN CERCLE autour d'elle (rien ne vise l'ennemi).
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
import nefira as N  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm, bez, resample, INK  # noqa: E402

ROOT = N.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'nefira')
TMP = os.path.join(HERE, '_images')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-nefira'
FPS = 24
VIEW = (-26, -26, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = N.GRD
FOE = (200.0, GR - 40)               # le milieu de l'ennemi (le scarabée y éclate)
CEN = (66.0, GR - 1.5)               # le centre du cercle au sol, sous elle (la spéciale)

# tons des effets : sable doré, or, poussière (ceux du pixel art, passés à la gamme de l'interface)
SAND = ['#fff4d6', '#fae8b2', '#e4be76', '#be8e50', '#8a6040']
GOLDFX = ['#fffbe8', '#fff0b0', '#ffd45c', '#e0962e', '#a8601e']
DUST = ['#f6ecd4', '#dcc6a0', '#b49470', '#7a5e5a']
SINK = '#4a2a1c'                     # le contour du scarabée (brun chaud, comme l'or du héros)


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


BASE = dict(lean=0.0, headx=0.0, heady=0.0, tilt=0.0, wl=0.0, ws=0.0, theta=0.0, gx=0.0, gy=0.0, nh=0.0, pend=0.0,
            hem=0.0, smile=0.0, gold=0.0, wph=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'g':
            d['gx'], d['gy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Scarabée d'or » : elle ramène la croix en arrière (le sable d'or s'enroule dans la boucle),
# puis la pointe vers l'ennemi d'un geste sec et royal : un scarabée d'or s'envole de la boucle, file en ondulant avec
# sa traîne de sable, éclate sur l'ennemi en bouffée d'or ; la croix revient droite.
ATTACK = [
    (0, {}),
    (150, dict(theta=-6, g=(-1.0, 0.4), lean=-0.5, wl=1.6, head=(-0.2, 0.2), pend=0.4)),
    (340, dict(theta=-11, g=(-2.0, 0.6), lean=-1.0, wl=3.0, head=(-0.5, 0.3), smile=0.4, pend=0.8)),
    (400, dict(theta=26, g=(3.0, -0.8), lean=1.0, wl=1.6, head=(0.4, 0.0), smile=1.0, pend=-0.6)),
    (470, dict(theta=32, g=(4.0, -1.0), lean=1.3, wl=0.4, head=(0.7, 0.0), smile=1.0, pend=-1.0)),
    (740, dict(theta=30, g=(4.0, -1.0), lean=1.1, wl=0.2, head=(0.6, 0.0), smile=1.0, pend=0.5)),
    (850, dict(theta=16, g=(2.0, -0.5), lean=0.5, wl=1.0, head=(0.3, 0.0), smile=0.8, pend=0.2)),
    (970, dict(theta=6, g=(1.0, -0.2), lean=0.2, wl=0.8, smile=0.5, pend=-0.2)),
    (1120, {}),
]
ATT_GO = 340          # le geste part
ATT_FLY = (370, 600)  # le vol du scarabée
ATT_HIT = 600         # l'éclat

# 3) La spéciale « Pyramide des sables » (sort d'équipe : grand soin et régénération) : elle ouvre grand ses ailes et
# lève la croix ; le sable d'or se soulève tout autour d'elle et monte en spirale (deux rubans, qui passent derrière
# elle puis devant) jusqu'au-dessus de sa tête ; une pyramide de lumière translucide s'y forme, de la pointe vers la
# base, un signe inventé s'allume sur sa face éclairée. LANCEMENT (780 ms, arrêt sur l'image) : la pyramide s'illumine,
# la reine s'éclaire d'un liseré d'or, un anneau d'or naît au sol sous ses pieds et s'élargit tout autour d'elle ; la
# pyramide se dissout en une pluie de grains et de pétales d'or qui retombe en cercle autour d'elle ; les ailes se
# replient.
SPECIAL = [
    (0, {}),
    (140, dict(wl=5, ws=0.3, g=(0, -1.0), hem=0.3)),
    (280, dict(wl=11, ws=0.7, g=(0, -2.0), theta=-4, hem=1.0, head=(0, -0.2))),
    (430, dict(wl=17, ws=1.0, g=(-0.4, -3.0), theta=-1, hem=0.8, head=(-0.4, -0.5), smile=0.5)),
    (610, dict(wl=17, ws=1.0, g=(-0.4, -3.0), theta=0, hem=0.5, head=(-0.4, -0.6), smile=0.8)),
    (780, dict(wl=17.5, ws=1.0, g=(-0.4, -3.2), theta=0, hem=0.4, head=(-0.4, -0.6), smile=1, gold=0.4)),
    (800, dict(wl=17.5, ws=1.0, g=(-0.4, -3.2), theta=0, hem=0.4, head=(-0.4, -0.6), smile=1, gold=1)),
    (990, dict(wl=17.5, ws=1.0, g=(-0.4, -3.2), theta=0, hem=0.4, head=(-0.4, -0.6), smile=1, gold=1)),
    (1090, dict(wl=16, ws=0.9, g=(-0.3, -2.4), hem=0.6, smile=1, gold=0.7)),
    (1190, dict(wl=13.5, ws=0.75, g=(-0.2, -2.0), hem=0.4, smile=0.9, gold=0.4)),
    (1300, dict(wl=11, ws=0.55, g=(0, -1.4), hem=0.2, smile=0.8, gold=0.2)),
    (1410, dict(wl=8, ws=0.4, g=(0, -1.0), smile=0.6)),
    (1530, dict(wl=5, ws=0.25, g=(0, -0.6), smile=0.4)),
    (1660, dict(wl=2.5, ws=0.1)),
    (1800, dict(wl=0.6)),
    (2180, {}),
]
SP_FLASH = 780        # LANCEMENT : le grand soin et la régénération partent vers l'équipe


# ======================================================================== la respiration (2 s)

def pulse(t, t0, up=0.06, hold=0.08, down=0.12):
    x = t - t0
    if x < 0 or x > up + hold + down:
        return 0.0
    if x < up:
        u = x / up
    elif x < up + hold:
        return 1.0
    else:
        u = 1 - (x - up - hold) / down
    return u * u * (3 - 2 * u)


IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : l'or de la croix de vie s'éclaire lentement, la gemme turquoise du croisement avec lui.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(lueur=0.5 - 0.5 * math.cos(u))


def signe_combat(T):
    """Au combat seulement (les ailes sont trop grandes pour la mémoire des menus) : les rémiges ondulent plus fort,
    deux vagues par boucle."""
    u = 2 * math.pi * T / IDLE_T
    return dict(wwv=2.2, wph=2 * u)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # la tête suit le souffle avec un temps de retard ; les ailes se soulèvent un peu à l'inspiration ; la croix se balance
    d = dict(heady=-0.25 * (0.5 - 0.5 * math.cos(u - 0.6)), tilt=0.5 * math.sin(u - 1.0),
             wl=1.4 * (0.5 - 0.5 * math.cos(u - 0.4)), theta=0.9 * math.sin(u - 0.8), gy=0.25 * math.sin(u - 0.9),
             pend=0.55 * math.sin(u - 1.6), nh=0.06 * (0.5 - 0.5 * math.cos(u - 1.2)), hem=0.12 * math.sin(u - 2.0))
    return d, br


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
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
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    # le frémissement de la tenue (la croix vibre d'un rien pendant que le sable s'enroule)
    if action == 'attack' and 160 <= tl <= 340:
        P['theta'] += 0.8 * math.sin(tl / 1000.0 * 2 * math.pi * 18)
    out = dict(breath=w * br, lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'], wl=P['wl'],
               wlF=P['wl'] * 0.8, ws=P['ws'], wph=signe_combat(T)['wph'] + P['wph'], theta=P['theta'],
               grip=(N.GRIP0[0] + P['gx'], N.GRIP0[1] + P['gy']), nh=P['nh'], pend=P['pend'], hem=P['hem'],
               smile=P['smile'], gold=P['gold'], ear=math.sin(2 * 2 * math.pi * T / IDLE_T - 0.5) + 0.5 * P['lean'],
               lueur=w * signe(T)['lueur'], wwv=w * signe_combat(T)['wwv'])
    return out


# ======================================================================== les effets (dégradés, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


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
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(ry), fig.rad(
        c[0], c[1], r, ry, [(0, color, op), (0.45, color, op * 0.4), (1, color, 0)]))


def grain(fig, x, y, s=0.7, op=1.0, rot=0.0, warm=False):
    """Un grain d'or : un petit losange aux flancs courbes, clair en haut à droite."""
    if op <= 0.02:
        return ''
    a = math.radians(rot)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (x + s * (u[0] * i + v[0] * j), y + s * (u[1] * i + v[1] * j))
    sh = sm([P(0, -1.2), P(0.75, 0), P(0, 1.2), P(-0.75, 0)], sharp=(0, 1, 2, 3), t=0.5)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, GOLDFX[0]), (0.5, GOLDFX[2] if not warm else GOLDFX[3]), (1, GOLDFX[3] if not warm else GOLDFX[4])])
    return '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op)


def petal(fig, x, y, s=1.0, rot=0.0, op=1.0):
    """Un pétale d'or (amande courbe), une nervure claire."""
    if op <= 0.02:
        return ''
    a = math.radians(rot)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (x + s * (u[0] * i + v[0] * j), y + s * (u[1] * i + v[1] * j))
    sh = sm([P(-1.6, 0), P(-0.2, -0.95), P(1.6, 0.1), P(-0.1, 0.7)], sharp=(0, 2), t=0.9)
    gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, GOLDFX[1]), (0.55, GOLDFX[2]), (1, GOLDFX[3])])
    return '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.7"/></g>' % (
        op, sh.d(), gr, ribbon([P(-1.1, 0), P(0.2, -0.2), P(1.2, 0.05)], [0.05, 0.3, 0.05]).d(), GOLDFX[0])


def sparkle(fig, c, r, op=1.0, rot=0.0):
    """Un éclat sur l'or : une étoile à quatre branches inégales aux flancs courbes (blanc au cœur)."""
    if r < 0.2 or op <= 0.02:
        return ''
    pts = []
    arms = (1.0, 0.5, 0.8, 0.45)
    for i in range(4):
        a = math.radians(rot + 90 * i - 90)
        pts.append((c[0] + r * arms[i] * math.cos(a), c[1] + r * arms[i] * math.sin(a)))
        b = math.radians(rot + 90 * i - 45)
        pts.append((c[0] + r * 0.2 * math.cos(b), c[1] + r * 0.2 * math.sin(b)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.9)
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.4, GOLDFX[0]), (1, GOLDFX[1])])
    return glow(fig, c, r * 1.2, GOLDFX[1], 0.35 * op) + '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op)


def puff(fig, cx, cy, r, op=1.0, tones=DUST):
    """Une bouffée de sable : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.3 * r, 0.72 * r), (cx - 0.8 * r, cy + 0.32 * r, 0.68 * r), (cx + 0.1 * r, cy - 0.55 * r, 0.6 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.9"/>' % (fm(x), fm(y), fm(rr), tones[3], tones[3]) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def taper_ribbon(pts, wmax, head=0.2, tail=0.45):
    """Un ruban effilé aux deux bouts le long d'une ligne."""
    m = len(pts)
    ws = []
    for j in range(m):
        u = j / max(1, m - 1)
        ws.append(max(0.06, wmax * min(1.0, u / tail if tail > 0 else 1, (1 - u) / head if head > 0 else 1)))
    return ribbon(pts, ws)


def sand_ribbon(fig, pts, w, tones, op=1.0):
    """Un ruban de sable doré : le corps en dégradé, un fil clair dessus (côté lumière)."""
    if len(pts) < 3 or op <= 0.02:
        return ''
    body = taper_ribbon(pts, w)
    hi = taper_ribbon([(x + 0.25, y - 0.35) for x, y in pts], w * 0.4)
    gr = g_lin(fig, pts[0], pts[-1], [(0, tones[3], 0.25), (0.5, tones[2], 0.95), (1, tones[1], 1)])
    return '<g opacity="%g"><path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.8"/></g>' % (op, body.d(), gr, hi.d(), tones[0])


def curl_pts(c, r0, a0, turn, n=26, shrink=0.55):
    """Une volute : une spirale qui s'enroule vers son centre (angles en degrés)."""
    out = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        r = r0 * (1 - shrink * t)
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


def scarab(fig, c, ang, flap, k=1.0):
    """Le scarabée d'or : corps en goutte, tête, deux élytres turquoise bordées d'or qui battent ; un seul contour."""
    a = math.radians(ang)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (c[0] + k * (u[0] * i + v[0] * j), c[1] + k * (u[1] * i + v[1] * j))
    body = sm([P(-3.4, 0), P(-1.6, -2.1), P(1.6, -2.0), P(3.0, 0), P(1.6, 2.0), P(-1.6, 2.1)], t=0.95)
    head = sm([P(2.6, -1.2), P(4.4, -1.0), P(5.0, 0), P(4.4, 1.0), P(2.6, 1.2)], t=0.95)
    horn = sm([P(4.6, -0.5), P(6.2, -1.4), P(5.6, 0.1)], sharp=(1,), t=0.7)
    fl = flap
    wing1 = sm([P(1.6, -1.0), P(-0.4, -2.6 - 2.6 * fl), P(-3.8, -3.2 - 3.2 * fl), P(-2.6, -1.0)], t=0.9)
    wing2 = sm([P(1.6, 1.0), P(-0.4, 2.6 + 1.6 * fl), P(-3.6, 3.0 + 2.0 * fl), P(-2.6, 1.0)], t=0.9)
    gb = g_lin(fig, P(3, -2), P(-3, 2), [(0, GOLDFX[1]), (0.5, GOLDFX[2]), (1, GOLDFX[4])])
    gw = g_lin(fig, P(1, -3), P(-3, 3), [(0, '#b6f6e2'), (0.5, '#52d8c0'), (1, '#10707a')])
    shapes = [(wing2, gw, 0.95), (horn, gb, 1), (body, gb, 1), (head, gb, 1), (wing1, gw, 0.95)]
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="1.5" stroke-linejoin="round"/>' % (sh.d(), SINK, SINK) for sh, _, _ in shapes)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl_, '' if o == 1 else ' opacity="%g"' % o) for sh, fl_, o in shapes)
    det = ('<path d="%s" fill="%s" opacity="0.85"/>' % (ribbon([P(-2.2, -0.8), P(0.2, -1.4), P(2.2, -1.0)], [0.1, 0.55, 0.1]).d(), GOLDFX[0]) +
           '<path d="%s" fill="%s" opacity="0.6"/>' % (ribbon([P(-2.8, 0.2), P(0, 0.15), P(2.6, 0.1)], [0.1, 0.35, 0.1]).d(), GOLDFX[4]) +
           '<circle cx="%s" cy="%s" r="%s" fill="#b4303a"/>' % (fm(P(4.0, -0.3)[0]), fm(P(4.0, -0.3)[1]), fm(0.45 * k)))
    return '<g>%s%s%s</g>' % (sil, col, det)


def burst(fig, c, r, rot=0.0, op=1.0):
    """L'éclat de l'impact : une étoile à quatre branches inégales, aux flancs courbes (blanc au cœur, or au bord)."""
    if r < 0.4 or op <= 0.02:
        return ''
    pts = []
    arms = (1.0, 0.6, 0.85, 0.5)
    for i in range(4):
        a = math.radians(rot + 90 * i)
        pts.append((c[0] + r * arms[i] * math.cos(a), c[1] + r * arms[i] * math.sin(a)))
        b = math.radians(rot + 90 * i + 45)
        pts.append((c[0] + r * 0.26 * math.cos(b), c[1] + r * 0.26 * math.sin(b)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.9)
    core = sh.scale(0.55, 0.55, c[0], c[1])
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.35, GOLDFX[0]), (0.7, GOLDFX[2]), (1, GOLDFX[3])])
    sil = '<path d="%s" fill="%s" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % (sh.d(), SINK, SINK)
    return '<g opacity="%g">%s<path d="%s" fill="%s"/><path d="%s" fill="#fffdf0" opacity="0.9"/></g>' % (op, sil, sh.d(), gr, core.d())


# ---- l'attaque de base

def scarab_path(s, start):
    """Le chemin du scarabée, de la boucle tendue vers l'ennemi : une ligne qui ondule doucement."""
    p0 = (start[0] + 3, start[1])
    p1 = (FOE[0] - 4, FOE[1])
    x = p0[0] + (p1[0] - p0[0]) * s
    y = p0[1] + (p1[1] - p0[1]) * s - 10 * math.sin(math.pi * s) + 3.5 * math.sin(3 * math.pi * s)
    return (x, y)


_START = []


def strike_loop():
    """Où est la boucle de la croix quand le scarabée s'envole (la pose clé du geste, sans la respiration)."""
    if not _START:
        k = keyed(ATTACK, ATT_FLY[0])
        pose = dict(lean=k['lean'], head=(k['headx'], k['heady']), wl=k['wl'], theta=k['theta'],
                    grip=(N.GRIP0[0] + k['gx'], N.GRIP0[1] + k['gy']))
        _START.append(N.build(pose=pose).ctx['loop'])
    return _START[0]


def fx_attack(tl):
    def f(fig, ctx):
        loop = ctx['loop']
        t = tl
        # 1) le sable d'or s'enroule dans la boucle (deux volutes, par la droite et par le haut), des grains y tombent
        ga = env(t, 20, 160, 330, 400)
        if ga > 0:
            lv = smooth((t - 20) / 320)
            r1 = 10 - 4 * lv
            c1 = curl_pts(loop, r1, -70 + 260 * lv, 220, shrink=0.7)
            c2 = curl_pts(loop, r1 - 1.5, 60 + 260 * lv, 200, shrink=0.75)
            fig.fx_front.append(sand_ribbon(fig, c1, 1.7, SAND, op=ga))
            fig.fx_front.append(sand_ribbon(fig, c2, 1.3, GOLDFX, op=ga))
            for i in range(7):
                a = math.radians(-100 + 41 * i + 80 * lv)
                r = (13 - 6 * lv) + 2.2 * ((i * 0.37) % 1)
                fig.fx_front.append(grain(fig, loop[0] + r * math.cos(a), loop[1] + r * math.sin(a), 0.55 + 0.2 * (i % 2), ga, rot=a * 40))
        # la boucle s'embrase (lueur dorée ronde)
        lg = env(t, 40, 300, 420, 620)
        if lg > 0:
            fig.fx_front.append(glow(fig, loop, 5 + 4 * lg, GOLDFX[2], 0.55 * lg))
        # 2) le geste : un croissant de sable suit la boucle, de l'arrière vers l'avant
        sw = env(t, ATT_GO, ATT_GO + 30, ATT_GO + 70, ATT_GO + 170)
        if sw > 0:
            G = ctx['G']
            R = math.dist(G, loop)
            a1 = math.degrees(math.atan2(loop[1] - G[1], loop[0] - G[0]))
            a0 = a1 - 42 * min(1, (t - ATT_GO) / 60 + 0.3)
            pts = [(G[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / 20)), G[1] + R * math.sin(math.radians(a0 + (a1 - a0) * i / 20))) for i in range(21)]
            fig.fx_back.append(sand_ribbon(fig, pts, 3.2, SAND, op=sw * 0.9))
        # 3) le scarabée s'envole, file en ondulant avec sa traîne de sable tressée
        if ATT_FLY[0] <= t < ATT_HIT + 20:
            s = smooth((t - ATT_FLY[0]) / (ATT_FLY[1] - ATT_FLY[0])) * 0.15 + 0.85 * min(1, (t - ATT_FLY[0]) / (ATT_FLY[1] - ATT_FLY[0]))
            s = min(1.0, s)
            st = strike_loop()
            p = scarab_path(s, st)
            q = scarab_path(max(0, s - 0.02), st)
            ang = math.degrees(math.atan2(p[1] - q[1], p[0] - q[0]))
            s0 = max(0.0, s - 0.5)
            ss = [s0 + (s - s0) * i / 40 for i in range(41)][:-3]
            if len(ss) > 4 and s - s0 > 0.04:
                for si, (tones, wmax, ph) in enumerate(((SAND, 2.6, 0.0), (GOLDFX, 1.6, math.pi))):
                    pts = []
                    for j, v in enumerate(ss):
                        x, y = scarab_path(v, st)
                        x2, y2 = scarab_path(min(1, v + 0.01), st)
                        tx, ty = x2 - x, y2 - y
                        L = math.hypot(tx, ty) or 1
                        a = 1.8 * math.sin(t / 40.0 + j * 0.35 + ph)
                        pts.append((x - ty / L * a, y + tx / L * a))
                    fig.fx_front.append(sand_ribbon(fig, pts, wmax, tones, op=1.0))
                for i in range(8):
                    v = s0 + (s - s0) * ((i * 0.618) % 1)
                    x, y = scarab_path(v, st)
                    fig.fx_front.append(grain(fig, x + 2.5 * math.sin(i * 2.3), y + 2.5 * math.cos(i * 1.7) + 1.5, 0.5 + 0.15 * (i % 3), 0.9, rot=i * 33))
            flap = math.sin(t / 1000.0 * 2 * math.pi * 14)
            fig.fx_front.append(scarab(fig, p, ang, flap, 1.0))
        # 4) l'éclat sur l'ennemi : un éclair d'or, une bouffée de sable doré, des grains qui jaillissent puis retombent
        if t >= ATT_HIT:
            tau = (t - ATT_HIT) / 1000.0
            fl = env(t, ATT_HIT - 5, ATT_HIT + 20, ATT_HIT + 70, ATT_HIT + 200)
            if fl > 0:
                fig.fx_front.append(glow(fig, FOE, 16, GOLDFX[1], 0.6 * fl))
                fig.fx_front.append(burst(fig, FOE, 9 * (0.6 + 0.4 * fl), rot=12, op=fl))
            cl = env(t, ATT_HIT, ATT_HIT + 60, ATT_HIT + 200, ATT_HIT + 480)
            if cl > 0:
                g = smooth((t - ATT_HIT) / 380)
                for i, (dx, dy, r) in enumerate(((5, 2, 6.5), (-5, 3, 5.0), (1, -5, 4.6), (9, -3, 3.8))):
                    fig.fx_back.append(puff(fig, FOE[0] + dx * (1 + 0.8 * g), FOE[1] + dy * (1 + 0.6 * g) - 3 * g, r * (0.7 + 0.6 * g), cl * 0.85, SAND[1:] + [DUST[3]]))
            for i in range(10):
                a = math.radians(-70 + i * 31 + 7 * (i % 3))
                sp = 50 + 22 * ((i * 0.41) % 1)
                x = FOE[0] + sp * math.cos(a) * tau
                y = FOE[1] + sp * math.sin(a) * tau + 0.5 * 180 * tau * tau
                if y < GR - 0.6 and tau < 0.7:
                    fig.fx_front.append(grain(fig, x, y, 0.6 + 0.2 * (i % 2), op=min(1, (0.7 - tau) * 3), rot=i * 50 + tau * 400))
            if t > ATT_HIT + 260:
                k = env(t, ATT_HIT + 260, ATT_HIT + 330, ATT_HIT + 420, ATT_HIT + 520)
                fig.fx_back.append(puff(fig, FOE[0] + 12, GR - 2.4, 2.6, 0.8 * k))
                fig.fx_back.append(puff(fig, FOE[0] - 9, GR - 2.0, 2.1, 0.7 * k))
    return f


# ---- la spéciale

STIR = [20, 75, 130, 170, 215, 255, 295, 335]          # les angles des bouffées autour d'elle (degrés)


def ring_pt(a, rx, ry=None, c=CEN):
    ry = rx * 0.15 if ry is None else ry
    return (c[0] + rx * math.cos(math.radians(a)), c[1] + ry * math.sin(math.radians(a)))


def spiral_pt(s, phase, twist):
    """Le ruban qui monte en spirale autour d'elle, de ses pieds (s = 0) jusqu'au-dessus de sa tête (s = 1)."""
    a = phase + 380 * s + twist
    r = 46 * (1 - 0.78 * s ** 0.9)
    y = GR - 2 - (GR + 4) * s ** 1.05
    x = CEN[0] + 6 * s + r * math.cos(math.radians(a))
    y += r * 0.22 * math.sin(math.radians(a))
    return (x, y), math.sin(math.radians(a)) > 0


PYR = dict(cx=78.0, base=4.0, hw=17.0, apex=-20.0)


def pyramid(fig, form=1.0, k=1.0, flash=0.0, ghost=0.0, sign=0.0):
    """La pyramide de lumière translucide, vue de trois quarts : deux faces (l'éclairée à droite), arêtes d'or lumineuses,
    elle se forme de la pointe vers la base (form 0..1) ; ghost : elle se dissout ; un signe inventé sur la face claire."""
    cx, by, hw, ay = PYR['cx'], PYR['base'], PYR['hw'] * k, PYR['apex']
    by = ay + (by - ay) * k
    A = (cx + hw * 0.2, ay)
    L = (cx - hw, by)
    M = (cx + hw * 0.35, by + 2.6 * k)
    R = (cx + hw, by - 0.6)
    lv = form
    Lf = (A[0] + (L[0] - A[0]) * lv, A[1] + (L[1] - A[1]) * lv)
    Mf = (A[0] + (M[0] - A[0]) * lv, A[1] + (M[1] - A[1]) * lv)
    Rf = (A[0] + (R[0] - A[0]) * lv, A[1] + (R[1] - A[1]) * lv)
    op = (1 - ghost)
    out = []
    out.append(glow(fig, (cx, (ay + by) / 2 + 2), hw * 1.6, GOLDFX[2], (0.18 + 0.35 * flash) * op * lv, ry=hw * 1.4))
    fl = sm([A, Lf, Mf], sharp=(0, 1, 2), t=0.3)
    fr = sm([A, Mf, Rf], sharp=(0, 1, 2), t=0.3)
    out.append('<path d="%s" fill="%s" opacity="%g"/>' % (fl.d(), g_lin(fig, A, Lf, [(0, GOLDFX[1], 0.35 + 0.4 * flash), (1, GOLDFX[3], 0.12 + 0.3 * flash)]), op))
    out.append('<path d="%s" fill="%s" opacity="%g"/>' % (fr.d(), g_lin(fig, A, Mf, [(0, '#ffffff', 0.45 + 0.45 * flash), (1, GOLDFX[1], 0.18 + 0.4 * flash)]), op))
    # les arêtes d'or (des rubans fins, plus épais près de la pointe), la base
    for p, q, w in ((A, Lf, 0.9), (A, Mf, 1.15), (A, Rf, 0.8), (Lf, Mf, 0.7), (Mf, Rf, 0.7)):
        pts = [(p[0] + (q[0] - p[0]) * i / 8, p[1] + (q[1] - p[1]) * i / 8) for i in range(9)]
        out.append('<path d="%s" fill="%s" opacity="%g"/>' % (ribbon(pts, [0.2] + [w * (1 + 0.5 * flash)] * 7 + [0.2]).d(), GOLDFX[2] if flash < 0.5 else GOLDFX[0], op))
        out.append('<path d="%s" fill="%s" opacity="%g"/>' % (ribbon(pts, [0.1] + [w * 0.45] * 7 + [0.1]).d(), GOLDFX[0], op))
    # le signe inventé (pas une lettre) sur la face éclairée : un arc ouvert, un point, une goutte
    if sign > 0 and lv > 0.95:
        c = ((A[0] + Mf[0] + Rf[0]) / 3, (A[1] + Mf[1] + Rf[1]) / 3 + 1.0)
        s = 1.0 * k
        arc = [(c[0] - 2.4 * s + 4.8 * s * i / 10, c[1] - 0.2 * s - 1.8 * s * math.sin(math.pi * i / 10)) for i in range(11)]
        col = GOLDFX[0] if flash > 0.5 else GOLDFX[2]
        out.append('<g opacity="%g"><path d="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
            sign * op, ribbon(arc, [0.1] + [0.55 * s] * 9 + [0.1]).d(), col, fm(c[0]), fm(c[1] - 0.6 * s), fm(0.6 * s), col,
            sm([(c[0], c[1] + 0.8 * s), (c[0] + 0.8 * s, c[1] + 2.2 * s), (c[0], c[1] + 3.2 * s), (c[0] - 0.8 * s, c[1] + 2.2 * s)], sharp=(0,), t=0.9).d(), col))
    return ''.join(out)


def ring(fig, rx, w, op):
    """L'anneau d'or au sol : un ovale aplati (posé au sol) ; rend (moitié de derrière, moitié de devant)."""
    if op <= 0.02 or rx < 1:
        return '', ''
    out = []
    for a0, a1 in ((180, 360), (0, 180)):
        pts = [ring_pt(a0 + (a1 - a0) * i / 30, rx) for i in range(31)]
        soft = ribbon(pts, [0.2] + [w * 2.6] * 29 + [0.2])
        core = ribbon(pts, [0.1] + [w] * 29 + [0.1])
        hot = ribbon(pts, [0.05] + [w * 0.4] * 29 + [0.05])
        out.append('<g opacity="%g"><path d="%s" fill="%s" opacity="0.3"/><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
            op, soft.d(), GOLDFX[2], core.d(), GOLDFX[2], hot.d(), GOLDFX[0]))
    return out[0], out[1]


RAIN = []
for i in range(26):
    a = (i * 137.5) % 360
    d = 22 + 40 * ((i * 0.618) % 1)
    RAIN.append((a, d, 0.0 + 0.012 * (i % 9), i % 4 == 0))


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        top = ctx['top']
        # 1) le sable se soulève à ses pieds, tout autour d'elle (bouffées : derrière elle, puis devant)
        st = env(t, 0, 140, 420, 700)
        if st > 0:
            for i, a in enumerate(STIR):
                r = 30 + 8 * ((i * 0.37) % 1) + 6 * smooth(t / 500)
                p = ring_pt(a, r, r * 0.2)
                rr = 2.6 + 1.2 * ((i * 0.53) % 1) + 1.4 * smooth(t / 400)
                lift = 3 * smooth(t / 600)
                el = puff(fig, p[0], p[1] - lift - rr * 0.5, rr, st * 0.85)
                (fig.fx_front if math.sin(math.radians(a)) > 0 else fig.fx_back).append(el)
        # 2) deux rubans (sable clair, or) montent en spirale autour d'elle, en se resserrant au-dessus de sa tête
        if 120 <= t <= 700:
            head_s = smooth((t - 120) / 380)
            tail_s = max(0.0, smooth((t - 260) / 420))
            if head_s - tail_s > 0.02:
                for (ph, tones, w) in ((160, SAND, 3.0), (340, GOLDFX, 2.2)):
                    seg = []
                    cur = None
                    n = 46
                    for j in range(n + 1):
                        s = tail_s + (head_s - tail_s) * j / n
                        p, front = spiral_pt(s, ph, t * 0.12)
                        if cur is None or front != cur:
                            if seg:
                                seg[-1][1].append(p)
                            seg.append((front, [p]))
                            cur = front
                        else:
                            seg[-1][1].append(p)
                    for front, pts in seg:
                        if len(pts) >= 3:
                            el = sand_ribbon(fig, pts, w, tones, op=env(t, 120, 200, 560, 700))
                            (fig.fx_front if front else fig.fx_back).append(el)
                    # des grains le long des rubans
                    for j in range(6):
                        s = tail_s + (head_s - tail_s) * ((j * 0.618 + 0.1) % 1)
                        p, front = spiral_pt(s, ph + 18, t * 0.12)
                        (fig.fx_front if front else fig.fx_back).append(grain(fig, p[0], p[1] - 1.5, 0.55, 0.9, rot=j * 40 + t * 0.3))
        # la croix brille pendant la montée
        lg = env(t, 200, 430, 990, 1300)
        if lg > 0:
            fig.fx_front.append(glow(fig, ctx['loop'], 6 + 3 * lg, GOLDFX[2], 0.5 * lg))
        # 3) la pyramide de lumière se forme au-dessus de sa tête (de la pointe vers la base), puis s'illumine
        if 430 <= t < 1300:
            form = smooth((t - 430) / 180)
            flash = env(t, SP_FLASH - 10, SP_FLASH, 990, 1090)
            ghost = smooth((t - 990) / 290) if t > 990 else 0.0
            k = 1.0 - 0.6 * ghost
            sign = smooth((t - 610) / 120)
            fig.fx_back.append(pyramid(fig, form=0.3 + 0.7 * form, k=k, flash=flash, ghost=ghost, sign=sign))
        # quelques éclats tournent autour de la pyramide (temps de pose)
        ob = env(t, 600, 660, 760, 820)
        if ob > 0:
            for i in range(3):
                a = math.radians(t * 0.5 + 120 * i)
                c = (PYR['cx'] + 22 * math.cos(a), (PYR['apex'] + PYR['base']) / 2 + 6 * math.sin(a))
                fig.fx_front.append(sparkle(fig, c, 2.2, ob, rot=t * 0.2))
        # 4) LANCEMENT : un liseré d'or tout autour d'elle (le sort part vers l'équipe), un anneau d'or naît au sol
        au = env(t, SP_FLASH - 10, SP_FLASH + 10, 990, 1300)
        if au > 0:
            fig.aura = (GOLDFX[2], 1.3 * au, 0.9 * au)
            fig.under.append((ctx['chest'][0], ctx['chest'][1] - 10, 50, 46, GOLDFX[2], 0.28 * au, None))
        if t >= SP_FLASH:
            g = smooth((t - SP_FLASH) / 520)
            rx = 18 + 52 * g
            op = env(t, SP_FLASH - 5, SP_FLASH + 30, 1150, 1450)
            back, front = ring(fig, rx, 1.6 * (1 - 0.5 * g), op)
            fig.fx_back.append(back)
            fig.fx_front.append(front)
        # 5) la pluie de grains et de pétales d'or qui s'ouvre en ombrelle et retombe en cercle autour d'elle
        if t >= 990:
            tau = (t - 990) / 1000.0
            for i, (a, d, dl, is_petal) in enumerate(RAIN):
                tt = tau - dl
                if tt <= 0:
                    continue
                k = min(1.0, tt / 0.55)
                e = smooth(k)
                land = ring_pt(a, d, d * 0.2)
                start = (PYR['cx'] + 6 * math.cos(math.radians(a)), (PYR['apex'] + PYR['base']) / 2)
                # l'ombrelle : d'abord vers le dehors et un peu vers le haut, puis la chute
                x = start[0] + (land[0] - start[0]) * e
                y = start[1] + (land[1] - start[1]) * (k ** 1.6) - 10 * math.sin(math.pi * min(1, k * 1.1)) * (1 - k)
                front = math.sin(math.radians(a)) > 0
                lay = fig.fx_front if front else fig.fx_back
                if k < 1:
                    if is_petal:
                        lay.append(petal(fig, x, y, 1.1, rot=a + tt * 500, op=1.0))
                    else:
                        lay.append(grain(fig, x, y, 0.65 + 0.2 * (i % 2), 1.0, rot=i * 30 + tt * 600))
                else:
                    gl = env(tt, 0.55, 0.6, 0.7, 1.0)
                    if gl > 0:
                        lay.append(glow(fig, (land[0], land[1] - 0.4), 3.2, GOLDFX[1], 0.8 * gl, ry=1.2))
                        lay.append(grain(fig, land[0], land[1] - 0.6, 0.55, gl, rot=i * 30))
    return f


# ---- les éclats sur les ors pendant la pose (un à la fois, comme le pixel art)

def fx_glints(T):
    def f(fig, ctx):
        t = T % 2.0
        P = ctx['P']
        spots = [
            (0.05, lambda: N.mapp(ctx['AM'], (104.0, 17.0))),          # la croix
            (0.55, lambda: N.mapp(ctx['UC'], (85.0, 58.4))),           # le collier
            (0.95, lambda: N.mapp(ctx['HEAD'], (N.BAND_X + 1.2, 14.6))),  # le cobra
            (1.45, lambda: N.mapp(ctx['HEAD'], (65.2, 52.8))),         # la boucle d'oreille
            (1.7, lambda: N.mapp(ctx['U'], (79.6, 70.0))),             # la ceinture
        ]
        for t0, pos in spots:
            k = env(t, t0, t0 + 0.1, t0 + 0.14, t0 + 0.3)
            if k > 0:
                fig.over.append(sparkle(fig, pos(), 1.9 * k, k, rot=8))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous elle."""
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
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 34 * k, fy - 3.0 * k, cx + 34 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
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
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    else:
        fx = [fx_glints(T)]
    return N.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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


SPRITE_FEET = (62, 104)          # les pieds dans l'image pixel de la pose (src/game/hd-figures.ts)


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées
    et la place du dessin de la pose dans ces images."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-minotaure-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)   # le fond clair (242, ou 240 dans la spéciale)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'myths-6.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan de terre, le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'meduse.webp')).convert('RGBA')
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
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25) for i in range(n)], PW, PH, 'b')
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
        moments = [1.0, 1.5, a_s + 0.3, a_s + 0.38, a_s + 0.48, a_s + 0.62, a_s + 0.8,
                   s_s + 0.25, s_s + 0.45, s_s + 0.62, s_s + 0.8, s_s + 0.95, s_s + 1.1, s_s + 1.3, s_s + 1.55, s_s + 1.9]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255, 255))
            sheet.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(DBG, exist_ok=True)
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)
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
