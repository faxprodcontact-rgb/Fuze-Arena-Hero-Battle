# Le crabe géant vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/crabe-geant/
# build.py) — respiration lourde, attaque de base « Pince-massue », attaque spéciale « Lame de fond » — dans le style
# lisse de l'interface, à 24 images par seconde.
#
#   python3 refonte-graphique/ui-moderne/monstres/crabe-geant/anim.py            # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/crabe-geant/)
#   python3 refonte-graphique/ui-moderne/monstres/crabe-geant/anim.py --planche [instants en s]   # une planche de contrôle
#
# Méthode (celle de Kael et de Nyrra) : le dessin (crabe.py) est fait de morceaux ; chaque image le redessine dans une
# POSE. Un vrai crabe, pas un humain : le corps est porté par six pattes dont les pointes restent PLANTÉES ; quand il
# avance, il fait de petits pas de côté, une patte sur deux (trois en l'air, trois au sol) ; les pinces tournent autour
# de leur épaule et se plient au poignet ; le doigt mobile s'ouvre et se ferme autour de son articulation ; les yeux
# rentrent dans leurs logettes avant le coup ; les algues pendent et se balancent avec retard. C'est un tank : longues
# préparations tenues, coups très courts, impacts tenus (le sol tremble), retours lents. Les poses clés reprennent celles
# du pixel art (mêmes gestes, même rythme) et sont reliées par des courbes douces sans dépassement. Les effets (eau,
# écume, vague, poussière) : dégradés, un seul contour, aucun flou SVG ; aucune gerbe de rayons droits.
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crabe as C  # noqa: E402
from crabe import mapp  # noqa: E402
from atelier import sm, ribbon, ellipse  # noqa: E402
from eau import (WATER, WINK, outlined, drop, foam, sheet, stream, mound, env, ballistic, splash_crown,  # noqa: E402
                 g_lin, g_rad)

ROOT = C.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'crabe-geant')
TMP = os.environ.get('CRABE_TMP') or tempfile.mkdtemp(prefix='crabe-anim-')
FPS = 24
VIEW = (-6.0, -20.0, 276.0, 155.25)     # la scène de la vidéo, en pixels du dessin (16/9), même échelle que les héros
VW, VH = 1280, 720
GR = C.GRD
HIT = (176.0, 93.0)                      # l'ennemi (le milieu de son corps), où la pince frappe
ENEMY_X = 214.0                          # la première ligne ennemie (où la vague déferle)
DUST = ['#f2e0b6', '#c8a070', '#8e664a']
SINK = '#4a3656'
K = 1.15                                 # le rythme du pixel art, un peu étiré (plus fluide)

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


NUM = ['spx', 'spy', 'rot', 'ca', 'cw', 'co', 'sa', 'sw', 'so', 'ex', 'ey', 'er', 'sAx', 'sAl', 'sBx', 'sBl']
BASE = dict(co=1.0, so=1.0)
MOMENT = ('sAl', 'sBl')                  # les pattes levées : seulement à la clé où on les lève


def flat(keys):
    """Les clés écrites en « ce qui change » : chaque clé reprend la précédente (sauf les pattes levées) ;
    None = retour au repos."""
    out, cur = [], dict(BASE)
    for ms, d in keys:
        if d is None:
            cur = dict(BASE)
        else:
            cur = {k: v for k, v in cur.items() if k not in MOMENT}
            cur.update(d)
        out.append((ms, {n: cur.get(n, BASE.get(n, 0.0)) for n in NUM}))
    return out


def keyed(keys, t):
    ts = [k[0] * K for k in keys]
    return {n: monotone(ts, [k[1][n] for k in keys], t) for n in NUM}


# ======================================================================== les actions (poses clés, temps du pixel art)
# 2) « Pince-massue » : il se cabre (le corps recule et se tasse, les yeux rentrent dans leurs logettes, la grosse pince
# part en arrière grande ouverte : anticipation tenue) ; il charge en deux petits pas de côté (une patte sur deux) en
# abattant la pince, qui se referme en tournant vers l'avant (une traînée d'eau suit son bout) et ÉCRASE l'ennemi à
# hauteur du ventre (arrêt sur image : éclat d'écume, nappes d'eau, gouttes ; le sol tremble : poussière sous ses
# pattes) ; il reste appuyé, relève la pince et revient à sa place à petits pas lourds.
ATTACK = flat([
    (0, None),
    (100, dict(spx=-1.5, spy=0.8, ca=-10, cw=-4, co=1.25, er=0.5, sa=-6, ex=-0.4)),
    (220, dict(spx=-3.0, spy=1.8, rot=-2.0, ca=-26, cw=-10, co=1.65, er=1.0, sa=-12, so=1.4, ex=-0.8)),
    (470, dict(spx=-3.4, spy=2.0, rot=-2.5, ca=-30, cw=-12, co=1.7)),
    (535, dict(spx=6.0, spy=0.4, rot=0.5, ca=18, cw=2, co=1.0, sa=-4, sAx=9.0, sAl=3.4, ex=-1.2)),
    (600, dict(spx=20.0, spy=1.8, rot=3.0, ca=64, cw=12, co=0.0, sa=6, so=0.6, sAx=20.0, sBx=5.0, sBl=2.6, er=0.8,
               ex=0.6)),
    (700, dict(spx=20.6, spy=2.1, rot=3.3, ca=66, cw=13, sBx=20.0, er=0.6, ex=0.0)),
    (800, dict(spx=20.0, spy=1.6, rot=2.6, ca=63, cw=12, co=0.1, er=0.3)),
    (900, dict(spx=15.0, spy=0.6, rot=0.0, ca=22, cw=0, co=0.7, sa=0, so=1.0, sBx=12.0, sBl=3.0, er=0.1, ex=-0.6)),
    (1000, dict(spx=9.0, spy=0.4, ca=4, co=0.95, sAx=12.0, sAl=3.0, sBx=8.0, er=0.0, ex=-0.3)),
    (1100, dict(spx=3.0, ca=-2, sAx=4.0, sAl=1.6, sBx=4.0, sBl=2.0)),
    (1210, dict(spx=0.3, spy=0.8, ca=0, sAx=0.0, sBx=0.0, ex=0.0)),
    (1360, None),
])
AT_SWING, AT_HIT, AT_END = 470 * K, 600 * K, 1360 * K

# 3) « Lame de fond » : il se dresse sur la pointe des pattes, les deux pinces levées (la menace d'un vrai crabe), il
# bave des bulles ; l'eau monte du sol et s'enroule autour de la grosse pince (tenu : le danger monte). Il l'abat de tout
# son poids dans le sol devant lui (arrêt sur image, éclair, le sol tremble) : une VAGUE jaillit du sol au point
# d'impact, grossit en roulant vers la droite, sa crête d'écume s'enroule, et elle DÉFERLE sur toute la première ligne
# ennemie (arrêt sur image) ; puis elle retombe en écume et en flaques. Il relève la pince et revient en garde.
SPECIAL = flat([
    (0, None),
    (100, dict(spy=-1.2, ca=-6, co=1.2, sa=-18, so=1.2)),
    (220, dict(spy=-4.0, rot=-3.0, ca=-12, cw=-6, co=1.55, sa=-34, sw=-10, so=1.5)),
    (370, dict(spy=-4.4, rot=-3.4, ca=-14, cw=-8, co=1.6, sa=-36, sw=-12, so=1.6)),
    (520, dict(spy=-4.2, rot=-3.0, ca=-12, co=1.5, sa=-35, so=1.4)),
    (700, dict(spy=-4.8, rot=-4.5, ca=-30, cw=-14, co=1.8, sa=-38, so=1.6)),
    (760, dict(spy=-4.8, rot=-4.5, ca=-32, cw=-14, co=1.8)),
    (795, dict(spx=4.0, spy=-1.0, rot=0.0, ca=30, cw=4, co=1.0, sAx=4.0, sAl=2.6)),
    (830, dict(spx=8.0, spy=2.0, rot=5.0, ca=81, cw=12, co=0.15, sa=-8, sw=0, so=0.8, sAx=8.0, sBx=3.0, sBl=2.2)),
    (1010, dict(spx=8.4, spy=2.2, rot=5.2, ca=82, co=0.1, sa=-4, sBx=8.0)),
    (1290, dict(spx=8.0, spy=1.6, rot=4.6, ca=80, cw=12, co=0.2)),
    (1490, dict(spx=6.0, spy=0.6, rot=1.5, ca=40, cw=6, co=0.6, sa=0, so=1.0, sBx=4.0, sBl=2.6)),
    (1690, dict(spx=2.0, spy=0.2, rot=0.0, ca=4, cw=0, co=0.95, sAx=2.0, sAl=2.6, sBx=2.0)),
    (1930, dict(spx=0.2, spy=0.6, ca=0, sAx=0.0, sBx=0.0)),
    (2080, None),
])
SP_COIL0, SP_WIND, SP_SLAM = 200 * K, 760 * K, 830 * K
SP_ROLL, SP_CRASH, SP_FALL, SP_END = 1010 * K, 1290 * K, 1490 * K, 1930 * K

# ======================================================================== la respiration (en boucle)
BREATH_T = 2.0


def breath_at(T):
    return 0.5 - 0.5 * math.cos(2 * math.pi * T / BREATH_T)


def idle_offsets(T):
    """Il respire lourdement : la carapace et les pinces se soulèvent (les pointes restent plantées) puis retombent ;
    les pinces suivent avec retard, la grosse pince s'entrouvre à l'inspiration ; la petite pince pince deux fois ; les
    yeux suivent avec retard ; les algues se balancent."""
    br = breath_at(T)
    lag = breath_at(T - 0.18)
    lag2 = breath_at(T - 0.3)
    u = 2 * math.pi * T / BREATH_T
    pinch = max(0.0, math.sin(2 * math.pi * T / 1.0)) ** 3
    return dict(breath=br, cl=(0.0, 1.6 * (br - lag)), sl=(0.0, 1.6 * (br - lag2)), co=0.16 * lag, so=-0.55 * pinch,
                ey=1.6 * (br - lag2), alg=4.0 * math.sin(u - 1.3), alg2=5.0 * math.sin(u - 1.9))


def pose_at(T, action=None, t0=0.0):
    """La pose au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0] * K
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    Q = act or {n: BASE.get(n, 0.0) for n in NUM}
    # les algues : un pendule simple qui suit le mouvement du corps (elles traînent derrière)
    P = dict(breath=w * idl['breath'], sp=(Q['spx'], Q['spy']), rot=Q['rot'],
             ca=Q['ca'], cw=Q['cw'], co=max(0.0, Q['co'] + w * idl['co']),
             sa=Q['sa'], sw=Q['sw'], so=max(0.0, Q['so'] + w * idl['so']),
             eyes=(Q['ex'], Q['ey'] + w * idl['ey']), er=max(0.0, min(1.0, Q['er'])),
             cl=(0.0, w * idl['cl'][1]), sl=(0.0, w * idl['sl'][1]),
             steps={k: ((Q['sAx'], max(0.0, Q['sAl'])) if C.GROUP[k] == 'A' else (Q['sBx'], max(0.0, Q['sBl'])))
                    for k in C.LEGS},
             alg=idl['alg'], alg2=idl['alg2'])
    P['blink'] = 1.0 if (w > 0.95 and 2.6 <= (T % 3.6) < 2.72) else 0.0
    return P, tl


def algae_track(segs, n):
    """Les algues traînent derrière quand le corps bouge (vitesse du corps → balancement), en plus de la respiration."""
    out, th, om, prev = [], 0.0, 0.0, None
    for i in range(n):
        T = i / FPS
        a, s = which(segs, T)
        P, _ = pose_at(T, a, s)
        x = P['sp'][0]
        if prev is None:
            prev = x
        v = (x - prev) * FPS
        for _ in range(8):
            al = -0.9 * v * 1.4 - 60.0 * th - 7.0 * om
            om += al / FPS / 8
            th += om / FPS / 8
        out.append(max(-28.0, min(28.0, th)))
        prev = x
    return out


# ======================================================================== outils des effets


def dust(fig, cx, k, r=3.0, op=1.0, seed=0):
    """Le sol tremble : une petite bouffée de poussière ocre posée au sol (k : 0 → 1 elle naît, s'ouvre et se défait)."""
    if k <= 0 or k >= 1 or op <= 0.02:
        return ''
    e = math.sin(math.pi * k)
    rr = r * (0.5 + 0.7 * k)
    balls = [(cx - rr * 0.7, GR - rr * 0.45, rr * 0.62), (cx + rr * 0.15, GR - rr * 0.7, rr * 0.78),
             (cx + rr * 0.9, GR - rr * 0.35, rr * 0.5)]
    if seed % 2:
        balls = [(2 * cx - x, y, r_) for x, y, r_ in balls]
    gr = g_lin(fig, (cx + rr, GR - rr * 1.4), (cx - rr, GR), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="1"/>' % (x, y, r_, SINK, SINK)
                  for x, y, r_ in balls)
    col = ''.join('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>' % (x, y, r_, gr) for x, y, r_ in balls)
    return '<g opacity="%.3f">%s%s</g>' % (min(1, e * 1.6) * op, sil, col)


def flash(fig, c, r, op):
    """L'éclair de l'impact : un rond de lumière (dégradé radial, sans rayons)."""
    if op <= 0.02:
        return ''
    return '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>' % (c[0], c[1], r, g_rad(fig, c, r, [
        (0, '#ffffff', 0.95 * op), (0.35, WATER[1], 0.7 * op), (0.7, WATER[2], 0.25 * op), (1, WATER[2], 0)]))


def bubble(fig, x, y, r, op=1.0):
    """Une bulle : un rond clair au contour bleu nuit, un éclat en haut à droite."""
    if r < 0.2 or op <= 0.02:
        return ''
    gr = g_rad(fig, (x + r * 0.3, y - r * 0.3), r * 1.3, [(0, '#ffffff', 0.5), (0.6, WATER[2], 0.35), (1, WATER[3], 0.6)])
    return ('<g opacity="%.3f"><circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
            '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="#ffffff" opacity="0.95"/></g>' % (
                op, x, y, r, gr, WINK, x + r * 0.38, y - r * 0.38, r * 0.3, r * 0.22))


def wave(fig, X, h, L, curl, op=1.0):
    """La vague qui roule vers la droite : un dos en pente douce, la crête d'écume, la lèvre qui s'enroule vers l'avant
    (curl 0 → 1), le creux sombre dans l'enroulement ; la lumière en haut à droite."""
    if h < 1 or op <= 0.02:
        return ''
    G = GR + 0.4
    c = max(0.0, min(1.0, curl))
    pts = [(X - L, G), (X - L * 0.62, G - h * 0.28), (X - L * 0.3, G - h * 0.72), (X - h * 0.22, G - h * 0.98),
           (X + h * 0.1 * (1 + c), G - h * 1.02), (X + h * (0.3 + 0.32 * c), G - h * (0.9 - 0.05 * c)),
           (X + h * (0.38 + 0.36 * c), G - h * (0.66 - 0.12 * c)), (X + h * (0.28 + 0.26 * c), G - h * (0.52 - 0.12 * c)),
           (X + h * (0.2 + 0.1 * c), G - h * 0.6), (X + h * 0.14, G - h * 0.42), (X + h * 0.32, G - h * 0.14),
           (X + h * 0.52, G)]
    sh = sm(pts, sharp=(0, 7, 11), t=0.9)
    gr = g_lin(fig, (X + h * 0.2, G - h), (X - L * 0.6, G), [(0, WATER[2]), (0.35, WATER[3]), (0.75, WATER[4]),
                                                            (1, WATER[5])])
    crest = sm([(X - L * 0.36, G - h * 0.66), (X - h * 0.25, G - h * 0.96), (X + h * 0.1 * (1 + c), G - h * 1.0),
                (X + h * (0.3 + 0.32 * c), G - h * (0.88 - 0.05 * c)), (X + h * (0.36 + 0.34 * c), G - h * (0.66 - 0.12 * c)),
                (X + h * (0.28 + 0.26 * c), G - h * (0.55 - 0.12 * c)), (X + h * (0.24 + 0.2 * c), G - h * 0.74),
                (X + h * 0.02, G - h * 0.84), (X - h * 0.4, G - h * 0.8)], sharp=(0,), t=0.9)
    tube = ellipse(X + h * 0.22, G - h * 0.5, h * 0.12, h * 0.16, -20)
    glint = ribbon([(X - L * 0.62, G - h * 0.22), (X - L * 0.45, G - h * 0.46), (X - L * 0.3, G - h * 0.62)],
                   [0.2, max(0.6, h * 0.05), 0.2])
    face = ribbon([(X + h * 0.18, G - h * 0.4), (X + h * 0.26, G - h * 0.2), (X + h * 0.42, G - h * 0.04)],
                  [0.2, max(0.6, h * 0.06), 0.2])
    return outlined([(sh, gr, 1), (tube, WATER[5], 0.55, 'n'), (crest, '#ffffff', 0.95, 'n'), (glint, WATER[1], 0.6, 'n'),
                     (face, WATER[1], 0.45, 'n')], w=1.5, op=op)


def puddle(fig, X, L, op=1.0):
    """Une flaque d'eau posée au sol, à plat, qui se résorbe."""
    if L < 0.8 or op <= 0.02:
        return ''
    sh = ellipse(X, GR + 0.3, L, max(0.6, L * 0.12))
    gr = g_lin(fig, (X + L, GR - 1), (X - L, GR + 1), [(0, WATER[1]), (0.5, WATER[2]), (1, WATER[3])])
    hi = ellipse(X + L * 0.35, GR, L * 0.3, max(0.25, L * 0.04))
    return outlined([(sh, gr, 1), (hi, '#ffffff', 0.8, 'n')], w=1.0, op=op)


# ======================================================================== les effets des actions
TRAIL = []


def tip_at(keys, t):
    """Où est le bout de la grosse pince à l'instant t (ms) de l'action (pour dessiner l'arc de sa traînée)."""
    Q = keyed(keys, t)
    P = dict(C.REST, sp=(Q['spx'], Q['spy']), rot=Q['rot'], ca=Q['ca'], cw=Q['cw'], co=Q['co'])
    return mapp(C.skeleton(P)[2], (113.4, 19.0))


def arc_trail(fig, keys, tl, t0, t1, w, op):
    """La traînée d'eau qui suit le bout de la pince : l'arc réellement parcouru pendant les 90 dernières ms."""
    if op <= 0.02:
        return
    a = max(t0, tl - 95)
    b = min(tl, t1)
    if b - a < 12:
        return
    pts = [tip_at(keys, a + (b - a) * i / 8) for i in range(9)]
    fig.fx_back.append(stream(fig, pts, 1.4, w, op=op))


def fx_idle_bubble(T):
    """Il bave : une bulle naît à la bouche, monte en ondulant et éclate (toutes les 3,6 s)."""
    def f(fig, ctx):
        ph = (T % 3.6) / 1.6
        if ph >= 1:
            return
        m = ctx['mouth']
        x = m[0] + 1.6 + 1.2 * ph + 0.6 * math.sin(ph * 9)
        y = m[1] - 1.0 - 13 * ph
        r = 0.6 + 0.9 * min(1, ph * 3)
        if ph > 0.92:
            fig.fx_front.append(foam(fig, x, y, 0.9 * (1 - (ph - 0.92) / 0.08) + 0.2, op=0.8))
        else:
            fig.fx_front.append(bubble(fig, x, y, r))
    return f


def fx_attack(tl):
    def f(fig, ctx):
        tip = ctx['tip']
        # la traînée d'eau qui suit le bout de la pince pendant qu'elle s'abat
        if AT_SWING + 20 < tl < AT_HIT + 120:
            k = 1 - max(0.0, (tl - AT_HIT) / 120)
            arc_trail(fig, ATTACK, tl, AT_SWING + 20, AT_HIT, 3.8 * k, min(1, k * 1.5))
        # l'impact : éclair, écume, nappes d'eau qui s'ouvrent autour du point frappé, gouttes ; poussière sous les pattes
        dt = tl - AT_HIT
        if 0 <= dt < 520:
            k = dt / 520
            hp = (HIT[0] + 2, HIT[1] + 1)
            fig.fx_front.append(flash(fig, hp, 16 * (0.6 + 0.6 * k), 1 - k))
            for j, (ang, L, bd, w) in enumerate(((-118, 17, -34, 4.2), (-48, 22, 30, 4.8), (18, 13, 36, 3.4))):
                L_ = L * (0.35 + 0.65 * min(1, k * 3)) * (1 - 0.3 * max(0, k - 0.5) * 2)
                fig.fx_front.append(sheet(fig, hp, ang, L_, bd, w, op=min(1, (1 - k) * 2), tail=max(0, k - 0.4) * 1.3))
            for j, (vx, vy) in enumerate(((60, -110), (95, -70), (30, -140), (120, -30), (-30, -120), (80, -150))):
                tau = k * 0.55 - 0.02 * (j % 3)
                if tau > 0:
                    x, y = ballistic(hp, (vx, vy), 330, tau)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 330 * tau, 1.1 if j % 2 else 0.85, op=min(1, (1 - k) * 2.5)))
            for j in range(3):
                fig.fx_front.append(foam(fig, hp[0] - 3 + 4 * j, hp[1] - 2 + 2.5 * (j % 2), 2.4 * math.sin(math.pi * min(1, k * 1.4)) + 0.2,
                                         op=1 - k, seed=j))
        if -20 <= dt < 520:
            k = (dt + 20) / 540
            for i, leg in enumerate(C.LEGS):
                fig.fx_front.append(dust(fig, ctx['J'][leg][-1][0], k - 0.06 * (i % 3), 2.6, seed=i))
    return f


def coil(fig, ctx, grow, t, op=1.0):
    """L'eau qui monte du sol et s'enroule autour de la grosse pince : une spirale (ce qui passe derrière la pince va
    derrière le dessin, ce qui passe devant va devant), une bosse d'eau au sol à son pied."""
    CL = ctx['CLAW']
    base_c = mapp(CL, (106.0, 66.0))
    top_c = mapp(CL, (112.0, 26.0))
    foot = (base_c[0] + 6.0, GR)
    pts = []
    n = 60
    for i in range(n + 1):
        s = i / n
        if s > grow:
            break
        if s < 0.3:
            c = (foot[0] + (base_c[0] - foot[0]) * s / 0.3, foot[1] + (base_c[1] - foot[1]) * s / 0.3)
            R = 4.0 + 6.0 * s / 0.3
        else:
            u = (s - 0.3) / 0.7
            c = (base_c[0] + (top_c[0] - base_c[0]) * u, base_c[1] + (top_c[1] - base_c[1]) * u)
            R = 15.0 - 3.0 * u
        a = 2 * math.pi * 2.3 * s - t * 7.0
        pts.append((c[0] + R * math.sin(a), c[1] + R * 0.28 * math.cos(a), math.cos(a)))
    if len(pts) < 3:
        return
    # en morceaux continus devant / derrière
    runs, cur, side = [], [pts[0]], pts[0][2] > 0
    for p in pts[1:]:
        sd = p[2] > 0
        if sd != side:
            cur.append(p)
            runs.append((side, cur))
            cur, side = [p], sd
        else:
            cur.append(p)
    runs.append((side, cur))
    for front, r in runs:
        if len(r) < 3:
            continue
        line = [(x, y) for x, y, _ in r]
        w0 = 2.0 + 2.2 * (1 - pts.index(r[0]) / n)
        svg = stream(fig, line, w0, w0 * 0.8, op=op)
        (fig.fx_front if front else fig.fx_back).append(svg)
    fig.fx_back.append(mound(fig, foot[0], 5.0 * op * min(1, grow * 3), 12, op=op))


def fx_special(tl):
    def f(fig, ctx):
        # les bulles qu'il bave quand il se dresse
        if 100 * K < tl < SP_WIND:
            m = ctx['mouth']
            for j in range(3):
                ph = ((tl - 100 * K) / 420 + j / 3) % 1
                fig.fx_front.append(bubble(fig, m[0] + 1.4 + 1.6 * ph + 0.5 * math.sin(ph * 8 + j), m[1] - 1 - 14 * ph,
                                           0.5 + 0.8 * ph, op=1 - ph ** 3))
        # l'eau s'enroule autour de la grosse pince (monte, tient), puis s'abat avec elle
        if SP_COIL0 < tl < SP_SLAM + 40:
            grow = min(1.0, (tl - SP_COIL0) / 420)
            op = 1.0 if tl < SP_SLAM - 20 else max(0.0, 1 - (tl - (SP_SLAM - 20)) / 60)
            coil(fig, ctx, grow, tl / 1000, op)
        if SP_WIND < tl < SP_SLAM + 80:
            k = 1 - max(0.0, (tl - SP_SLAM) / 80)
            arc_trail(fig, SPECIAL, tl, SP_WIND, SP_SLAM, 4.4 * k, k)
        dt = tl - SP_SLAM
        imp = (ctx['tip'][0] + 2, GR - 1)
        if 0 <= dt < 420:
            k = dt / 420
            fig.fx_front.append(flash(fig, (imp[0], GR - 4), 20 * (0.5 + 0.7 * k), 1 - k))
            e = math.sin(math.pi * min(1.0, k * 1.2))
            fig.fx_front.append(mound(fig, imp[0], 6 * e, 13, op=min(1, e * 1.5)))
            for j, (vx, vy) in enumerate(((-50, -120), (40, -140), (95, -90), (-85, -70), (10, -165))):
                x, y = ballistic((imp[0], GR - 3), (vx, vy), 330, k * 0.6)
                if y < GR:
                    fig.fx_front.append(drop(fig, x, y, vx, vy + 330 * k * 0.6, 1.1 if j % 2 else 0.85, op=min(1, (1 - k) * 3)))
            for j in range(3):
                fig.fx_front.append(foam(fig, imp[0] - 6 + 6 * j, GR - 1.5, 2.2 * e + 0.2, op=min(1, e * 1.5), seed=j))
        if -20 <= dt < 600:
            k = (dt + 20) / 620
            for i, leg in enumerate(C.LEGS):
                fig.fx_front.append(dust(fig, ctx['J'][leg][-1][0], k - 0.05 * (i % 3), 3.0, seed=i))
        # la vague : jaillit au point d'impact, grossit en roulant vers la droite, s'enroule, déferle sur la ligne
        x0 = imp[0] + 4
        if SP_SLAM + 60 < tl < SP_CRASH + 60:
            u = (tl - (SP_SLAM + 60)) / (SP_CRASH + 60 - (SP_SLAM + 60))
            ue = u * u * (3 - 2 * u)
            X = x0 + (ENEMY_X - 6 - x0) * ue
            h = 6 + 28 * min(1, u * 1.2)
            fig.fx_front.append(wave(fig, X, h, 16 + 30 * min(1, u * 1.3), u ** 1.5))
            for j in range(3):
                fig.fx_front.append(foam(fig, X - h * 0.5 - 4 * j, GR - 1.5, 1.4 + 0.4 * j, op=0.9, seed=j))
        if SP_CRASH - 20 <= tl < SP_FALL + 260:
            k = (tl - (SP_CRASH - 20)) / (SP_FALL + 280 - (SP_CRASH - 20))
            fig.fx_front.append(flash(fig, (ENEMY_X + 4, GR - 16), 26 * (0.5 + 0.6 * k), max(0, 1 - k * 2)))
            # la lèvre retombe en avant, la vague s'affaisse
            fig.fx_front.append(wave(fig, ENEMY_X - 6 + 12 * k, 34 * (1 - k) ** 0.8, 46 - 16 * k, 1.0, op=1 - k ** 2))
            # l'écume déferle sur la ligne ennemie : de grosses boules d'écume qui s'ouvrent puis se défont
            e = math.sin(math.pi * min(1.0, k * 1.1))
            for j, (dx, dy, r) in enumerate(((0, -6, 3.6), (8, -12, 3.0), (-6, -16, 2.6), (14, -4, 2.8), (4, -22, 2.2),
                                             (20, -14, 2.0), (-12, -4, 2.4))):
                fig.fx_front.append(foam(fig, ENEMY_X + dx + 6 * k, GR + dy * (0.4 + 0.8 * k), r * e + 0.2,
                                         op=min(1, e * 1.4), seed=j))
            for j, (vx, vy) in enumerate(((60, -150), (110, -110), (20, -180), (150, -60), (-20, -130), (85, -170))):
                x, y = ballistic((ENEMY_X + 2, GR - 22), (vx, vy), 330, k * 0.8)
                if y < GR:
                    fig.fx_front.append(drop(fig, x, y, vx, vy + 330 * k * 0.8, 1.2 if j % 2 else 0.9, op=min(1, (1 - k) * 3)))
        # les flaques qui restent, puis se résorbent
        if SP_CRASH + 100 < tl < SP_END + 200:
            k = (tl - (SP_CRASH + 100)) / (SP_END + 200 - (SP_CRASH + 100))
            for j, (dx, L) in enumerate(((-34, 6), (-14, 9), (6, 12), (24, 8))):
                fig.fx_back.append(puddle(fig, ENEMY_X + dx, L * (1 - k ** 2) * min(1, k * 6), op=1 - k ** 3))
    return f


# ======================================================================== la vidéo


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael, Nyrra et Kesha)."""
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
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * BREATH_T), ('attack', ATTACK[-1][0] * K / 1000), ('idle', 1.0),
           ('attack', ATTACK[-1][0] * K / 1000), ('idle', 1.2), ('special', SPECIAL[-1][0] * K / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def which(segs, T):
    for a, s, e in segs:
        if s <= T < e:
            return (a if a != 'idle' else None), s
    return None, 0.0


def shadow(fig, P):
    """L'ombre douce au sol sous lui (elle suit le corps)."""
    cx = 62 + P['sp'][0]
    fig.under.insert(0, (cx, GR + 0.6, 62, 3.4, '#0a0418', 0.55, [(0, '#0a0418', 0.55), (0.7, '#0a0418', 0.3),
                                                                  (1, '#0a0418', 0)]))


def frame_svg(T, segs, alg, view=VIEW, ow=0.95):
    act, t0 = which(segs, T)
    P, tl = pose_at(T, act, t0)
    P['alg'] += alg
    P['alg2'] += alg * 1.2
    fx = []
    if act == 'attack':
        fx = [fx_attack(tl)]
    elif act == 'special':
        fx = [fx_special(tl)]
    else:
        fx = [fx_idle_bubble(T)]
    fig = C.build(ow=ow, pose=P, fx=fx, frame=view)
    shadow(fig, P)
    return fig.svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(C.HEROS, 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def main():
    planche = '--planche' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    segs, total = timeline()
    n = int(round(total * FPS))
    ALG = algae_track(segs, n)
    if planche:
        a_s = [s for a, s, e in segs if a == 'attack'][0]
        s_s = [s for a, s, e in segs if a == 'special'][0]
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.25, a_s + 0.5, a_s + 0.62, a_s + 0.7, a_s + 0.9, a_s + 1.15, a_s + 1.4,
                            s_s + 0.28, s_s + 0.6, s_s + 0.88, s_s + 0.97, s_s + 1.05, s_s + 1.2, s_s + 1.35,
                            s_s + 1.5, s_s + 1.62, s_s + 1.8, s_s + 2.1, s_s + 2.3]
        fr = []
        for T in moments:
            i = min(n - 1, int(round(T * FPS)))
            # les effets qui retiennent leurs dernières positions (traînées) : rejouer les images d'avant
            TRAIL.clear()
            for j in range(max(0, i - 6), i):
                frame_svg(j / FPS, segs, ALG[j])
            fr.append(frame_svg(T, segs, ALG[i]))
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        sheet_.save(os.path.join(TMP, 'planche.png'))
        print('planche :', os.path.join(TMP, 'planche.png'))
        return
    print('images :', n, '(%.1f s)' % total)
    TRAIL.clear()
    fr = [frame_svg(i / FPS, segs, ALG[i]) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
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
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == '__main__':
    main()
