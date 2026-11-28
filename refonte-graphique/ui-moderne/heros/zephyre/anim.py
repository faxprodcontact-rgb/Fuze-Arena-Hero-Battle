# Zéphyre vectorielle ANIMÉE (refonte des héros du 26/11/2026, même méthode que Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/zephyre/build.py) — respiration, attaque de base
# « Shuriken du vent », attaque spéciale « Danse des feuilles » — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/zephyre/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/zephyre/
#   python3 refonte-graphique/ui-moderne/heros/zephyre/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (zephyre.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui respire et se
# penche depuis les hanches, tête d'un seul bloc, pans du bandeau et de la ceinture qui traînent avec retard ; le bras
# lointain est placé par cinématique inverse depuis le poignet : il arme derrière la tête, fouette, se tend main ouverte,
# cueille le shuriken qui revient). Les poses clés reprennent celles du pixel art (mêmes gestes, mêmes temps : longue
# armée tenue, fouetté très court, impact tenu, retour en boomerang ; pour la spéciale : elle se ramasse, le tourbillon
# l'avale, trois doubles turquoise frappent ensemble autour de l'ennemi, puis elle ressort du tourbillon) et sont reliées
# par des courbes douces sans dépassement (24 images par seconde). Les effets de vent (rubans, croissants, volutes,
# feuilles, éclat) sont dessinés dans le même style : dégradés, un contour, courbes ; aucun flou SVG ; jamais de rayons
# droits répétés.
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
import zephyre as Z  # noqa: E402
from atelier import Figure, sm, ribbon, ellipse, f as fm, ID  # noqa: E402
from outils import crpath  # noqa: E402

ROOT = Z.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'zephyre')
TMP = os.path.join(Z.TMP, 'anim')
FPS = 24
VIEW = (-24, -42, 292, 164.25)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = Z.GRD
INKW = '#0d3a46'                     # le contour du vent (bleu pétrole presque noir)
WIND = ['#ffffff', '#e4fbff', '#b2eef0', '#7ad8c0', '#36b294', '#1a6e68']
LEAF = ['#c8f6c4', '#7ed69a', '#3ea878', '#1e6e58']
GHOST = ('#effffa', '#a6ecda', '#5ccab4', '#2f8e80')   # les doubles : clair, ton, ombre, contour
GHOST_INK = '#1a6e68'
EX, EY = 202.0, 64.0                 # le centre de l'ennemi (poitrine), à droite


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


NUM = ['crouch', 'lean', 'tilt', 't', 'e', 'headx', 'heady', 'fwx', 'fwy', 'spin', 'nwx', 'nwy', 'squint', 'shx', 'shy']
STEP = ['hand', 'star']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, t=0, e=0, headx=0, heady=0, fwx=Z.FW0[0], fwy=Z.FW0[1], spin=0, nwx=0, nwy=0,
             squint=0, shx=0, shy=0, hand=0, star=1)
    for key, v in k.items():
        if key in ('head', 'fw', 'nw', 'sh'):
            d[{'head': 'headx', 'fw': 'fwx', 'nw': 'nwx', 'sh': 'shx'}[key]] = v[0]
            d[{'head': 'heady', 'fw': 'fwy', 'nw': 'nwy', 'sh': 'shy'}[key]] = v[1]
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    out = {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}
    last = max(i for i in range(len(ts)) if ts[i] <= t) if t >= ts[0] else 0
    for n in STEP:
        out[n] = fl[last][n]
    return out


# ======================================================================== les actions (poses clés, comme le pixel art)
# 2) L'attaque de base « Shuriken du vent » : elle arme le bras derrière la tête (le shuriken dépasse au-dessus du
# bandeau), le buste recule, tient ; puis fouette le bras en avant : le shuriken part en tournoyant, frappe l'ennemi
# (éclat, étincelles d'acier, arrêt), revient par une courbe basse comme un boomerang et claque dans sa main levée.
ATTACK = [
    (0, {}),
    (90, dict(crouch=2, lean=-2, fw=(86, 33), head=(0, 1), t=1, e=1, squint=0.5)),
    (250, dict(crouch=3, lean=-4, fw=(79, 30), head=(-1, 1), tilt=-2, t=2, e=1, squint=1)),
    (300, dict(crouch=3.2, lean=-4.4, fw=(78.4, 29.6), head=(-1, 1.1), tilt=-2.4, t=2.2, e=1.2, squint=1)),
    (345, dict(crouch=1, lean=3, fw=(108, 35), t=-1, e=-1, star=0, squint=1)),
    (390, dict(crouch=1, lean=5, fw=(116, 52), hand=1, star=0, t=-2, e=-2, head=(1, 0), tilt=2, squint=1)),
    (530, dict(crouch=1.2, lean=5.2, fw=(116.4, 52.4), hand=1, star=0, t=-1.5, e=-1.5, head=(1, 0), tilt=2, squint=1)),
    (610, dict(crouch=0.5, lean=2, fw=(110, 42), hand=1, star=0, t=0, e=1, squint=0.6)),
    (730, dict(crouch=0, lean=0, fw=(97, 33), hand=1, star=0, t=1, e=1)),
    (770, dict(crouch=1.2, lean=0, fw=Z.FW0, head=(0, 1), t=1, e=0, hand=0, star=1)),
    (900, dict(crouch=0.4, t=0, e=-1)),
    (1060, {}),
]
T_THROW, T_HIT, T_BACK, T_CATCH = 345, 500, 580, 770

# 3) L'attaque spéciale « Danse des feuilles » : elle se ramasse (le vent se lève, des feuilles montent), tient ; un
# tourbillon de feuilles l'avale (elle pâlit puis disparaît) ; une rafale de feuilles file jusqu'à l'ennemi ; trois
# doubles turquoise surgissent autour de lui (devant, derrière, au-dessus) et frappent ensemble au kunaï (trois
# croissants, éclair, arrêt sur l'image) ; ils s'effritent en feuilles, les feuilles reviennent en tourbillon à sa place
# et Zéphyre en ressort, posée, puis se redresse en garde.
SPECIAL = [
    (0, {}),
    (100, dict(crouch=2, lean=-1, head=(0, 1), t=1, e=1, squint=0.5)),
    (300, dict(crouch=4, lean=-2, head=(0, 1), t=1.6, e=1.6, squint=1)),
    (1180, dict(crouch=4, lean=-1, head=(0, 1), t=-1.4, e=-1.4, squint=1)),
    (1330, dict(crouch=4, lean=-1, head=(0, 1), t=-0.6, e=-0.6, squint=0.5)),
    (1460, dict(crouch=3, head=(0, 1), t=0.4, e=1)),
    (1600, dict(crouch=1, t=-0.6, e=0)),
    (1780, {}),
]
CLONE = dict(crouch=4.5, lean=8, fw=(99, 66), star=0.0, nw=(9, -5), t=-2, e=-2, head=(1, 1), tilt=4, squint=1)
SP_HIT = 600


def vis_special(tl):
    """Zéphyre elle-même pendant la spéciale : 1 = elle, entre les deux = silhouette pâle, 0 = disparue."""
    if tl < 330:
        return 1.0
    if tl < 440:
        return 1.0 - (tl - 330) / 110
    if tl < 1180:
        return 0.0
    if tl < 1300:
        return (tl - 1180) / 120
    return 1.0


# ======================================================================== la respiration (en boucle)

BREATH = 1.5     # la respiration vive : deux par boucle du repos (1,6 s avant le 27/11)
IDLE_T = 3.0     # la boucle du repos (s) : respiration et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : les deux pans du bandeau turquoise flottent lentement dans le vent (ils montent derrière elle, puis
    retombent) et le grand shuriken bascule doucement entre ses doigts. Une pose partielle pour build() ; jouée au
    combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(t=2.0 * math.sin(u), spin=7.0 * math.sin(u - 0.8))


def idle_offsets(T):
    u = 2 * math.pi * T / BREATH
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.5 * (0.5 - 0.5 * math.cos(u - 2.4)), heady=0.3 * math.sin(u - 1.9),
                tilt=0.5 * math.sin(u - 1.2), t=0.9 * math.sin(u - 1.9), e=0.8 * math.sin(u - 2.5),
                spin=2.0 * math.sin(u - 1.0), fwy=-0.45 * math.sin(u - 0.9))


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
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    for n in STEP:
        P[n] = src[n]
    P['breath'] = w * idl['breath']
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['fw'] = (P.pop('fwx'), P.pop('fwy'))
    P['nw'] = (P.pop('nwx'), P.pop('nwy'))
    P['shift'] = (P.pop('shx'), P.pop('shy'))
    sg = signe(T)                                  # le signe du repos : les pans du bandeau, le shuriken (anim.signe)
    P['t'] += w * sg['t']
    P['spin'] += w * sg['spin']
    P['blink'] = 1.0 if (w > 0.95 and 1.9 <= (T % IDLE_T) < 2.0) else 0.0
    return P


# ======================================================================== les effets de vent (dessinés, un seul contour)

def outlined(items, ink=INKW, w=1.0, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs).
    items : (forme, remplissage, opacité[, 'n' = sans contour])."""
    if op <= 0.02:
        return ''
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in items if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in items)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


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


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bez(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def arc_band(C, rx, ry, a0, a1, w, n=28, rot=0.0):
    """Un croissant le long d'un arc d'ellipse (de a0, fin, à a1 ; plein au milieu) autour de C ; degrés."""
    outer, inner = [], []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * math.sin(math.pi * t) ** 0.8
        for lst, k in ((outer, 0.0), (inner, ww)):
            x, y = (rx - k) * math.cos(a), (ry - k * ry / rx) * math.sin(a)
            lst.append((C[0] + x * cr - y * sr, C[1] + x * sr + y * cr))
    return sm(outer + inner[::-1][1:-1], sharp=(0, n), t=0.6)


def crescent(fig, C, rx, ry, a0, a1, w, op=1.0, rot=0.0, ink=True):
    """Un croissant de vent : blanc au cœur, cyan, jade sur le bord ; un contour."""
    if op <= 0.02 or w <= 0.1:
        return ''
    sh = arc_band(C, rx, ry, a0, a1, w, rot=rot)
    core = arc_band(C, rx - w * 0.15, ry - w * 0.15 * ry / rx, a0 + (a1 - a0) * 0.18, a1 - (a1 - a0) * 0.12, w * 0.45, rot=rot)
    pa = (C[0] + rx * math.cos(math.radians(a0 + rot)), C[1] + ry * math.sin(math.radians(a0 + rot)))
    pb = (C[0] + rx * math.cos(math.radians(a1 + rot)), C[1] + ry * math.sin(math.radians(a1 + rot)))
    gr = g_lin(fig, pa, pb, [(0, WIND[4]), (0.5, WIND[3]), (1, WIND[2])])
    items = [(sh, gr, 1), (core, WIND[0], 0.85, 'n')]
    if not ink:
        items = [(sh, gr, 1, 'n'), (core, WIND[0], 0.85, 'n')]
    return outlined(items, w=0.9, op=op)


def gust(fig, pts, w, op=1.0, curl=0.0, core=True):
    """Un ruban de vent le long d'une courbe : fin au départ, plein, puis effilé ; une volute au bout (curl, rayon)."""
    if op <= 0.02:
        return ''
    c = crpath(pts, 30)
    if curl > 0:
        a_end = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
        ctr = (c[-1][0] - math.sin(a_end) * curl, c[-1][1] + math.cos(a_end) * curl)
        a0 = math.atan2(c[-1][1] - ctr[1], c[-1][0] - ctr[0])
        c = c + [(ctr[0] + curl * (1 - 0.35 * k / 8) * math.cos(a0 + 0.55 * k), ctr[1] + curl * (1 - 0.35 * k / 8) * math.sin(a0 + 0.55 * k))
                 for k in range(1, 9)]
    n = len(c) - 1
    ws = [max(0.12, w * math.sin(math.pi * min(1, (i / n) * 1.15)) ** 0.7 * (1 - 0.55 * i / n)) for i in range(n + 1)]
    sh = ribbon(c, ws)
    gr = g_lin(fig, c[0], c[n // 2], [(0, WIND[4]), (0.6, WIND[3]), (1, WIND[2])])
    items = [(sh, gr, 1)]
    if core:
        items.append((ribbon(c[2:-3], [x * 0.38 for x in ws[2:-3]]), WIND[0], 0.85, 'n'))
    return outlined(items, w=0.9, op=op)


def leaf(fig, c, ang, s=1.0, op=1.0, flip=1.0):
    """Une feuille (jade) : deux pointes, une nervure ; flip < 1 : elle tourne sur elle-même (vue de biais)."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    k = max(0.25, abs(flip))

    def P(x, y):
        return (c[0] + (x * ca - y * k * sa) * s, c[1] + (x * sa + y * k * ca) * s)
    sh = sm([P(-1.9, 0), P(-0.6, -0.95), P(0.9, -0.8), P(2.0, 0), P(0.9, 0.75), P(-0.6, 0.85)], sharp=(0, 3), t=0.9)
    rib = ribbon([P(-1.5, 0.02), P(0.2, -0.05), P(1.6, 0)], [0.05, 0.22 * s, 0.05])
    gr = g_lin(fig, P(1.5, -0.9), P(-1.5, 0.9), [(0, LEAF[0]), (0.5, LEAF[1]), (1, LEAF[2])])
    return outlined([(sh, gr, 1), (rib, LEAF[3], 0.55, 'n')], ink=INKW, w=0.55 * s + 0.15, op=op)


def flash(fig, c, r, op=1.0):
    """L'éclat de l'impact : un disque de lumière (dégradé radial), sans contour."""
    if op <= 0.02 or r <= 0.2:
        return ''
    gr = g_rad(fig, c, r, [(0, '#ffffff', op), (0.3, '#ffffff', 0.9 * op), (0.55, WIND[2], 0.7 * op), (0.8, WIND[3], 0.35 * op), (1, WIND[3], 0)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), gr)


def spark(fig, c, s, ang=0.0, op=1.0):
    """Une étincelle d'acier : une petite étoile à quatre pointes, blanc doré."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    pts = []
    for k in range(8):
        r = s if k % 2 == 0 else s * 0.3
        pts.append((c[0] + r * math.cos(a + k * math.pi / 4), c[1] + r * math.sin(a + k * math.pi / 4)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.6)
    return outlined([(sh, '#fff8d2', 1)], ink='#6a4a2a', w=0.5, op=op)


def puff(fig, c, r, op=1.0, seed=0):
    """Une bouffée de poussière (sable clair), quelques boules réunies sous un contour."""
    if op <= 0.02 or r < 0.3:
        return ''
    rnd = [(0.0, 0.0, 1.0), (0.85, 0.2, 0.7), (-0.85, 0.25, 0.66), (0.3, -0.5, 0.6), (-0.4, -0.35, 0.5)][:3 + seed % 3]
    balls = [ellipse(c[0] + dx * r, c[1] + dy * r, rr * r) for dx, dy, rr in rnd]
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#f8ecd0'), (0.5, '#d8bc90'), (1, '#a8866a')])
    return outlined([(b, gr, 1) for b in balls], ink='#5a4040', w=0.7, op=op)


def shadow(fig, c, rx, op):
    """L'ombre douce au sol (dégradé radial, sans flou)."""
    if op <= 0.02:
        return ''
    gr = fig.rad(c[0], c[1], rx, rx * 0.16, [(0, '#0a0418', 0.55 * op), (0.6, '#0a0418', 0.3 * op), (1, '#0a0418', 0)])
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(rx), fm(rx * 0.16), gr)


# ---------- les silhouettes pâles (Zéphyre qui s'efface, les doubles) ----------
_GID = [0]


def ghost_svg(fig, op, M=ID):
    """Une image rémanente du héros : le vrai dessin (on devine encore les yeux, le bandeau, la ceinture) sous un voile
    turquoise pâle qui recouvre aussi le contour (il devient jade) ; translucide."""
    import re
    if op <= 0.02:
        return ''
    _GID[0] += 1
    u = 'gh%d_' % _GID[0]
    svg = fig.svg()
    svg = re.sub(r'id="([^"]+)"', lambda m_: 'id="%s%s"' % (u, m_.group(1)), svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m_: 'url(#%s%s)' % (u, m_.group(1)), svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m_: 'href="#%s%s"' % (u, m_.group(1)), svg)
    inner = svg[svg.index('>') + 1:svg.rindex('</svg>')]
    gid = u + 'veil'
    veil = ['<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="96" y1="10" x2="50" y2="117">'
            '<stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            '</linearGradient>' % (gid, GHOST[0], GHOST[1], GHOST[2])]
    sil, fil = [], []
    for i, p in enumerate(fig.parts):
        tf = ' transform="matrix(%s)"' % ' '.join(fm(v) for v in p.M) if p.M != ID else ''
        d = p.shape.d()
        if p.outline:
            sil.append('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s"/>' % (d, tf, GHOST_INK, GHOST_INK, fm(2 * fig.ow)))
        fil.append('<path d="%s"%s fill="url(#%s)"/>' % (d, tf, gid))
    tm = ' transform="matrix(%s)"' % ' '.join(fm(v) for v in M) if M != ID else ''
    return ('<g%s opacity="%g"><defs>%s</defs>%s<g stroke-linejoin="round" opacity="0.55">%s</g>'
            '<g opacity="0.62">%s</g></g>') % (tm, max(0, min(1, op)), ''.join(veil), inner, ''.join(sil), ''.join(fil))


def place(feet, flip=False, rot=0.0, pivot=(70.0, 80.0), k=0.9):
    """La matrice qui pose un double : ses pieds (64, 116) en `feet`, retourné (il regarde à gauche), tourné, un peu
    plus petit (k) pour laisser de l'air autour de l'ennemi."""
    from atelier import mchain, mT, mR, mS
    M = mchain(mT(feet[0] - Z.FEET[0], feet[1] - Z.FEET[1]), mS(k, k, *Z.FEET))
    if flip:
        M = mchain(M, (-1, 0, 0, 1, 2 * Z.FEET[0], 0))
    if rot:
        M = mchain(M, mR(rot, *pivot))
    return M


# ======================================================================== l'attaque de base : les effets
FX_STAR = {}


def star_out(s):
    p0 = FX_STAR['throw']
    p3 = (EX - 5, EY - 3)
    return bez(p0, (p0[0] + 38, p0[1] - 14), (p3[0] - 42, p3[1] - 16), p3, s)


def star_back(s):
    p0 = (EX - 5, EY - 3)
    p3 = FX_STAR['catch']
    return bez(p0, (p0[0] - 24, p0[1] + 34), (p3[0] + 46, p3[1] + 36), p3, s)


def star_fly(fig, path, s, ang, R=10.0, trail=0.28, arcs=True):
    C = path(s)
    # la traînée : un ruban qui suit la courbe derrière lui
    if trail > 0 and s > 0.02:
        pts = [path(max(0.0, s - trail * k / 10)) for k in range(10, -1, -1)]
        if math.dist(pts[0], pts[-1]) > 2:
            ws = [0.2 + 3.2 * (k / 10) ** 1.4 for k in range(11)]
            tr = ribbon(pts, ws)
            fig.fx_back.append('<path d="%s" fill="%s"/>' % (tr.d(), g_lin(fig, pts[0], pts[-1], [(0, WIND[3], 0), (0.6, WIND[2], 0.55), (1, WIND[1], 0.85)])))
    if arcs:
        for k in (0, 180):
            fig.fx_back.append(crescent(fig, C, R + 3.0, (R + 3.0) * 0.86, ang + k, ang + k + 110, 2.2, op=0.95))
    Z.add_star(fig, 'fstar', C, ang, R=R, squash=0.86, cast=0)


def fx_attack(tl):
    def f(fig, ctx):
        P = ctx['P']
        fig.fx_back.insert(0, shadow(fig, (ctx['feet'][0] + 2, GR), 36, 1.0))
        # le fouetté : un croissant de vent qui suit le bras qui passe au-dessus
        k = env(tl, 320, 345, 370, 420)
        if k:
            W = ctx['wrist']
            fig.fx_back.append(crescent(fig, (W[0] - 8, W[1] + 14), 20, 18, -150, -40, 3.6 * k, op=k))
        # la poussière aux pieds (elle pousse sur les jambes)
        k = env(tl, 340, 360, 420, 560)
        if k:
            fig.fx_back.append(puff(fig, (ctx['feet'][0] + 22 + 6 * (1 - k), GR - 1.6), 2.6 + 1.2 * (1 - k), op=k, seed=1))
            fig.fx_back.append(puff(fig, (ctx['feet'][0] - 18 - 4 * (1 - k), GR - 1.2), 2.0 + 0.8 * (1 - k), op=k * 0.8, seed=2))
        # le shuriken en vol : l'aller (il tournoie), l'arrêt sur l'ennemi, le retour en boomerang
        spin = (tl - T_THROW) * 1.6
        if T_THROW <= tl < T_HIT:
            s = smooth((tl - T_THROW) / (T_HIT - T_THROW)) * 0.75 + 0.25 * (tl - T_THROW) / (T_HIT - T_THROW)
            star_fly(fig, star_out, s, spin, trail=0.3, arcs=tl > T_THROW + 25)
        elif T_HIT <= tl < T_BACK:
            star_fly(fig, star_out, 1.0, spin * 0.5, trail=0.0, arcs=True)
        elif T_BACK <= tl < T_CATCH:
            s = smooth((tl - T_BACK) / (T_CATCH - T_BACK))
            star_fly(fig, star_back, s, spin, trail=0.32)
        # l'impact : éclat, croissants qui s'ouvrent, étincelles d'acier
        if T_HIT - 10 <= tl < T_HIT + 260:
            k = (tl - T_HIT + 10) / 270
            c = (EX - 5, EY - 3)
            fig.fx_front.append(flash(fig, c, 8 + 12 * k, op=1 - k * k))
            for i, a in enumerate((-30, 90, 210)):
                fig.fx_front.append(crescent(fig, c, 8 + 14 * k, (8 + 14 * k) * 0.9, a + 60 * k, a + 60 * k + 85, 2.8 * (1 - k), op=1 - k))
            for i in range(6):
                a = math.radians(-160 + i * 58 + 13 * (i % 2))
                d = 6 + 16 * smooth(k * 1.3)
                p = (c[0] + math.cos(a) * d, c[1] + math.sin(a) * d + 10 * k * k)
                fig.fx_front.append(spark(fig, p, 1.6 * (1 - k) + 0.3, ang=40 * i + 200 * k, op=1 - k))
        # la prise : il claque dans la main (une petite bouffée de vent)
        k = env(tl, T_CATCH - 10, T_CATCH + 10, T_CATCH + 40, T_CATCH + 200)
        if k:
            C = ctx['star'][0]
            fig.fx_front.append(crescent(fig, C, 9 + 5 * (1 - k), 8 + 4 * (1 - k), 200, 320, 2.2 * k, op=k))
            fig.fx_front.append(crescent(fig, C, 9 + 5 * (1 - k), 8 + 4 * (1 - k), 20, 140, 2.2 * k, op=k))
    return f


# ======================================================================== l'attaque spéciale : les effets

def tornado(fig, c, k, height=78.0, phase=0.0, tight=1.0, op=1.0, leaves=14):
    """Le tourbillon de feuilles : des bandes de vent en entonnoir (étroit en bas, large en haut), la moitié avant
    devant elle, la moitié arrière derrière ; des feuilles prises dedans, sur une hélice."""
    if op <= 0.02 or k <= 0.02:
        return
    cx, gy = c
    n = 5
    for i in range(n):
        h = gy - 3 - height * k * (i + 0.4) / n
        r = (8 + 18 * (i / (n - 1)) ** 1.1) * tight
        ry = r * 0.28
        ph = phase * (1.3 - 0.15 * i) + 47 * i
        sway = 3 * math.sin(math.radians(phase * 0.7 + 60 * i))
        w = 2.4 + 1.2 * (i / n)
        fig.fx_back.append(crescent(fig, (cx + sway, h), r, ry, 180 + ph % 360 - 180 + 20, 180 + ph % 360 - 180 + 150, w * 0.7, op=op * 0.8))
        fig.fx_front.append(crescent(fig, (cx + sway, h), r, ry, ph % 360 + 20, ph % 360 + 165, w, op=op))
    for j in range(leaves):
        u = j / leaves
        a = math.radians(phase * 2.2 + j * 137.5)
        hh = gy - 4 - height * k * ((u + phase / 900.0) % 1.0)
        r = (9 + 18 * ((gy - hh) / max(1, height))) * tight
        p = (cx + r * math.cos(a), hh + r * 0.28 * math.sin(a))
        L = leaf(fig, p, phase * 3 + j * 50, 1.1, op=op, flip=math.cos(a + phase / 40))
        (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(L)


def leaf_stream(fig, p0, p1, p2, p3, s0, s1, n, seed=0, op=1.0, size=1.1):
    for j in range(n):
        u = s0 + (s1 - s0) * ((j * 0.618 + seed * 0.29) % 1.0)
        p = bez(p0, p1, p2, p3, u)
        off = 5 * math.sin(j * 2.3 + seed)
        fig.fx_front.append(E.feuille(fig, p[0], p[1] + off, j * 67 + seed * 30 + u * 400, size * 0.7, op=op))


# ---- l'attaque spéciale (effets refaits le 28/11 avec effets_pro : le tourbillon d'UNE silhouette, rubans et
# croissants de vent d'un seul tenant sans contour sombre, feuilles d'une forme, lumière et étincelles ; les doubles,
# le rythme et les instants inchangés)
import effets_pro as E  # noqa: E402


def _ell(C, rx, ry, a0, a1, rot=0.0, n=14):
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((C[0] + x * cr - y * sr, C[1] + x * sr + y * cr))
    return out


def crescent_p(fig, C, rx, ry, a0, a1, w, op=1.0, rot=0.0, ink=True):
    if op <= 0.02 or w <= 0.1:
        return ''
    return E.ruban(fig, _ell(C, rx, ry, a0, a1, rot), w * 1.6, 'vent', op=op, kind='fuseau', halo=0.4)


def gust_p(fig, pts, w, op=1.0, curl=0.0, core=True):
    if op <= 0.02:
        return ''
    c = crpath(pts, 16)
    if curl > 0:
        a_end = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
        ctr = (c[-1][0] - math.sin(a_end) * curl, c[-1][1] + math.cos(a_end) * curl)
        a0 = math.atan2(c[-1][1] - ctr[1], c[-1][0] - ctr[0])
        c = c + [(ctr[0] + curl * (1 - 0.35 * k / 8) * math.cos(a0 + 0.55 * k), ctr[1] + curl * (1 - 0.35 * k / 8) * math.sin(a0 + 0.55 * k))
                 for k in range(1, 9)]
    return E.ruban(fig, c, w * 1.7, 'vent', op=op, kind='pointe', halo=0.4)


def leaf_p(fig, c, ang, s=1.0, op=1.0, flip=1.0):
    return E.feuille(fig, c[0], c[1], ang, s * 0.7 * max(0.45, abs(flip)) ** 0.3, op=op)


def flash_p(fig, c, r, op=1.0):
    return E.lumiere(fig, c, r * 1.5, op, 'vent')


def tornado_p(fig, c, k, height=78.0, phase=0.0, tight=1.0, op=1.0, leaves=14):
    """Le tourbillon de feuilles : UN cyclone posé au sol (voile et rubans en hélice d'une silhouette), ce qu'il
    avale passe entre ses deux moitiés ; quelques feuilles prises dedans, sur une hélice."""
    if op <= 0.02 or k <= 0.02:
        return
    bk, fr = E.tourbillon(fig, c, height * k, 26 * tight, phase, 'vent', op=op, split=True)
    fig.fx_back.append(bk)
    fig.fx_front.append(fr)
    n = max(3, leaves // 3)
    for j in range(n):
        u = j / n
        a = math.radians(phase * 2.2 + j * 137.5)
        hh = c[1] - 4 - height * k * ((u + phase / 900.0) % 1.0)
        r = (9 + 18 * ((c[1] - hh) / max(1, height))) * tight
        p = (c[0] + r * math.cos(a), hh + r * 0.28 * math.sin(a))
        (fig.fx_front if math.sin(a) > 0 else fig.fx_back).append(leaf_p(fig, p, phase * 3 + j * 50, 1.1, op=op, flip=math.cos(a + phase / 40)))


def leaf_stream_p(fig, p0, p1, p2, p3, s0, s1, n, seed=0, op=1.0, size=1.1):
    leaf_stream(fig, p0, p1, p2, p3, s0, s1, max(2, n // 2), seed=seed, op=op, size=size)


def fx_special(tl, P_clone):
    def f(fig, ctx):
        home = (Z.FEET[0] + 2, GR)
        v = vis_special(tl)
        fig.fx_back.insert(0, shadow(fig, (home[0], GR), 36, max(v, 0.0)))
        # 0) le vent se lève à ses pieds, des feuilles montent
        k = env(tl, 0, 200, 330, 420)
        if k:
            for i in range(3):
                r = 14 + 6 * i
                fig.fx_back.append(crescent_p(fig, (home[0], GR - 1.5 - 2 * i), r, r * 0.22, 190 + tl * 0.6 + 70 * i, 330 + tl * 0.6 + 70 * i, 1.8, op=k * 0.8))
                fig.fx_front.append(crescent_p(fig, (home[0], GR - 1.5 - 2 * i), r, r * 0.22, 10 + tl * 0.6 + 70 * i, 150 + tl * 0.6 + 70 * i, 2.2, op=k))
            for j in range(4):
                u = ((tl / 420.0) * 0.9 + j * 0.143) % 1.0
                a = math.radians(j * 97 + tl * 0.9)
                p = (home[0] + (12 + 8 * u) * math.cos(a), GR - 4 - 34 * u)
                fig.fx_front.append(leaf_p(fig, p, j * 70 + tl, 1.0, op=k * (1 - u ** 3), flip=math.cos(a)))
        # 1) le tourbillon l'avale
        k = env(tl, 260, 360, 440, 540)
        if k:
            tornado_p(fig, home, k, phase=tl * 1.1, tight=1.0, op=k)
        # 2) la rafale de feuilles file jusqu'à l'ennemi
        k = env(tl, 430, 470, 520, 600)
        if k:
            s1 = smooth((tl - 430) / 110)
            p0, p3 = (home[0] + 6, GR - 30), (EX - 6, EY + 4)
            for i, dy in enumerate((0, 12)):
                q0, q3 = (p0[0], p0[1] + dy), (p3[0], p3[1] + dy * 0.5)
                pts = [bez(q0, (q0[0] + 30, q0[1] - 40), (q3[0] - 40, q3[1] - 40), q3, max(0.0, s1 - 0.5 + 0.5 * u)) for u in (0, 0.25, 0.5, 0.75, 1)]
                fig.fx_front.append(gust_p(fig, pts, 4.0 - i, op=k, curl=3.0 if s1 > 0.9 else 0))
                leaf_stream_p(fig, q0, (q0[0] + 30, q0[1] - 40), (q3[0] - 40, q3[1] - 40), q3, max(0, s1 - 0.5), s1, 8, seed=i, op=k)
        # 3) les doubles surgissent, frappent ensemble, s'effritent
        k_in = smooth((tl - 500) / 90)
        k_out = 1 - smooth((tl - 860) / 110)
        g = min(k_in, k_out)
        if g > 0.02 and tl >= 500:
            solid = 0.55 + 0.35 * smooth((tl - 560) / 40)
            # l'ombre de chaque double, puis le double du dessus (derrière), puis les deux autres
            for feet in ((EX - 34, GR), (EX + 33, GR)):
                fig.fx_back.append(shadow(fig, (feet[0], GR), 24, g * 0.8))
            spots = [((EX - 8, EY - 30), False, 52.0), ((EX - 34, GR), False, 0.0), ((EX + 33, GR), True, 0.0)]
            for (feet, flip, rot), cf in zip(spots, P_clone):
                M = place(feet, flip, rot)
                fig.fx_front.append(ghost_svg(cf, g * solid, M))
        # les trois croissants qui tournent autour de lui, l'éclair, l'arrêt sur l'image
        k = env(tl, SP_HIT - 20, SP_HIT, SP_HIT + 200, SP_HIT + 320)
        if k:
            c = (EX, EY)
            sweep = smooth((tl - SP_HIT + 20) / 160) * 120
            for i, a in enumerate((200, 320, 80)):
                fig.fx_front.append(crescent_p(fig, c, 19 - 2 * i, 13 + 2 * i, a + sweep, a + sweep + 100, 3.2, op=k, rot=-20 + 25 * i))
            fig.fx_front.append(flash_p(fig, c, 10 + 10 * k, op=k))
            for i in range(4):
                a = math.radians(-140 + i * 85)
                d = 9 + 12 * smooth((tl - SP_HIT) / 260)
                fig.fx_front.append(E.etincelle(fig, c[0] + math.cos(a) * d, c[1] + math.sin(a) * d, 60 * math.cos(a), 60 * math.sin(a), 0.7, 'vent', op=k))
        # 4) ils s'effritent en feuilles, qui repartent vers elle
        k = env(tl, 850, 900, 980, 1080)
        if k:
            for j in range(8):
                u = (tl - 850) / 230
                a = math.radians(j * 45 + 7 * (j % 3))
                d = 6 + 30 * smooth(u) * (0.6 + 0.4 * ((j * 0.37) % 1))
                p = (EX + math.cos(a) * d, EY + 10 + math.sin(a) * d * 0.8 + 12 * u * u)
                fig.fx_front.append(leaf_p(fig, p, j * 40 + tl * 0.8, 1.1, op=k, flip=math.cos(j + tl / 60)))
        k = env(tl, 980, 1040, 1120, 1220)
        if k:
            s1 = smooth((tl - 980) / 180)
            p0, p3 = (EX - 4, EY + 14), (home[0] + 4, GR - 26)
            pts = [bez(p0, (p0[0] - 30, p0[1] - 46), (p3[0] + 40, p3[1] - 44), p3, max(0.0, s1 - 0.5 + 0.5 * u)) for u in (0, 0.25, 0.5, 0.75, 1)]
            fig.fx_front.append(gust_p(fig, pts, 3.6, op=k, curl=3.0 if s1 > 0.85 else 0))
            leaf_stream_p(fig, p0, (p0[0] - 30, p0[1] - 46), (p3[0] + 40, p3[1] - 44), p3, max(0, s1 - 0.5), s1, 10, seed=3, op=k)
        # 5) le tourbillon la rend, les feuilles retombent
        k = env(tl, 1080, 1160, 1240, 1360)
        if k:
            tornado_p(fig, home, k, phase=tl * 1.1 + 200, tight=1.0, op=k, leaves=10)
        k = env(tl, 1260, 1300, 1380, 1600)
        if k:
            u = (tl - 1260) / 340
            for j in range(3):
                p = (home[0] - 22 + j * 18 + 4 * math.sin(tl / 70 + j), GR - 30 + 26 * u * (0.7 + 0.3 * ((j * 0.41) % 1)))
                fig.fx_front.append(leaf_p(fig, p, j * 60 + tl * 0.5, 1.0, op=k, flip=math.cos(tl / 50 + j)))
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
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def timeline():
    seq = [('idle', 3.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


_CLONES = []


def clones():
    if not _CLONES:
        dive = dict(CLONE, crouch=2, lean=4, fw=(104, 62), nw=(12, -2), t=-2.5, e=-2.5)
        for p in (dive, CLONE, CLONE):
            P = dict(Z.REST, **p)
            for k in ('fw', 'nw', 'head'):
                P[k] = tuple(P[k])
            _CLONES.append(Z.build(pose=P, frame=VIEW))
    return _CLONES


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P = pose_at(T, act, t0)
    tl = (T - t0) * 1000
    if act == 'attack':
        if 'throw' not in FX_STAR:
            FX_STAR['throw'] = Z.build(pose=pose_at(t0 + T_THROW / 1000, act, t0)).ctx['star'][0]
            FX_STAR['catch'] = Z.build(pose=pose_at(t0 + T_CATCH / 1000, act, t0)).ctx['star'][0]
        return Z.build(ow=ow, pose=P, fx=[fx_attack(tl)], frame=view).svg()
    if act == 'special':
        v = vis_special(tl)
        fx = fx_special(tl, clones())
        if v >= 0.999:
            return Z.build(ow=ow, pose=P, fx=[fx], frame=view).svg()
        canvas = Figure(*view, ow=ow)
        canvas.ctx = dict(P=P, feet=Z.FEET)
        if v > 0.01:
            me = Z.build(ow=ow, pose=P, frame=view)
            canvas.fx_back.append(ghost_svg(me, 0.85 * v))
        fx(canvas, canvas.ctx)
        return canvas.svg()

    def sh(fig, ctx):
        fig.fx_back.insert(0, shadow(fig, (ctx['feet'][0] + 2, GR), 36, 1.0))
    return Z.build(ow=ow, pose=P, fx=[sh], frame=view).svg()


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
        moments = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]] or \
            [0.8, a_s + 0.1, a_s + 0.28, a_s + 0.36, a_s + 0.42, a_s + 0.52, a_s + 0.66, a_s + 0.77,
             s_s + 0.2, s_s + 0.36, s_s + 0.48, s_s + 0.56, s_s + 0.62, s_s + 0.9, s_s + 1.05, s_s + 1.2, s_s + 1.3, s_s + 1.5]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 6), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(Z.TMP, 'planche.png')
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
    for width, colors in ((400, 128), (380, 96), (360, 80)):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(TMP, 'v%04d.png'),
                        '-vf', 'fps=12,scale=%d:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=%d:stats_mode=diff[p];'
                        '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle' % (width, colors), gifp], check=True)
        if os.path.getsize(gifp) <= 3 * 1024 * 1024:
            break
    print('écrit', mp4, '(%d ko)' % (os.path.getsize(mp4) // 1024), 'et', gifp, '(%d ko)' % (os.path.getsize(gifp) // 1024))
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
