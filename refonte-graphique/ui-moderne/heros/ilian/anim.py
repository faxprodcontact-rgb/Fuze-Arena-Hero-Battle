# Ilian vectoriel ANIMÉ (refonte des héros du 26/11/2026, même méthode que Kael : ../kael/anim.py) : les mêmes
# animations que son pixel art (refonte-graphique/pixel/hd/anim/ilian/build.py) — respiration, attaque de base « le
# trident s'abat », attaque spéciale « Colère des marées » — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/heros/ilian/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/ilian/
#   python3 refonte-graphique/ui-moderne/heros/ilian/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (ilian.py) est fait de morceaux ; chaque image le redessine dans une POSE (buste qui respire et se
# penche depuis les hanches, tête, crinière et barbe qui suivent avec retard, cape, bras lointain ; le bras proche est
# placé par cinématique inverse depuis le poing, qui tient le trident). Les poses clés reprennent celles du pixel art
# (mêmes prises, mêmes angles, même glissement de la hampe dans la main, mêmes temps : longue préparation, coup très
# court, impact tenu, retour) et sont reliées par des courbes douces sans dépassement (24 images par seconde). Les
# effets d'eau (traînée, gerbes, gouttes, écume, tourbillon, vague qui s'enroule et s'écrase) sont dessinés dans le
# même style : dégradés, un seul contour, aucun flou SVG ; jamais de rayons droits répétés.
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
import ilian as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'ilian')
TMP = os.environ.get('ILIAN_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-24, -42, 292, 164.25)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WINK = '#0c1846'                     # le contour de l'eau (un bleu nuit presque noir)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']

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


NUM = ['crouch', 'lean', 'tilt', 'mane', 'beard', 'cape', 'far', 'roar', 'glow', 'bend', 'stretch', 'ang', 'slide',
       'plant', 'grip', 'hx', 'hy', 'headx', 'heady', 'epx', 'epy']


def flat(k):
    d = dict(crouch=0, lean=0, tilt=0, mane=0, beard=0, cape=0, far=0, roar=0, glow=0, bend=-1, stretch=0, ang=-90,
             slide=0, plant=1, grip=1, hx=K.G0[0], hy=K.G0[1], headx=0, heady=0, epx=0, epy=0)
    for key, v in k.items():
        if key == 'hand':
            d['hx'], d['hy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'ep':
            d['epx'], d['epy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, comme le pixel art)
# Angles de la hampe en degrés, y vers le bas (−90 = les dents en haut). La main (prise) est dans le repère du buste.
# 2) L'attaque de base : il arrache le trident du sol, le lève haut au-dessus de l'épaule en se cambrant (la hampe glisse
# dans sa main jusqu'au talon : plus d'allonge), tient, puis l'abat d'un seul bras devant lui (image étirée par la
# vitesse), impact tenu (gerbe d'eau au bout des dents), il revient en garde et replante le trident.
LIFT = dict(plant=0)
ATTACK = [
    (0, {}),
    (110, dict(hand=(22, 50), ang=-93, slide=-10, crouch=1, lean=-1, ep=(0, -1), mane=1, cape=1, plant=0)),
    (350, dict(hand=(30, 30), ang=-110, slide=-38, crouch=2, lean=-3, head=(-1, 0), tilt=-3, ep=(-1, -2), mane=1, beard=1,
               cape=1, far=-3, roar=0.3, plant=0)),
    (480, dict(hand=(29.4, 29), ang=-113, slide=-38, crouch=2.2, lean=-3.4, head=(-1.2, 0), tilt=-3.5, ep=(-1, -2.2), mane=1,
               beard=1, cape=1, far=-3.5, roar=0.4, plant=0)),
    (530, dict(hand=(72, 52), ang=-28, slide=-38, crouch=1, lean=2, ep=(0, -1), mane=-1, beard=-1, cape=-1, far=3, stretch=4,
               grip=-1, bend=1, roar=0.8, plant=0)),
    (580, dict(hand=(70, 70), ang=18, slide=-38, crouch=3, lean=5, head=(1, 1), tilt=3, mane=-1, beard=-1, cape=-1, far=7,
               grip=-1, bend=1, roar=1, stretch=1.5, plant=0)),
    (630, dict(hand=(70, 70.4), ang=18.5, slide=-38, crouch=3.2, lean=5.2, head=(1, 1.2), tilt=3.4, mane=-1.2, beard=-1.2,
               cape=-1.2, far=7.5, grip=-1, bend=1, roar=1, plant=0)),
    (760, dict(hand=(70, 70), ang=18, slide=-38, crouch=3, lean=5, head=(1, 1), tilt=2.5, mane=0, beard=0, cape=0, far=4,
               grip=-1, bend=1, roar=0.8, plant=0)),
    (860, dict(hand=(58, 66), ang=8, slide=-30, crouch=2, lean=3, mane=1, beard=1, cape=1, grip=-1, bend=1, roar=0.3, plant=0)),
    (960, dict(hand=(28, 58), ang=-75, slide=-20, crouch=1, lean=1, mane=1, grip=1, bend=-1, plant=0)),
    (1060, dict(hand=(20, 60), ang=-86, slide=-2, crouch=1, bend=-1, plant=0)),
    (1180, dict(crouch=1, plant=1)),
    (1330, {}),
]
ATTACK_HIT = 580

# 3) L'attaque spéciale « Colère des marées » : il arrache le trident et le lève tout droit vers le ciel (un tourbillon
# d'eau naît à ses pieds et monte autour de lui, les pierres de mer s'allument). Devant lui, la mer se lève : une vague
# pousse du sol, grandit jusqu'à le dépasser et enroule sa crête d'écume. Il abat le trident pour la désigner : la vague
# bascule, s'écrase sur l'ennemi (arrêt sur l'image), éclate en gerbes et en gouttes, roule en écume et se retire.
SPECIAL = [
    (0, {}),
    (120, dict(hand=(20, 54), crouch=1, lean=-1, ep=(0, -1), mane=1, cape=1, plant=0, glow=0.5)),
    (260, dict(hand=(23, 44), crouch=0, lean=-2, head=(0, -1), ep=(-1, -2), mane=1, beard=1, cape=1, plant=0, glow=1)),
    (480, dict(hand=(27, 30), lean=-2, head=(0, -1), tilt=-2, ep=(-1, -2.2), mane=0, beard=1, plant=0, glow=1.5, roar=0.5)),
    (620, dict(hand=(27, 29.6), lean=-2.4, head=(0, -1.2), tilt=-2.5, ep=(-1, -2.2), mane=-1, cape=-1, plant=0, glow=2, roar=0.8)),
    (820, dict(hand=(27, 29), lean=-3, head=(0, -1.2), tilt=-3, ep=(-1, -2.4), mane=-1, beard=-1, cape=-1, plant=0, glow=2, roar=1)),
    (880, dict(hand=(68, 48), ang=-24, slide=-30, crouch=2, lean=3, ep=(0, -1), mane=1, beard=1, cape=1, far=3, grip=-1, bend=1,
               stretch=4, plant=0, glow=2, roar=1)),
    (940, dict(hand=(74, 62), ang=4, slide=-30, crouch=3, lean=5, head=(1, 1), tilt=3, mane=1, beard=1, cape=1, far=7, grip=-1,
               bend=1, plant=0, glow=1.6, roar=1)),
    (1160, dict(hand=(74, 62.4), ang=4.5, slide=-30, crouch=3.2, lean=5.2, head=(1, 1.2), tilt=3, mane=0, beard=0, cape=0, far=6,
                grip=-1, bend=1, plant=0, glow=1.2, roar=1)),
    (1280, dict(hand=(73, 62), ang=3, slide=-30, crouch=2, lean=4, mane=-1, beard=-1, cape=-1, far=3, grip=-1, bend=1, plant=0,
                glow=0.8, roar=0.6)),
    (1380, dict(hand=(62, 64), ang=-2, slide=-24, crouch=2, lean=3, mane=-1, beard=-1, grip=-1, bend=1, plant=0, glow=0.5, roar=0.3)),
    (1480, dict(hand=(40, 66), ang=8, slide=-26, crouch=1, lean=1, cape=1, grip=-1, bend=1, plant=0, glow=0.3)),
    (1600, dict(hand=(22, 60), ang=-74, slide=-2, crouch=1, mane=1, cape=1, grip=1, bend=-1, plant=0)),
    (1720, dict(crouch=1, plant=1)),
    (1900, {}),
]
SP_HIT = 1160                         # la vague s'écrase (arrêt sur l'image)
WAVE_X = 128.0                        # où la vague se lève, devant le roi
CRASH_X = 212.0                       # où elle s'écrase (l'ennemi)


# ======================================================================== la respiration (en boucle, 3 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la pierre de mer du trident s'éveille lentement (les dents s'éclairent de bleu, lueur douce autour du
    fer) et la longue crinière blanche flotte plus ample dans son dos.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(mer=0.5 - 0.5 * math.cos(u), mane=1.6 * math.sin(u - 1.9))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    return dict(breath=br, crouch=0.45 * (0.5 - 0.5 * math.cos(u - 2.4)), heady=0.35 * math.sin(u - 1.9),
                tilt=0.6 * math.sin(u - 1.2), mane=0.9 * math.sin(u - 1.9), beard=0.8 * math.sin(u - 2.3),
                cape=0.8 * math.sin(u - 0.8), far=1.2 * math.sin(u - 1.0), glow=0.15 * br)


def pose_at(T, action=None, t0=0.0):
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
    P['breath'] = w * idl['breath']
    sg = signe(T)
    P['mane'] += w * sg['mane']
    P['mer'] = w * sg['mer']
    P['hand'] = (P.pop('hx'), P.pop('hy'))
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ep'] = (P.pop('epx'), P.pop('epy'))
    P['plant'] = max(0.0, min(1.0, P['plant']))
    P['blink'] = 1.0 if (w > 0.95 and 1.36 <= (T % IDLE_T) < 1.46) else 0.0
    return P


# ======================================================================== les effets d'eau (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def drop(fig, x, y, vx, vy, r=1.0, op=1.0):
    """Une goutte d'eau : ronde devant, effilée derrière (dans le sens de sa course), éclairée en haut à droite."""
    if op <= 0.02:
        return ''
    a = math.atan2(vy, vx) if (vx or vy) else math.pi / 2
    pts = [(x + r * math.cos(a + math.radians(d)), y + r * math.sin(a + math.radians(d))) for d in (-90, -45, 0, 45, 90)]
    tail = (x - math.cos(a) * r * 2.6, y - math.sin(a) * r * 2.6)
    sh = sm(pts + [tail], sharp=(5,), t=0.9)
    gr = g_lin(fig, (x + r, y - r), tail, [(0, WATER[1]), (0.45, WATER[2]), (1, WATER[3])])
    return outlined([(sh, gr, 1), (ellipse(x + r * 0.25, y - r * 0.3, r * 0.38, r * 0.26), '#ffffff', 0.95, 'n')], w=1.0, op=op)


def foam(fig, cx, cy, r, op=1.0, seed=0):
    """Une boule d'écume : quelques bulles réunies sous un contour, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = [(0.0, 0.0, 1.0), (0.78, 0.22, 0.72), (-0.82, 0.3, 0.68), (0.18, -0.58, 0.64), (-0.4, -0.4, 0.5), (1.3, 0.5, 0.45)]
    rnd = rnd[:4 + seed % 3]
    balls = [(cx + dx * r, cy + dy * r, rr * r) for dx, dy, rr in rnd]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r * 0.9), [(0, '#ffffff'), (0.5, WATER[1]), (1, WATER[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), WINK, WINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="#ffffff" opacity="0.9"/>' % (fm(cx + 0.3 * r), fm(cy - 0.35 * r), fm(0.3 * r))
    return '<g opacity="%g">%s%s%s</g>' % (max(0, min(1, op)), sil, col, hi)


def sheet(fig, base, ang, length, bend, w, op=1.0, tail=0.0):
    """Une nappe d'eau qui jaillit : un ruban courbe, large à la base, fin et clair au bout (ang : degrés, y vers le bas)."""
    if length < 1 or op <= 0.02:
        return ''
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    b = bend / 60.0
    p0 = (base[0] + d[0] * length * tail, base[1] + d[1] * length * tail)
    p1 = (base[0] + d[0] * length * 0.35 + nrm[0] * length * b * 0.3, base[1] + d[1] * length * 0.35 + nrm[1] * length * b * 0.3)
    p2 = (base[0] + d[0] * length * 0.7 + nrm[0] * length * b * 0.55, base[1] + d[1] * length * 0.7 + nrm[1] * length * b * 0.55)
    p3 = (base[0] + d[0] * length + nrm[0] * length * b, base[1] + d[1] * length + nrm[1] * length * b)
    sh = lock(p0, p1, p2, p3, w * (1 - tail * 0.6), n=12, bulge=0.35, tipw=w * 0.22)
    core = lock(p0, p1, p2, ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2), w * 0.42 * (1 - tail * 0.6), n=10, bulge=0.1)
    gr = g_lin(fig, p0, p3, [(0, WATER[4]), (0.4, WATER[3]), (0.8, WATER[2]), (1, WATER[1])])
    gc = g_lin(fig, p0, p3, [(0, WATER[3]), (1, '#ffffff')])
    # le bout de la nappe se casse en une goutte ronde (jamais une pointe d'aiguille)
    rr = max(0.6, w * 0.2)
    bead = ellipse(p3[0] + d[0] * rr * 0.6, p3[1] + d[1] * rr * 0.6, rr, rr)
    return outlined([(sh, gr, 1), (bead, WATER[1], 1), (core, gc, 0.75, 'n'),
                     (ellipse(p3[0] + d[0] * rr * 0.6 + rr * 0.3, p3[1] + d[1] * rr * 0.6 - rr * 0.35, rr * 0.35, rr * 0.3), '#ffffff', 1, 'n')], op=op)


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


def trail(fig, C, R, a0, a1, w, op=1.0):
    """La traînée d'eau des dents du trident : un croissant courbe qui s'efface vers l'arrière, avec sa crête d'écume."""
    if abs(a1 - a0) < 4 or op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + 1.0, a0, a1, w)
    crest = arc_band(C, R + 1.6, a0, a1, w * 0.34)
    g1 = g_lin(fig, pa, pb, [(0, WATER[3], 0), (0.5, WATER[3], 0.55 * op), (1, WATER[2], 0.9 * op)])
    g2 = g_lin(fig, pa, pb, [(0, WATER[1], 0), (0.6, WATER[1], 0.8 * op), (1, '#ffffff', op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, crest.d(), g2)


def ring_arc(fig, c, rx, ry, a0, a1, w, op=1.0):
    """Un morceau d'anneau d'eau (ellipse vue de 3/4) qui s'effile aux deux bouts : le tourbillon."""
    if op <= 0.02 or ry <= 0:
        return ''
    n = 24
    pts = [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    ws = [w * math.sin(math.pi * i / n) ** 0.7 + 0.15 for i in range(n + 1)]
    sh = ribbon(pts, ws)
    gr = g_lin(fig, pts[0], pts[-1], [(0, WATER[3]), (0.5, WATER[2]), (1, WATER[1])])
    hi = ribbon([(p[0], p[1] - w * 0.2) for p in pts[4:-4]], [x * 0.3 for x in ws[4:-4]])
    return outlined([(sh, gr, 1), (hi, '#ffffff', 0.8, 'n')], w=1.1, op=op)


def wave(fig, xb, h, L, lip, r, op=1.0, foamy=1.0):
    """La vague : le dos qui monte du sol, la crête qui s'enroule vers l'avant (lip) en volute (r), le creux ; écume
    blanche sur la crête. Un seul contour."""
    if h < 1.5 or op <= 0.02:
        return ''
    G = GR + 0.4
    top = (xb + lip * 0.3, G - h)
    pts = [(xb - L * 0.62, G), (xb - L * 0.34, G - h * 0.22), (xb - L * 0.14, G - h * 0.62), (top[0] - r * 0.6, G - h * 0.97), top,
           (xb + lip * 0.75, G - h + r * 0.5), (xb + lip, G - h + r * 1.5), (xb + lip - r * 0.7, G - h + r * 2.3),
           (xb + lip - r * 1.5, G - h + r * 1.6), (xb + lip * 0.5, G - h + r * 1.6), (xb + L * 0.1, G - h * 0.45),
           (xb + L * 0.36, G - h * 0.08), (xb + L * 0.5, G)]
    sh = sm(pts, sharp=(0, 6, 12), t=0.9)
    gr = g_lin(fig, (xb + lip * 0.5, G - h), (xb - L * 0.3, G), [(0, WATER[2]), (0.3, WATER[3]), (0.7, WATER[4]), (1, WATER[5])])
    # le creux sous la volute (plus sombre), la face éclairée, l'écume de la crête, des reflets
    hollow = sm([(xb + lip - r * 1.4, G - h + r * 1.7), (xb + lip * 0.5, G - h + r * 1.7), (xb + L * 0.08, G - h * 0.45),
                 (xb + L * 0.05, G - h * 0.2), (xb - L * 0.05, G - h * 0.5), (xb + lip * 0.2, G - h + r * 1.1)])
    crest = sm([(xb - L * 0.2, G - h * 0.72), (top[0] - r * 0.7, G - h * 0.99), top, (xb + lip * 0.78, G - h + r * 0.55),
                (xb + lip, G - h + r * 1.5), (xb + lip * 0.86, G - h + r * 1.2), (xb + lip * 0.5, G - h + r * 0.55),
                (top[0] - r * 0.5, G - h + r * 0.6), (xb - L * 0.15, G - h * 0.6)])
    glint = ribbon([(xb - L * 0.42, G - h * 0.12), (xb - L * 0.26, G - h * 0.4), (xb - L * 0.1, G - h * 0.68)], [0.2, max(0.6, h * 0.025), 0.2])
    items = [(sh, gr, 1),
             (hollow, WATER[5], 0.45, 'n'),
             (crest, g_lin(fig, top, (xb - L * 0.2, G - h * 0.6), [(0, '#ffffff'), (1, WATER[1])]), min(1, foamy), 'n'),
             (glint, WATER[1], 0.7, 'n')]
    return outlined(items, w=1.5, op=op)


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


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---- l'attaque de base : la traînée d'eau des dents, la gerbe à l'impact

HIT = {}


def fx_attack(tl, ang_prev):
    def f(fig, ctx):
        G, ang, tip = ctx['G'], ctx['ang'], ctx['tip']
        R = math.dist(G, tip)
        a1 = ang
        a0 = ang_prev
        if abs(a1 - a0) > 16 and 470 < tl < 640:
            fig.fx_back.append(trail(fig, G, R, a0, a1, 13, op=1.0))
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0 and 'c' in HIT:
            c = HIT['c']
            e = env(tau, 0, 0.04, 0.14, 0.42)
            if e > 0:
                fig.fx_front.append(sheet(fig, (c[0] + 1, c[1]), -62, 14 * e + 4, 22, 5.4, op=1))
                fig.fx_front.append(sheet(fig, (c[0] + 3, c[1] + 1), -24, 11 * e + 3, 20, 4.4, op=1))
                fig.fx_back.append(sheet(fig, (c[0] - 2, c[1]), -112, 10 * e + 3, -20, 4.0, op=1))
                fig.fx_front.append(foam(fig, c[0] + 1.5, c[1] + 0.5, 3.4 * e, op=1, seed=1))
            for i, (vx, vy, r) in enumerate(((60, -80, 1.2), (95, -30, 1.0), (25, -110, 0.9), (75, 20, 0.8), (-30, -70, 0.9),
                                             (45, -55, 1.3), (110, -60, 0.8), (10, -40, 0.7))):
                if tau < 0.65:
                    x, y = ballistic(c, (vx, vy), 220, tau)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 220 * tau, r, op=min(1, (0.65 - tau) * 5)))
            if 0.12 < tau < 0.7:
                k = (tau - 0.12) / 0.58
                fig.fx_back.append(foam(fig, c[0] + 3 + 3 * k, c[1] - 2 - 4 * k, 2.4 * (1 - k) + 0.6, op=0.9 * (1 - k), seed=2))
    return f


# ---- l'attaque spéciale

def fx_special(tl, ang_prev):
    def f(fig, ctx):
        P = ctx['P']
        G, ang, tip = ctx['G'], ctx['ang'], ctx['tip']
        t = tl
        cx = 64.0
        # le tourbillon : des anneaux d'eau qui naissent à ses pieds et montent autour de lui en tournant (moitié
        # arrière derrière lui, moitié avant devant)
        wh = env(t, 100, 300, 860, 1080)
        if wh > 0:
            for j in range(2):
                k = ((t - 100) / 1000.0 + j / 2.0) % 1.0
                y = GR - 4 - 74 * k
                rx = 31 + 7 * math.sin(math.pi * k) + 5 * j
                ry = 5.0 + 2 * math.sin(math.pi * k)
                op = wh * min(1, k * 6) * min(1, (1 - k) * 3)
                rot_ = (t * 0.25 + j * 140) % 120
                w = 3.4 + 1.4 * math.sin(math.pi * k)
                # derrière lui : le grand arc ; devant : deux bouts d'anneau sur les côtés (il tourne autour de lui)
                fig.fx_back.append(ring_arc(fig, (cx, y), rx, ry, 190 + rot_ * 0.2, 345 + rot_ * 0.2, w * 0.85, op=op * 0.9))
                fig.fx_front.append(ring_arc(fig, (cx, y), rx, ry, 8 + rot_ * 0.3, 62 + rot_ * 0.3, w, op=op))
                fig.fx_front.append(ring_arc(fig, (cx, y), rx, ry, 128 + rot_ * 0.2, 176 + rot_ * 0.05, w * 0.8, op=op))
            for i in range(10):
                fr = (i * 0.618) % 1
                x0 = 30 + 68 * fr
                k = ((t / 1000.0) * (0.6 + 0.3 * ((i * 0.37) % 1)) + (i * 0.29) % 1) % 1
                fig.fx_front.append(drop(fig, x0 + 3 * math.sin(k * 6 + i), GR - 6 - 70 * k, 0, -1, 0.8 + 0.3 * (i % 3) / 2,
                                         op=wh * (1 - k) * min(1, k * 5)))
        # la flaque qui frémit, puis la vague qui se lève devant lui
        if 120 <= t < 400:
            e = env(t, 120, 220, 300, 400)
            fig.fx_back.append(outlined([(ribbon([(WAVE_X - 16, GR + 0.3), (WAVE_X, GR - 1.2), (WAVE_X + 16, GR + 0.3)], [0.3, 2.6 * e, 0.3]),
                                          g_lin(fig, (WAVE_X, GR - 2), (WAVE_X, GR), [(0, WATER[2]), (1, WATER[4])]), 1)], op=e))
        if 260 <= t < SP_HIT:
            if t < 880:
                k = smooth((t - 260) / 560.0)
                h = 6 + 100 * k
                L = 26 + 34 * k
                lip = 4 + 26 * k
                r = 3 + 7 * k
                xb = WAVE_X - 4 * k
            else:
                # elle bascule en avant vers l'ennemi
                k = smooth((t - 880) / (SP_HIT - 880.0))
                h = 106 - 40 * k
                L = 60 + 30 * k
                lip = 30 + 38 * k
                r = 10 - 2 * k
                xb = WAVE_X - 4 + (CRASH_X - 50 - WAVE_X) * k
            fl = 1 + 0.03 * math.sin(t / 40.0)
            fig.fx_back.append(wave(fig, xb, h * fl, L, lip, r))
            if t > 420:
                for j, (dx, dy) in enumerate(((4, -3), (10, 2), (-2, -6))):
                    kk = ((t - 420) / 260.0 + j * 0.33) % 1
                    x, y = xb + lip + dx + 10 * kk, GR - h + r + dy - 6 * kk
                    fig.fx_back.append(drop(fig, x, y, 1, 0.4, 0.8 + 0.3 * j, op=1 - kk))
        # le trident désigne l'ennemi : un ruban d'eau en croissant derrière les dents
        if 840 <= t <= 1100:
            a1 = ang
            a0 = -90.0
            e = env(t, 840, 880, 960, 1100)
            R = math.dist(G, tip)
            fig.fx_back.append(trail(fig, G, R, a0, a1, 16 * e, op=e))
        # l'éclair de l'impact (un éclat clair qui part de l'endroit du choc)
        fl = env(t, SP_HIT - 10, SP_HIT, SP_HIT + 20, SP_HIT + 120)
        if fl > 0:
            c = (CRASH_X, GR - 20)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(120), g_rad(
                fig, c, 120, [(0, '#ffffff', 0.85 * fl), (0.15, WATER[1], 0.5 * fl), (0.5, WATER[2], 0.15 * fl), (1, WATER[3], 0)])))
        # l'écrasement : la vague s'aplatit et roule en déferlante basse ; deux grandes nappes s'ouvrent en coupe
        if SP_HIT <= t < 1900:
            tg = (t - SP_HIT) / 1000.0
            k = smooth(tg / 0.5)
            h = 66 * (1 - k) + 12 * k
            if tg < 0.9:
                h2 = h * (1 - smooth((tg - 0.4) / 0.5)) if tg > 0.4 else h
                fig.fx_back.append(wave(fig, CRASH_X - 50 + 30 * smooth(tg / 0.9), max(0, h2), 90 + 20 * k, 68 - 50 * k, 7 - 3 * k,
                                        op=1 - smooth((tg - 0.6) / 0.3)))
            px = CRASH_X
            se = env(tg, 0, 0.06, 0.25, 0.6)
            if se > 0:
                grow = smooth(tg / 0.25)
                fig.fx_front.append(sheet(fig, (px - 4, GR - 3), -102, 34 + 26 * grow, -26, 15 * se, op=1, tail=0.15 * smooth((tg - 0.25) / 0.35)))
                fig.fx_front.append(sheet(fig, (px + 6, GR - 3), -74, 38 + 30 * grow, 26, 16 * se, op=1, tail=0.15 * smooth((tg - 0.25) / 0.35)))
                fig.fx_back.append(sheet(fig, (px - 12, GR - 2), -134, 18 + 12 * grow, -24, 9 * se, op=1))
                fig.fx_back.append(sheet(fig, (px + 14, GR - 2), -44, 20 + 14 * grow, 24, 9 * se, op=1))
            fe = env(tg, 0, 0.05, 0.4, 0.75)
            if fe > 0:
                fig.fx_front.append(foam(fig, px + 2, GR - 9, 9 * fe, op=1, seed=5))
                fig.fx_front.append(foam(fig, px - 24 - 10 * tg, GR - 4, 5 * fe, op=1, seed=6))
                fig.fx_front.append(foam(fig, px + 28 + 10 * tg, GR - 4, 5.4 * fe, op=1, seed=7))
            for j, (vx, vy, rr) in enumerate(((-70, -170, 1.6), (60, -190, 1.8), (-110, -90, 1.2), (115, -110, 1.3), (-25, -230, 1.1),
                                              (30, -210, 1.4), (-140, -40, 1.0), (150, -50, 1.1), (5, -150, 0.9), (85, -150, 1.0))):
                tau = tg - 0.02 * (j % 3)
                if 0 <= tau < 0.85:
                    x, y = ballistic((px, GR - 10), (vx, vy), 300, tau)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 300 * tau, rr, op=min(1, (0.85 - tau) * 4)))
            # elle se retire : des volutes d'écume qui se défont, une flaque qui s'efface
            re = env(tg, 0.35, 0.5, 0.6, 0.74)
            if re > 0:
                for j, (dx, rr) in enumerate(((-34, 3.4), (-12, 4.2), (16, 3.8), (40, 3.0))):
                    fig.fx_front.append(foam(fig, px + dx + 6 * (tg - 0.35), GR - 2.5, rr * re, op=re, seed=j))
                fig.fx_back.append(outlined([(ribbon([(px - 50, GR + 0.3), (px, GR - 1.0), (px + 50, GR + 0.3)], [0.3, 2.4, 0.3]),
                                              g_lin(fig, (px, GR - 2), (px, GR), [(0, WATER[2]), (1, WATER[4])]), 1)], op=re))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre, une ombre douce sous lui."""
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
    cx = (64 - 4 - x0) * k
    sd.ellipse([cx - 42 * k, fy - 3.0 * k, cx + 42 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * k))
    im.alpha_composite(sh)
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
        Pp = pose_at(T - 0.06, act, t0)
        tl = (T - t0) * 1000
        if act == 'attack':
            if 'c' not in HIT:
                Ph = pose_at(t0 + ATTACK_HIT / 1000.0, act, t0)
                HIT['c'] = K.build(pose=Ph).ctx['tip']
            fx = [fx_attack(tl, Pp['ang'])]
        else:
            fx = [fx_special(tl, Pp['ang'])]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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
            [1.0, a_s + 0.11, a_s + 0.40, a_s + 0.53, a_s + 0.60, a_s + 0.75, a_s + 0.9, a_s + 1.0,
             s_s + 0.3, s_s + 0.6, s_s + 0.86, s_s + 0.95, s_s + 1.2, s_s + 1.3, s_s + 1.45, s_s + 1.65]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.path.join(TMP, 'planche.png')
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
