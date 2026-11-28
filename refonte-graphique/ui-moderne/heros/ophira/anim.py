# Ophira vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/meduse/build.py)
# — respiration (le corps de serpent ondule, les serpents de la chevelure vivent chacun à leur rythme), attaque de base
# « Croc de pierre », attaque spéciale « Regard pétrifiant » — dans le style lisse de l'interface, à 24 images par
# seconde.
#
#   python3 refonte-graphique/ui-moderne/heros/ophira/anim.py             # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/ophira/)
#   python3 refonte-graphique/ui-moderne/heros/ophira/anim.py --planche [t…]   # une planche d'instants (contrôle)
#
# Méthode (comme Kael, ../kael/anim.py) : le dessin (ophira.py) est fait de morceaux ; chaque image le redessine dans
# une POSE : la taille monte et descend avec le corps de serpent qui se dresse ou ondule, le buste se penche depuis la
# taille, la tête, chaque serpent (son cou va chercher un décalage, son début reste dans la coiffe), les deux bras par
# cinématique inverse depuis les poignets (le coude tourne autour de sa vraie jointure), les doigts plus ou moins
# crochus, la crosse de la queue qui se roule, une bosse qui court le long de la queue posée au sol. Les poses clés
# reprennent celles du pixel art (mêmes gestes, même rythme), reliées par des courbes douces sans dépassement.
# Effets de la terre et du regard dessinés dans le même style : dégradés, un seul contour, courbes ; aucun flou SVG.
import json
import math
import os
import random
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import ophira as O  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm, bez, resample, INK, limb  # noqa: E402

ROOT = O.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'ophira')
TMP = os.path.join(HERE, '_images')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-ophira'
FPS = 24
VIEW = (-26, -26, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = O.GRD
FOE = (202.0, GR)                    # le pied de l'ennemi (comme le pixel art : 142 pixels devant elle)

# tons des effets : pierre et poussière (terre), regard (le vert de ses yeux)
STONE = ['#f6e2c0', '#c8a07a', '#94705e', '#624650', '#3e2a3a']
DUST = ['#f8ecd8', '#dcc6a6', '#ac927a', '#705a5e']
GAZE = ['#ffffff', '#f4ffc8', '#b8ff58', '#5cd23c', '#1e8a46', '#0c4a3a']
GINK = '#0c2c2a'                     # le contour du regard et des éclats verts
SINK = '#3a2430'                     # le contour de la pierre


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


SN = O.SNAKES
BASE = dict(lean=0.0, rise=0.0, wave=0.0, coil=0.0, headx=0.0, heady=0.0, tilt=0.0,
            hfx=O.WRISTF0[0], hfy=O.WRISTF0[1], rotF=0.0, curlF=0.0, hnx=O.WRIST0[0], hny=O.WRIST0[1], rot=0.0, curl=0.0,
            glow=0.0, jaw=0.0)
for _k in SN:
    BASE['%sx' % _k] = 0.0
    BASE['%sy' % _k] = 0.0
    BASE['t%s' % _k] = 1.0
    BASE['g%s' % _k] = 0.55
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'handF':
            d['hfx'], d['hfy'] = v
        elif key == 'hand':
            d['hnx'], d['hny'] = v
        elif key == 'sn':
            for s_, (x, y) in v.items():
                d['%sx' % s_], d['%sy' % s_] = x, y
        elif key == 'tg':
            for s_, t_ in v.items():
                d['t%s' % s_] = t_
        elif key == 'gape':
            for s_, g_ in v.items():
                d['g%s' % s_] = g_
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


def every(v):
    return {k: v for k in SN}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Croc de pierre » (pixel : ATTAQUE). Elle se ramasse : le buste recule, le corps de serpent se
# bande, la griffe revient vers l'épaule, la poussière du sol monte se souder dans sa paume en un croc de pierre
# recourbé à pointe d'émeraude ; les serpents se dressent, langues rentrées, les yeux s'allument. Puis le corps se
# détend comme un fouet : le buste file en avant, le bras se tend, le croc part en tournoyant vers la droite, une
# traînée de poussière ondule derrière lui ; les serpents traînent puis dépassent le mouvement ; retour en garde.
REAR = {'S1': (1.4, -1.2), 'S2': (1.4, -1.4), 'S3': (1.4, -1.2), 'S4': (1.2, -0.4), 'S5': (-0.4, -1.6), 'S6': (-0.6, -1.4)}
LAG = {'S1': (-1.6, 1.0), 'S2': (-1.6, 0.6), 'S3': (-1.6, 0.4), 'S4': (-1.4, 0.4), 'S5': (-1.6, 1.0), 'S6': (-1.4, 1.2)}
OVER = {'S1': (0.9, -0.3), 'S2': (0.8, -0.5), 'S3': (0.9, -0.2), 'S4': (0.6, -0.4), 'S5': (0.8, -0.6), 'S6': (0.9, -0.3)}
ATTACK = [
    (0, {}),
    (110, dict(lean=-2, wave=-1.0, coil=0.5, handF=(97.0, 55.0), rotF=-6, curlF=0.3, sn={k: (v[0] * 0.6, 0) for k, v in REAR.items()})),
    (230, dict(lean=-4, rise=0.3, wave=-2.0, coil=1.0, head=(-0.6, 0.6), tilt=-3, handF=(95.8, 53.6), rotF=-12, curlF=0.7,
               sn=REAR, tg=every(0.0), gape=every(0.3), glow=1.2, jaw=0.3)),
    (520, dict(lean=-4.6, rise=0.4, wave=-2.3, coil=1.3, head=(-0.8, 0.5), tilt=-3.6, handF=(95.4, 53.4), rotF=-14, curlF=0.8,
               sn=REAR, tg=every(0.0), gape=every(0.3), glow=1.6, jaw=0.4)),
    # le fouet : le corps se détend, le croc part
    (580, dict(lean=2.4, wave=1.6, coil=0.2, head=(0.8, 0), tilt=2, handF=(105.6, 57.2), rotF=12, curlF=0.0,
               sn=LAG, tg=every(2.0), gape=every(0.9), glow=1.2, jaw=0.6)),
    (650, dict(lean=3.2, wave=2.0, coil=-0.8, head=(1.0, 0.2), tilt=2.6, handF=(106.4, 57.6), rotF=14, curlF=-0.1,
               sn=LAG, tg=every(2.0), gape=every(0.9), glow=0.8, jaw=0.5)),
    (740, dict(lean=3.0, wave=1.4, coil=-1.2, head=(0.8, 0.2), tilt=2, handF=(105.4, 57.2), rotF=10, curlF=0.05,
               tg=every(1.6), glow=0.4, jaw=0.3)),
    # retour en garde (les serpents dépassent le mouvement, puis reviennent)
    (880, dict(lean=1.6, wave=0.6, coil=-0.8, head=(0.3, 0), tilt=1, handF=(102.4, 56.6), rotF=4, sn=OVER, glow=0.2)),
    (1040, dict(lean=0.6, wave=-0.3, coil=-0.3, head=(0, -0.3), sn={k: (v[0] * 0.3, v[1] * 0.3) for k, v in OVER.items()})),
    (1240, {}),
]
FANG_FORM = (90, 500)        # le croc se forme dans la paume
FANG_THROW = 560             # il part

# 3) L'attaque spéciale « Regard pétrifiant » (pixel : SPECIALE). Elle se dresse de toute sa hauteur (le corps de
# serpent s'allonge), la crosse se roule, les six serpents se dressent en sifflant, ses yeux s'allument d'un blanc vert
# brûlant ; une lueur naît devant son visage (anticipation tenue). Elle penche la tête vers l'ennemi : le regard part,
# une onde verte qui ondule comme un serpent jusqu'à lui. L'ennemi se couvre de pierre (une croûte en plaques monte du
# sol, son front brille de vert) ; arrêt sur l'image quand il est statue, des veines vertes y courent ; la statue
# éclate, les morceaux volent et retombent, la poussière se défait. Elle se repose sur ses anneaux.
RISE = {'S1': (1.0, -1.6), 'S2': (1.2, -2.2), 'S3': (1.2, -2.0), 'S4': (1.0, -1.2), 'S5': (0.6, -1.8), 'S6': (0.4, -2.0)}
STRIKE = {'S1': (2.2, 0.0), 'S2': (1.6, -0.8), 'S3': (2.2, 0.2), 'S4': (1.4, 0.2), 'S5': (1.6, -0.8), 'S6': (1.8, 0.2)}
SPECIAL = [
    (0, {}),
    (120, dict(rise=1.0, lean=-1, wave=-0.8, coil=1.0, head=(0, 0.6), sn={k: (v[0] * 0.5, v[1] * 0.5) for k, v in RISE.items()},
               tg=every(1.4), gape=every(0.8), glow=0.5)),
    (300, dict(rise=2.6, lean=-1.2, wave=-1.3, coil=2.2, head=(0, 0.2), tilt=-2, sn=RISE, tg=every(2.0), gape=every(1.0),
               glow=2.0, jaw=0.4, curlF=0.5, curl=0.5)),
    (560, dict(rise=2.9, lean=-1.3, wave=-1.4, coil=2.5, head=(-0.2, 0.0), tilt=-2.6, sn=RISE, tg=every(2.0), gape=every(1.0),
               glow=3.0, jaw=0.5, curlF=0.6, curl=0.6)),
    # le regard part
    (630, dict(rise=2.4, lean=1.4, wave=0.8, coil=1.8, head=(1.4, 0.4), tilt=4, sn=STRIKE, tg=every(2.0), gape=every(1.0),
               glow=3.0, jaw=0.6, curlF=0.3, curl=0.4, handF=(102.4, 56.2))),
    (720, dict(rise=2.4, lean=2.0, wave=1.2, coil=1.4, head=(1.6, 0.4), tilt=4.6, sn=STRIKE, tg=every(1.8), gape=every(0.9),
               glow=3.0, jaw=0.6, curlF=0.3, curl=0.4, handF=(102.6, 56.2))),
    (1240, dict(rise=2.3, lean=2.0, wave=1.0, coil=1.2, head=(1.5, 0.4), tilt=4.2, sn=STRIKE, tg=every(1.2), gape=every(0.8),
                glow=2.2, jaw=0.4, curlF=0.3, curl=0.4, handF=(102.6, 56.2))),
    # la statue éclate ; elle se repose
    (1420, dict(rise=1.6, lean=1.0, wave=0.4, coil=0.4, head=(0.4, -0.4), tilt=1.0, sn={k: (v[0] * 0.4, v[1] * 0.4) for k, v in RISE.items()},
                glow=1.0, jaw=0.2)),
    (1700, dict(rise=0.6, lean=0, wave=-0.4, coil=-0.6, head=(0, 0.6), sn=OVER, glow=0.3)),
    (1960, dict(rise=0.0, wave=-0.3, coil=-0.5, head=(0, 0.3), sn={k: (v[0] * 0.3, v[1] * 0.3) for k, v in OVER.items()})),
    (2260, {}),
]
SP_GAZE = (560, 760)         # l'onde du regard voyage (début, arrivée)
SP_STONE = (720, 1000)       # la croûte de pierre monte
SP_VEINS = (1060, 1250)      # les veines vertes
SP_BURST = 1260              # la statue éclate


# ======================================================================== la respiration (en boucle, 2 s)
# Le corps de serpent ondule (le milieu se bombe d'un côté puis de l'autre), le buste se balance avec un temps de
# retard, la crosse suit encore plus tard, une petite bosse court le long de la queue, de l'avant vers la pointe. Chaque
# serpent a son rythme (les deux du front vont deux fois plus vite, comme des gardes nerveux) et sort la langue à son
# tour. Un clignement toutes les 4 s.
RHYTHM = {'S1': (0.9, 0.8, 1, 0.0), 'S2': (0.7, 0.9, 1, 2.1), 'S3': (0.4, 0.9, 1, 4.0), 'S4': (0.7, 0.8, 1, 1.2),
          'S5': (0.5, 0.8, 2, 0.6), 'S6': (0.7, 0.7, 2, 2.4)}
FLICK = {'S1': (0.15, 0.7), 'S2': (0.45, 1.3), 'S3': (0.8, 0.3), 'S4': (1.15, 1.7), 'S5': (1.5, 0.95), 'S6': (1.8, 0.5)}


def pulse(t, t0, up=0.06, hold=0.14, down=0.1):
    """0 hors de l'éclair, 1 pendant : une langue qui sort et rentre."""
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


IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def tongues(T):
    """Les langues des six serpents, chacune à son tour (le cycle de 2 s d'avant, ramené sur IDLE_T)."""
    tt = (T % IDLE_T) * 2.0 / IDLE_T
    return {'t%s' % k: 1.2 * max(pulse(tt, t0), pulse(tt, t1, hold=0.1)) for k, (t0, t1) in FLICK.items()}


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : les six serpents de sa chevelure ondulent plus largement, chacun à son rythme (les deux du front deux
    fois plus vite), et sortent la langue à tour de rôle. Une pose partielle pour build() ; jouée au combat (pose_at :
    l'ondulation s'ajoute à la respiration, les langues y sont déjà) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    sn = {k: (SG_K * ax * math.cos(turns * u + ph), SG_K * ay * math.sin(turns * u + ph))
          for k, (ax, ay, turns, ph) in RHYTHM.items()}
    tg = tongues(T)
    return dict(sn=sn, tg={k: tg['t%s' % k] for k in RHYTHM})


SG_K = 3.0       # l'ondulation du signe : 3 fois celle de la respiration


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    d = dict(breath=0.5 - 0.5 * math.cos(u), wave=1.2 * math.sin(u), lean=0.7 * math.sin(u - 1.3),
             coil=0.55 * math.sin(u - 2.0), heady=0.3 * math.sin(u - 0.6), tilt=0.8 * math.sin(u - 0.9),
             hfy=0.4 * math.sin(u - 1.0), hfx=0.2 * math.sin(u - 1.4), rotF=2.0 * math.sin(u - 1.1),
             curlF=0.12 * math.sin(u + 0.4), hny=0.4 * math.sin(u - 0.7), rot=-2.0 * math.sin(u - 0.8),
             curl=0.12 * math.sin(u + 1.2))
    for k, (ax, ay, turns, ph) in RHYTHM.items():
        d['%sx' % k] = ax * math.cos(turns * u + ph)
        d['%sy' % k] = ay * math.sin(turns * u + ph)
    d.update(tongues(T))
    return d


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
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
    src = act or dict(BASE)
    Q = {}
    for n in NUM:
        if n.startswith('t') and n[1:] in SN:
            # la langue : celle de l'action, ou les éclairs de la respiration
            Q[n] = src[n] if act and w < 0.99 else 0.0
            Q[n] = (1 - w) * Q[n] + w * idl.get(n, 0.0)
        else:
            Q[n] = src[n] + w * idl.get(n, 0.0)
    P = dict(breath=w * idl['breath'], lean=Q['lean'], rise=Q['rise'], wave=Q['wave'], coil=Q['coil'],
             head=(Q['headx'], Q['heady']), tilt=Q['tilt'], handF=(Q['hfx'], Q['hfy']), rotF=Q['rotF'], curlF=Q['curlF'],
             hand=(Q['hnx'], Q['hny']), rot=Q['rot'], curl=Q['curl'], glow=Q['glow'], jaw=Q['jaw'],
             sn={k: (Q['%sx' % k], Q['%sy' % k]) for k in SN}, tg={k: Q['t%s' % k] for k in SN},
             gape={k: Q['g%s' % k] for k in SN})
    sg = signe(T)['sn']                       # le signe du repos : les serpents ondulent plus largement
    P['sn'] = {k: (P['sn'][k][0] + w * sg[k][0], P['sn'][k][1] + w * sg[k][1]) for k in SN}
    # la bosse qui court le long de la queue (seulement au repos)
    P['hump'] = ((T % IDLE_T) / IDLE_T * 1.3 - 0.15, 0.75 * w)
    P['ear'] = math.sin(2 * math.pi * T / IDLE_T - 2.0)
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % IDLE_T) < 1.40) else 0.0
    return P


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=SINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                     '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


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


def glow(fig, c, r, color, op):
    if op <= 0.01 or r <= 0.1:
        return ''
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)]))


def dust(fig, cx, cy, r, op=1.0, seed=0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    rnd = random.Random(seed)
    balls = [(cx, cy, r)]
    for i in range(3):
        a = rnd.uniform(0, 2 * math.pi)
        balls.append((cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.45 + 0.2 * r, r * rnd.uniform(0.55, 0.75)))
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DUST[3], DUST[3]) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    hi = '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.7"/>' % (fm(cx + r * 0.3), fm(cy - r * 0.35), fm(r * 0.38), DUST[0])
    return '<g opacity="%g">%s%s%s</g>' % (op, sil, col, hi)


def pebble(fig, x, y, s=1.0, rot=0.0, op=1.0, seed=0):
    """Un gravillon / un éclat de pierre (brun chaud, éclairé en haut à droite, un contour)."""
    rnd = random.Random(seed)
    n = 5 + seed % 2
    pts = []
    for i in range(n):
        a = rot + 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        rr = s * rnd.uniform(0.75, 1.15)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.85))
    sh = sm(pts, sharp=tuple(range(n)), t=0.45)
    face = sm([(x + s * 0.1, y - s * 0.75), (x + s * 0.95, y - s * 0.2), (x + s * 0.2, y + s * 0.1)], sharp=(0, 1, 2), t=0.5)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, STONE[1]), (0.55, STONE[2]), (1, STONE[3])])
    return outlined([(sh, gr, 1), (face, STONE[0], 0.55)], w=0.9, op=op)


# ---- l'attaque : le croc de pierre

def fang_shape(c, ang, k=1.0):
    """Le croc : une corne de pierre recourbée (base large taillée, pointe vers +x qui se recourbe vers le bas) ; rend
    (corne, pointe d'émeraude, arête claire)."""
    from outils import taper, crpath

    def P(u, v):
        a = math.radians(ang)
        return (c[0] + k * (u * math.cos(a) - v * math.sin(a)), c[1] + k * (u * math.sin(a) + v * math.cos(a)))
    spine = crpath([P(-3.6, 0.2), P(-0.6, -0.7), P(2.6, -0.6), P(4.8, 0.6), P(6.0, 2.6)], n=16)
    horn = taper(spine, 3.6 * k, 0.1, tip='sharp', wmid=2.6 * k)
    tip = taper(spine[10:], 1.9 * k, 0.1, tip='sharp')
    face = taper([(x + 0.25 * k, y - 0.55 * k) for x, y in spine[1:11]], 1.0 * k, 0.2, tip='sharp')
    return horn, tip, face


def draw_fang(fig, c, ang, k=1.0, op=1.0):
    horn, tip, face = fang_shape(c, ang, k)
    gr = g_lin(fig, (c[0] + 4 * k, c[1] - 3 * k), (c[0] - 4 * k, c[1] + 3 * k), [(0, STONE[0]), (0.45, STONE[1]), (1, STONE[2])])
    gt = g_lin(fig, (c[0] + 4 * k, c[1] - 1 * k), (c[0] + 6 * k, c[1] + 3 * k), [(0, O.EMER.light), (0.5, O.EMER.base), (1, O.EMER.shadow)])
    return outlined([(horn, gr, 1), (face, STONE[0], 0.7), (tip, gt, 1)], w=1.1, op=op)


def wavy_trail(fig, pts, w0, w1, amp, phase, op=1.0):
    """Une traînée de poussière qui serpente (une onde, jamais une ligne droite), effilée aux deux bouts."""
    if len(pts) < 3 or op <= 0.02:
        return ''
    n = len(pts) - 1
    out, ws = [], []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        u = i / n
        off = amp * math.sin(u * 9.0 + phase) * math.sin(math.pi * u)
        out.append((p[0] + nx * off, p[1] + ny * off))
        ws.append(max(0.1, (w0 + (w1 - w0) * u) * math.sin(math.pi * min(1, u * 1.1)) ** 0.6))
    rb = ribbon(out, ws)
    gr = g_lin(fig, out[0], out[-1], [(0, DUST[2], 0.2), (0.5, DUST[1], 0.8), (1, DUST[0], 1)])
    return '<g opacity="%g"><path d="%s" fill="%s" stroke="%s" stroke-width="0.6" stroke-opacity="0.5"/></g>' % (op, rb.d(), gr, DUST[3])


def fx_attack(tl):
    def f(fig, ctx):
        palm = ctx['palmF']
        back, front = [], []
        # 1) la poussière monte du sol en spirale et se soude dans la paume
        f0, f1 = FANG_FORM
        if f0 - 40 <= tl < FANG_THROW:
            for i in range(9):
                s0 = f0 - 40 + i * 32                 # chaque grain part à son tour
                u = (tl - s0) / 260.0
                if u <= 0 or u >= 1:
                    continue
                gx = 66 + 46 * math.sin(i * 2.3) + (8 if i % 2 else -6)
                start = (gx, GR - 1.0)
                e = ease(u)
                a = 6.0 * u + i
                x = start[0] + (palm[0] - start[0]) * e + 4.0 * (1 - e) * math.cos(a)
                y = start[1] + (palm[1] - start[1]) * e + 2.0 * (1 - e) * math.sin(a)
                s_ = 0.9 * (1 - 0.6 * e) + 0.3
                (front if i % 3 == 0 else back).append(pebble(fig, x, y, s_, rot=a, op=min(1, u * 5), seed=10 + i))
            # les petites bouffées soulevées au sol, au départ des grains
            for i, x in enumerate((44.0, 92.0, 108.0)):
                lv = env(tl, f0 - 40 + i * 50, f0 + 40 + i * 50, f0 + 120 + i * 50, f0 + 300 + i * 50)
                back.append(dust(fig, x, GR - 1.6, 1.6 + 1.2 * lv, op=lv, seed=30 + i))
        # 2) le croc grandit dans la paume (pointe d'émeraude), tenu, il tremble à peine
        if f0 + 80 <= tl < FANG_THROW:
            k = ease((tl - f0 - 80) / 260.0)
            jit = 0.25 * math.sin(tl * 0.09) if tl > f1 - 120 else 0.0
            front.append(glow(fig, (palm[0] + 1, palm[1] - 5), 6 + 3 * k, '#ffd88a', 0.3 * k))
            front.append(draw_fang(fig, (palm[0] + 0.2 + jit, palm[1] - 2.6), -34, k=0.45 + 0.75 * k))
        # 3) le croc part en tournoyant vers la droite et sort du cadre ; derrière lui, une traînée qui serpente
        if tl >= FANG_THROW:
            u = (tl - FANG_THROW) / 1000.0
            x0, y0 = palm[0] + 0.2, palm[1] - 2.6
            x = x0 + 300 * u
            y = y0 - 10 * u + 18 * u * u
            ang = -34 + 900 * u
            fade = 1 - ease((tl - FANG_THROW - 420) / 200.0)
            if x < VIEW[0] + VIEW[2] + 12:
                # la traînée : de la paume au croc, qui s'efface par la queue
                tail_u = max(0.0, u - 0.22)
                n = 16
                pts = []
                for i in range(n + 1):
                    uu = tail_u + (u - tail_u) * i / n
                    pts.append((x0 + 300 * uu, y0 - 10 * uu + 18 * uu * uu))
                back.append(wavy_trail(fig, pts, 0.3, 2.2, 1.6, tl * 0.02, op=fade))
                front.append(draw_fang(fig, (x, y), ang, k=1.2))
            # le souffle du lancer : un fuseau clair devant la paume
            sw = env(tl, FANG_THROW, FANG_THROW + 30, FANG_THROW + 60, FANG_THROW + 170)
            if sw > 0:
                a0 = palm
                pts = [(a0[0] + 2 + 26 * i / 10, a0[1] - 3 + 1.2 * math.sin(i * 0.8)) for i in range(11)]
                ws = [0.1] + [2.4 * sw * math.sin(math.pi * i / 10) for i in range(1, 10)] + [0.1]
                back.append('<path d="%s" fill="%s"/>' % (ribbon(pts, ws).d(), g_lin(fig, pts[0], pts[-1], [(0, DUST[0], 0.0), (0.4, DUST[0], 0.6 * sw), (1, DUST[1], 0)])))
            # la poussière arrachée sous la queue quand le corps se détend
            for i, (x_, s_) in enumerate(((100.0, 1.0), (14.0, 0.8), (60.0, 0.6))):
                lv = env(tl, FANG_THROW + i * 30, FANG_THROW + 80 + i * 30, FANG_THROW + 140 + i * 30, FANG_THROW + 460 + i * 30)
                if lv > 0:
                    rise_ = (tl - FANG_THROW - i * 30) / 460.0
                    back.append(dust(fig, x_ + 3 * rise_ * (1 if x_ > 60 else -1), GR - 1.8 - 3.5 * rise_, (2.0 + 1.6 * rise_) * s_ + 0.6, op=lv, seed=40 + i))
        fig.fx_back.append(''.join(back))
        fig.fx_front.append(''.join(front))
    return f


# ---- la spéciale : le regard, la statue, l'éclatement

# La statue : une silhouette de guerrier tournée vers elle (jambes écartées, buste, bras levé devant le visage, tête),
# en capsules : (u, h) = (x − FOE, hauteur au-dessus du sol), rayon.
STATUE = [((-7, 0), (-5, 25), 4.8), ((7, 0), (5, 25), 4.8), ((0, 24), (0, 31), 8.4), ((0, 31), (1, 43), 10.2),
          ((0, 44), (-1, 51), 4.0), ((-1, 57), (-1, 57), 7.2), ((-8, 44), (-16, 34), 3.8), ((-16, 34), (-14, 52), 3.4),
          ((9, 43), (13, 27), 3.8), ((13, 27), (14, 18), 3.4)]
STATUE_H = 65.0
_ST_CACHE = {}


def statue_geom():
    """La silhouette de la statue et ses plaques (cellules), en polygones shapely (calculés une fois)."""
    if 'g' in _ST_CACHE:
        return _ST_CACHE['g']
    from shapely.geometry import LineString, Point, MultiPoint, box
    from shapely.ops import unary_union, voronoi_diagram
    caps = []
    for (a, b, r) in STATUE:
        A = (FOE[0] + a[0], GR - a[1])
        B = (FOE[0] + b[0], GR - b[1])
        if A == B:
            caps.append(Point(A).buffer(r, 24))
        else:
            caps.append(LineString([A, B]).buffer(r, 24))
    sil = unary_union(caps).buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    sil = sil.intersection(box(FOE[0] - 40, GR - 80, FOE[0] + 40, GR))
    rnd = random.Random(9)
    seeds = MultiPoint([(FOE[0] + rnd.uniform(-20, 20), GR - rnd.uniform(0, 68)) for _ in range(30)])
    cells = []
    for c in voronoi_diagram(seeds, envelope=box(FOE[0] - 45, GR - 85, FOE[0] + 45, GR + 5)).geoms:
        g = c.intersection(sil)
        if not g.is_empty and g.area > 0.5:
            cells.append(g)
    _ST_CACHE['g'] = (sil, cells)
    return sil, cells


def front_line(level, x):
    return GR - level * (STATUE_H + 3) + 1.6 * math.sin(x * 0.9) + 1.1 * math.sin(x * 0.37 + 1.0)


def statue(fig, level, cracks=0.0, flash=0.0):
    """La croûte de pierre : level 0..1 (du sol vers le haut, front irrégulier bordé de lueur verte) ; plaques de roche
    éclairées en haut à droite, un seul contour ; cracks 0..2 : veines vertes qui courent dans la pierre."""
    from shapely.geometry import Polygon
    sil, cells = statue_geom()
    if level <= 0:
        return ''
    xs = [FOE[0] - 40 + i * 1.0 for i in range(81)]
    clipr = Polygon([(x, front_line(level, x)) for x in xs] + [(FOE[0] + 40, GR + 2), (FOE[0] - 40, GR + 2)])
    part = sil.intersection(clipr)
    if part.is_empty:
        return ''
    shp = O.shape_poly(part, step=0.6)
    out = ['<path d="%s" fill="%s" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % (shp.d(), SINK, SINK, )]
    cid = fig.uid('c')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, shp.d()))
    inner = []
    # le fond (les joints entre les plaques)
    inner.append('<path d="%s" fill="%s"/>' % (shp.d(), STONE[4]))
    cx0, cy0 = FOE[0], GR - 36
    for i, cell in enumerate(cells):
        g = cell.intersection(part).buffer(-0.28)
        if g.is_empty or g.area < 0.3:
            continue
        cs = O.shape_poly(g, step=0.8, t=0.6)
        c = g.centroid
        k = ((c.x - cx0) * 0.6 - (c.y - cy0) * 0.8) / 40.0 + ((i * 37) % 7 - 3) * 0.04
        base = STONE[1] if k > 0.18 else STONE[2] if k > -0.2 else STONE[3]
        light = STONE[0] if k > 0.18 else STONE[1] if k > -0.2 else STONE[2]
        x0_, y0_, x1_, y1_ = g.bounds
        gr = g_lin(fig, (x1_, y0_), (x0_, y1_), [(0, light), (0.6, base), (1, STONE[3])])
        inner.append('<path d="%s" fill="%s"/>' % (cs.d(), gr))
        # l'arête éclairée de la plaque (en haut à droite)
        inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.6"/>' % (cs.d(), cs.move(-0.35, 0.45).d(), STONE[0]))
    # l'ombre propre de la statue (bande en bas à gauche) et la lumière du bord
    inner.append('<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.55"/>' % (shp.d(), shp.move(1.3, -1.6).d(), STONE[4]))
    if flash > 0:
        inner.append('<path d="%s" fill="%s" opacity="%g"/>' % (shp.d(), GAZE[1], 0.7 * flash))
    # le front de pierre qui monte : un liseré de lueur verte
    if level < 1:
        band = part.difference(Polygon([(x, front_line(level, x) + 2.2) for x in xs] + [(FOE[0] + 40, GR + 2), (FOE[0] - 40, GR + 2)]))
        if not band.is_empty:
            bs = O.shape_poly(band, step=0.6)
            inner.append('<path d="%s" fill="%s"/>' % (bs.d(), GAZE[3]))
            band2 = part.difference(Polygon([(x, front_line(level, x) + 1.0) for x in xs] + [(FOE[0] + 40, GR + 2), (FOE[0] - 40, GR + 2)]))
            if not band2.is_empty:
                inner.append('<path d="%s" fill="%s"/>' % (O.shape_poly(band2, step=0.6).d(), GAZE[1]))
    # les veines vertes
    if cracks > 0:
        cy = GR - 38
        paths = [[(0, 0), (-3, -5), (-2, -11), (-4, -17)], [(0, 0), (5, -3), (7, -9)], [(0, 0), (-4, 6), (-5, 14), (-7, 22)],
                 [(0, 0), (3, 8), (6, 16), (6, 26)], [(-3, -5), (-9, -3), (-14, 2)], [(3, 8), (8, 9)]]
        if cracks >= 1:
            paths += [[(-2, -11), (1, -17), (-1, -22)], [(-5, 14), (1, 19)], [(7, -9), (11, -14)], [(-14, 2), (-15, 10)]]
        for j, pth in enumerate(paths):
            lv = max(0.0, min(1.0, cracks * 1.6 - j * 0.12))
            if lv <= 0:
                continue
            m = max(2, int(round(len(pth) * lv)))
            pts = [(FOE[0] + p[0], cy + p[1]) for p in pth[:m]]
            if len(pts) < 2:
                continue
            pts = resample(pts, 6)
            ws = [0.15] + [0.9 + 0.3 * min(cracks, 1.5)] * 5 + [0.15]
            inner.append('<path d="%s" fill="%s" opacity="0.6"/>' % (ribbon(pts, [w * 2.4 for w in ws]).d(), GAZE[3]))
            inner.append('<path d="%s" fill="%s"/>' % (ribbon(pts, ws).d(), GAZE[2]))
            inner.append('<path d="%s" fill="%s"/>' % (ribbon(pts, [w * 0.4 for w in ws]).d(), GAZE[0]))
    out.append('<g clip-path="url(#%s)">%s</g>' % (cid, ''.join(inner)))
    return ''.join(out)


def chunks(fig, t):
    """Les morceaux de la statue qui volent puis retombent (t en s depuis l'éclatement)."""
    sil, cells = statue_geom()
    out_b, out_f = [], []
    for i, cell in enumerate(cells):
        c = cell.centroid
        rnd = random.Random(100 + i)
        vx = (c.x - FOE[0]) * 1.6 + rnd.uniform(-14, 14)
        vy = -26 - rnd.uniform(0, 30) + (GR - c.y) * 0.2
        x = c.x + vx * t
        y = c.y + vy * t + 0.5 * 150 * t * t
        s = max(1.0, min(4.2, math.sqrt(cell.area) * 0.42))
        landed = y > GR - s * 0.6
        if landed:
            # posé au sol, il roule un peu puis s'arrête
            tl = (y - (GR - s * 0.6)) / 60.0
            y = GR - s * 0.55
            x = c.x + vx * min(t, 0.45) * 1.0
        rot = (rnd.uniform(-1, 1) * 6 * min(t, 0.5))
        op = 1.0 - ease((t - 0.75) / 0.35)
        if op <= 0.02:
            continue
        (out_f if i % 3 == 0 else out_b).append(pebble(fig, x, y, s, rot=rot, op=op, seed=i))
    return ''.join(out_b), ''.join(out_f)


def gaze_path(ctx):
    """Le chemin du regard : des yeux jusqu'à la poitrine de l'ennemi, une courbe en S."""
    e1, e2 = ctx['eyes']
    e = ((e1[0] + e2[0]) / 2 + 2.5, (e1[1] + e2[1]) / 2)
    t = (FOE[0] - 6.0, GR - 44.0)
    return bez(e, (e[0] + 40, e[1] - 24), (t[0] - 52, t[1] + 20), t, 60)


def gaze(fig, ctx, p, tail=0.0, amp=3.2, ph=0.0):
    """L'onde du regard : elle ondule comme un serpent ; p = où en est sa tête (0..1), tail = la part effacée."""
    path = resample(gaze_path(ctx), 80)
    n = len(path) - 1
    head = int(p * n)
    i0 = int(tail * n)
    if head - i0 < 2:
        return ''
    pts, ws = [], []
    for i in range(i0, head + 1):
        a = path[max(0, i - 1)]
        b = path[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        rel = (head - i) / max(head, 1)
        off = amp * math.sin(rel * 9.0 + ph) * min(1.0, rel * 4)
        pts.append((path[i][0] + nx * off, path[i][1] + ny * off))
        ws.append(0.5 + 3.4 * (1 - rel) ** 1.4)
    ws[0] = 0.1
    rb = ribbon(pts, ws)
    core = ribbon(pts, [w * 0.42 for w in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, GAZE[4]), (0.6, GAZE[3]), (1, GAZE[2])])
    out = outlined([(rb, gr, 1), (core, GAZE[1], 0.95)], ink=GINK, w=0.9)
    hx, hy = pts[-1]
    out += glow(fig, (hx, hy), 9, GAZE[2], 0.45)
    orb = ellipse(hx, hy, 2.8, 2.8)
    out += outlined([(orb, g_rad(fig, (hx + 0.6, hy - 0.6), 3.0, [(0, GAZE[0]), (0.5, GAZE[1]), (1, GAZE[2])]), 1)], ink=GINK, w=0.9)
    return out


def burst(fig, c, r, rot=0.0, op=1.0, tones=None):
    """L'éclat de l'impact : une étoile à quatre branches inégales, aux flancs courbes."""
    if r < 0.4 or op <= 0.02:
        return ''
    tones = tones or [GAZE[0], GAZE[1], GAZE[2], GAZE[3]]
    pts = []
    arms = (1.0, 0.55, 0.85, 0.5)
    for i in range(4):
        a = math.radians(rot + 90 * i)
        pts.append((c[0] + r * arms[i] * math.cos(a), c[1] + r * arms[i] * math.sin(a)))
        b = math.radians(rot + 90 * i + 45)
        pts.append((c[0] + r * 0.24 * math.cos(b), c[1] + r * 0.24 * math.sin(b)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.9)
    core = sh.scale(0.55, 0.55, c[0], c[1])
    gr = g_rad(fig, c, r, [(0, tones[0]), (0.35, tones[1]), (0.7, tones[2]), (1, tones[3])])
    return outlined([(sh, gr, 1), (core, '#ffffff', 0.9)], ink=GINK, w=1.0, op=op)


def fx_special(tl):
    def f(fig, ctx):
        back, front = [], []
        # 1) elle se dresse : la poussière s'arrache sous ses anneaux, quelques gravillons flottent
        lv = env(tl, 40, 200, 320, 620)
        if lv > 0:
            u = min(1.0, tl / 600)
            for i, (x, s_) in enumerate(((100.0, 1.0), (10.0, 0.9), (54.0, 0.7))):
                back.append(dust(fig, x + (4 if i == 0 else -3) * u, GR - 1.8 - 2.5 * u, (1.8 + 1.8 * u) * s_, op=lv, seed=50 + i))
            for i, (x, h0) in enumerate(((108.0, 5), (30.0, 8), (76.0, 3))):
                back.append(pebble(fig, x, GR - h0 - 9 * u - 2 * i, 0.7, rot=u * 3 + i, op=lv, seed=60 + i))
        # 2) ses yeux s'allument : une lueur verte devant le visage (anticipation tenue)
        e1, e2 = ctx['eyes']
        g = ctx['P']['glow']
        if g > 0.3:
            front.append(glow(fig, e1, 3.0 + 1.6 * g, GAZE[2], 0.16 * g))
            front.append(glow(fig, e2, 2.4 + 1.3 * g, GAZE[2], 0.16 * g))
        lv = env(tl, 300, 480, 560, 640)
        if lv > 0:
            c = (e2[0] + 7, e2[1] - 1)
            front.append(glow(fig, c, 9 * lv + 2, GAZE[2], 0.4 * lv))
            # une lueur courbe : un croissant vert qui naît devant le visage
            arc = [(c[0] - 2 + 3.2 * math.cos(a), c[1] + 6.0 * math.sin(a)) for a in [(-1.2 + 2.4 * i / 10) for i in range(11)]]
            front.append(E.ruban(fig, arc, 2.8 * lv, _REGARD, op=lv, kind='fuseau'))   # « pro » (28/11)
        # 3) le regard part et voyage jusqu'à l'ennemi
        g0, g1 = SP_GAZE
        if g0 <= tl < g1 + 260:
            p = min(1.0, (tl - g0) / (g1 - g0))
            tail = max(0.0, (tl - g1 + 40) / 300.0)
            if tail < 0.98:
                front.append(gaze(fig, ctx, ease(p) * 0.98 + 0.02, tail=min(0.97, tail), ph=tl * 0.03))
        # 4) l'impact (un éclat vert), la croûte de pierre monte, arrêt sur l'image, les veines, l'éclatement
        s0, s1 = SP_STONE
        v0, v1 = SP_VEINS
        if g1 - 30 <= tl < g1 + 220:
            k = env(tl, g1 - 30, g1, g1 + 60, g1 + 220)
            front.append(glow(fig, (FOE[0] - 5, GR - 44), 14 * k + 2, GAZE[2], 0.5 * k))
            front.append(burst(fig, (FOE[0] - 5, GR - 44), 8.5 * k, rot=20, op=k))
        if s0 <= tl < SP_BURST + 40:
            level = ease((tl - s0) / (s1 - s0))
            cr = 0.0 if tl < v0 else 2.0 * ease((tl - v0) / (v1 - v0))
            fl = env(tl, SP_BURST - 40, SP_BURST, SP_BURST, SP_BURST + 40)
            back.append(statue(fig, max(0.05, level), cracks=cr, flash=fl))
            if cr > 0:
                back.append(glow(fig, (FOE[0], GR - 38), 20, GAZE[2], 0.25 * min(1, cr)))
        if tl >= SP_BURST:
            t = (tl - SP_BURST) / 1000.0
            k = env(tl, SP_BURST, SP_BURST + 30, SP_BURST + 60, SP_BURST + 200)
            front.append(glow(fig, (FOE[0], GR - 38), 22 * k + 2, '#fff6d0', 0.6 * k))
            front.append(burst(fig, (FOE[0], GR - 38), 14 * k, rot=8, op=k, tones=['#ffffff', '#fff4c8', STONE[0], STONE[1]]))
            b_, f_ = chunks(fig, t)
            back.append(b_)
            front.append(f_)
            # la poussière enfle puis se défait en volutes
            for i, (dx, dy, r0) in enumerate(((-14, -4, 7), (15, -4, 6.4), (1, -2, 5.4), (-6, -26, 4.6), (10, -32, 4.0))):
                lv = env(tl, SP_BURST + i * 25, SP_BURST + 120 + i * 25, SP_BURST + 300 + i * 25, SP_BURST + 760 + i * 40)
                if lv > 0:
                    gr_ = min(1.0, t * 2.2)
                    (front if i == 2 else back).append(dust(fig, FOE[0] + dx * (1 + 0.3 * gr_), GR + dy - 3 * gr_, r0 * (0.6 + 0.5 * gr_), op=lv, seed=70 + i))
        fig.fx_back.append(''.join(back))
        fig.fx_front.append(''.join(front))
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
    cx = (52 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 50 * k, fy - 3.2 * k, cx + 50 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * k)))
    return im


def timeline():
    """La suite de la vidéo (repos ×2, attaque ×2, spéciale ×1) : (action, début, fin) en secondes."""
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
    return O.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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


SPRITE_FEET = (61, 114)          # les pieds dans l'image pixel de la pose (src/game/hd-figures.ts)


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées
    et la place du dessin de la pose dans ces images."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-meduse-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'myths-4.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de son clan, le pixel art à gauche et le vectoriel à
    droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'meduse.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (118, 214)
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
        moments = [1.0, 1.5, a_s + 0.2, a_s + 0.45, a_s + 0.6, a_s + 0.68, a_s + 0.9,
                   s_s + 0.3, s_s + 0.55, s_s + 0.65, s_s + 0.8, s_s + 0.95, s_s + 1.15, s_s + 1.3, s_s + 1.5, s_s + 1.9]
        if len(sys.argv) > 2:
            moments = [float(x) for x in sys.argv[2:]]
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



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : le regard est UN jet ondulant (tête ronde, cœur blanc, halo doux, sans contour sombre), l'éclat
# de l'impact une lumière (plus d'étoile à branches), la poussière en bouffées fondues, les cailloux en galets ;
# la statue, ses morceaux et l'attaque gardent leur dessin.
import effets_pro as E  # noqa: E402

_REGARD = dict(bord=(GAZE[3], GAZE[4], GAZE[4]), milieu=(GAZE[2], GAZE[1]), coeur=(GAZE[0], GAZE[1]), halo=GAZE[2],
               clair=GAZE[0], fonce=GAZE[5], fumee=(GAZE[1], GAZE[2], GAZE[3]))
_PIERRE = (STONE[0], STONE[1], STONE[2], STONE[3], STONE[4], '#24142e')


def _gaze(fig, ctx, p, tail=0.0, amp=3.2, ph=0.0):
    path = resample(gaze_path(ctx), 80)
    n = len(path) - 1
    head = int(p * n)
    i0 = int(tail * n)
    if head - i0 < 2:
        return ''
    pts, ws = [], []
    for i in range(i0, head + 1, 2):
        a = path[max(0, i - 1)]
        b = path[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        rel = (head - i) / max(head, 1)
        off = amp * math.sin(rel * 9.0 + ph) * min(1.0, rel * 4)
        pts.append((path[i][0] + nx * off, path[i][1] + ny * off))
        ws.append(0.4 + 5.0 * (1 - rel) ** 1.4)
    if len(pts) < 2:
        return ''
    ws[0] = 0.1
    hx, hy = pts[-1]
    return E.group([E.jet(fig, pts, ws, _REGARD), E.lumiere(fig, (hx, hy), 10, 0.6, _REGARD), E.boule(fig, (hx, hy), 3.0, ph * 30, _REGARD)])


E.accrocher(sys.modules[__name__], {
    'gaze': _gaze,
    'burst': lambda fig, c, r, rot=0.0, op=1.0, tones=None: E.lumiere(fig, c, r * 2.4, op, _REGARD if tones is None else 'terre'),
    'dust': lambda fig, cx, cy, r, op=1.0, seed=0: E.nuage(fig, cx, cy, r * 1.15, 'terre', op=op, seed=seed, flat=0.75),
    'pebble': lambda fig, x, y, s=1.0, rot=0.0, op=1.0, seed=0: E.caillou(fig, x, y, 1.6 * s, math.degrees(rot), seed=seed, op=op, pierre=_PIERRE),
})


if __name__ == '__main__':
    main()
