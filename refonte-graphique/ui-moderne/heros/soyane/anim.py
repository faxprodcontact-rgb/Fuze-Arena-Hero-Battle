# Soyane vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/arachne/build.py)
# — respiration, attaque de base « Piqûre », attaque spéciale « Nid de pierre » — dans le style lisse de l'interface,
# à 24 images par seconde (même méthode que Kael : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/soyane/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/soyane/
#   python3 refonte-graphique/ui-moderne/heros/soyane/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (soyane.py) est fait de morceaux ; chaque image le redessine dans une POSE : le corps de
# l'araignée se déplace (les pointes des pattes restent plantées), chaque patte est UNE forme recalculée depuis ses
# articulations (hanche, genou pointu, cheville, pointe : elle se plie autour de ses vraies jointures, rien ne se
# décroche), la femme respire et se penche depuis la taille, ses deux bras sont placés par cinématique inverse depuis
# les poings qui tiennent les dagues. Une araignée : mouvements nerveux (de courtes tenues, puis des départs secs), les
# pattes ne bougent jamais toutes ensemble. Les poses clés et les durées reprennent celles du pixel art.
# Effets dans le même style : dégradés, un seul contour, courbes ; aucun flou SVG ; jamais de rayons droits répétés.
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
import soyane as S  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm, bez, resample, INK  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'soyane')
TMP = os.path.join(HERE, '_images')
FPS = 24
VIEW = (-24, -30, 267, 150)          # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = S.GRD
FOE = (194.0, GR)                    # le pied de l'ennemi (130 pixels devant elle, comme le pixel art)
COCOON = (FOE[0], GR - 19)

# tons des effets : soie, pierre, cristal grenat, poussière (ceux du pixel art, passés à la gamme de l'interface)
SILK = ['#ffffff', '#f2ecf8', '#d4cae6', '#a698c4', '#6e6290']
STONE = ['#f0d4b4', '#b88c74', '#86625e', '#563c4a', '#36243a']
STONE_F = ['#c8a690', '#8e6a64', '#664a52', '#44303f', '#2a1c30']   # les pattes de pierre du fond
GARNET = ['#ffe2d4', '#ff8a74', '#e2384c', '#a01a3c', '#5c0c2a']
DUST = ['#f4e8d6', '#d8c4a8', '#a8907c', '#6e5a60']
GINK = '#3a0c1c'                     # le contour du cristal et de l'éclat


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


LEGN = list(S.LEGS0)
BASE = dict(spx=0, spy=0, lean=0, headx=0, heady=0, tilt=0, abd=0, hx=S.HAND0[0], hy=S.HAND0[1], ang=S.ANG0,
            fhx=S.HANDF0[0], fhy=S.HANDF0[1], angF=S.ANGF0, grin=0, smear=0, smearF=0)
NUM = list(BASE) + ['%s%s%s' % (L, j, c) for L in LEGN for j in 'kat' for c in 'xy']


def rest_leg(L, sp):
    """La patte au repos quand le corps est déplacé de sp (le genou suit un peu, la pointe reste plantée)."""
    h, k, a, t = S.LEGS0[L]
    return [h, (k[0] + 0.6 * sp[0], k[1] + 0.6 * sp[1]), (a[0] + 0.2 * sp[0], a[1] + 0.2 * sp[1]), t]


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'sp':
            d['spx'], d['spy'] = v
        elif key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'hand':
            d['hx'], d['hy'] = v
        elif key == 'handF':
            d['fhx'], d['fhy'] = v
        elif key == 'near':          # le poing proche décalé (dx, dy) et sa dague tournée (da)
            d['hx'], d['hy'] = S.HAND0[0] + v[0], S.HAND0[1] + v[1]
            d['ang'] = S.ANG0 + (v[2] if len(v) > 2 else 0)
        elif key == 'far':           # le poing lointain décalé (dx, dy) et sa dague tournée (da)
            d['fhx'], d['fhy'] = S.HANDF0[0] + v[0], S.HANDF0[1] + v[1]
            d['angF'] = S.ANGF0 + (v[2] if len(v) > 2 else 0)
        elif key != 'legs':
            d[key] = v
    sp = (d['spx'], d['spy'])
    legs = k.get('legs', {})
    for L in LEGN:
        pts = rest_leg(L, sp)
        spec = legs.get(L)
        if isinstance(spec, (list, tuple)):
            pts = [pts[0]] + [tuple(p) for p in spec[1:]]
        elif isinstance(spec, dict):
            for j, key in ((1, 'k'), (2, 'a'), (3, 't')):
                if key in spec:
                    pts[j] = (pts[j][0] + spec[key][0], pts[j][1] + spec[key][1])
        for j, c in ((1, 'k'), (2, 'a'), (3, 't')):
            d['%s%sx' % (L, c)], d['%s%sy' % (L, c)] = pts[j]
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# Les pattes du pixel art (hanche, genou, cheville, pointe) : la hanche est celle du dessin, portée par le corps.
R3_UP = [None, (106, 64), (118, 70), (122, 84)]
R4_UP = [None, (114, 56), (126, 60), (131, 72)]
R3_TR = [None, (105, 63), (118, 68), (123, 82)]
R4_TR = [None, (115, 55), (127, 59), (131, 71)]
R3_GO = [None, (112, 66), (128, 84), (134, 104)]
R4_GO = [None, (120, 60), (134, 76), (141, 94)]
R3_HIT = [None, (113, 69), (130, 91), (136, 116)]
R4_HIT = [None, (121, 63), (137, 85), (144, 115.4)]
R3_BK = [None, (108, 67), (122, 82), (126, 98)]
R4_BK = [None, (117, 61), (129, 77), (134, 93)]
R4_DN = [None, (114, 64), (122, 88), (124, 108)]
R3_HIGH = [None, (108, 56), (123, 54), (131, 64)]
R4_HIGH = [None, (117, 48), (131, 46), (139, 56)]
R3_TUG = [None, (107, 57), (122, 55), (130, 65)]
R3_SLAM = [None, (112, 70), (128, 94), (132, 116)]
R4_SLAM = [None, (120, 64), (136, 90), (141, 115.4)]

# 2) L'attaque de base « Piqûre » : elle se ramasse en arrière (corps reculé, dague levée plus haut, les deux pattes
# avant dressées, frémissantes) ; puis tout part d'un coup : le corps bondit, la dague lointaine pique droit dans
# l'ennemi pendant que les deux pattes avant se plantent devant elle comme deux pieux ; elle retire la dague d'un coup
# sec et repique aussitôt ; retour saccadé, patte après patte.
ATTACK = [
    (0, {}),
    (90, dict(legs={'R3': dict(k=(0, -1)), 'L1': dict(k=(0, -1))})),
    (215, dict(sp=(-3, 1), lean=-2, head=(0, 1), abd=1, near=(-1, -2, -4), far=(-2, 1, -3), grin=0.5,
               legs={'R3': R3_UP, 'R4': R4_UP, 'L1': dict(k=(-1, -1)), 'L2': dict(k=(0, -1))})),
    (260, dict(sp=(-3, 1), lean=-2.5, head=(0, 1), abd=0.6, near=(-1, -3, -5), far=(-3, 1, -3), grin=0.8,
               legs={'R3': R3_TR, 'R4': R4_TR, 'L1': dict(k=(-1, -1)), 'L2': dict(k=(0, -1))})),
    (360, dict(sp=(-3.2, 1), lean=-3, head=(0, 1), abd=0.4, near=(-1, -3, -5), far=(-3, 1, -3), grin=1,
               legs={'R3': R3_TR, 'R4': R4_TR, 'L1': dict(k=(-1, -1)), 'L2': dict(k=(0, -1))})),
    (410, dict(sp=(4, 0), lean=3, near=(1, 0, 2), far=(4, -1, 6), smearF=3, grin=1,
               legs={'R3': R3_GO, 'R4': R4_GO})),
    (450, dict(sp=(6, 1), lean=4, head=(1, 0), near=(1, 1, 3), far=(6, 0, 5), grin=1,
               legs={'R3': R3_HIT, 'R4': R4_HIT, 'L1': dict(k=(1, 0)), 'L2': dict(k=(1, 0))})),
    (580, dict(sp=(6, 1), lean=4, head=(1, 0.4), near=(1, 1, 3), far=(6, 0, 5), grin=1,
               legs={'R3': R3_HIT, 'R4': R4_HIT, 'L1': dict(k=(1, 0)), 'L2': dict(k=(1, 0))})),
    (640, dict(sp=(4, 1), lean=2, head=(1, 0), near=(0, 0, 0), far=(0, 0, 0), grin=1,
               legs={'R3': R3_HIT, 'R4': R4_HIT})),
    (690, dict(sp=(6, 1), lean=4, head=(1, 1), near=(1, 1, 3), far=(6, 0, 5), smearF=2, grin=1,
               legs={'R3': R3_HIT, 'R4': R4_HIT})),
    (770, dict(sp=(5.6, 1), lean=3.6, head=(1, 0.8), near=(1, 1, 3), far=(5.6, 0, 5), grin=0.8,
               legs={'R3': R3_HIT, 'R4': R4_HIT})),
    (860, dict(sp=(1, 0), lean=1, near=(0, 0, 0), far=(0, 0, 0), grin=0.5, legs={'R3': R3_BK, 'R4': R4_BK})),
    (950, dict(legs={'R3': dict(k=(0, -1), t=(1, -2)), 'R4': R4_DN})),
    (1080, dict(legs={'R4': dict(k=(0, -1)), 'L2': dict(k=(0, -1))})),
    (1200, {}),
]
HITS = (450, 690)

# 3) L'attaque spéciale « Nid de pierre » : elle se tasse (l'abdomen se gonfle), se cabre (pattes avant dressées) et
# lance de ses filières deux longs fils de soie qui passent au-dessus d'elle en grandes courbes et s'enroulent autour
# de l'ennemi : un cocon. Elle tire sur les fils, puis plante ses deux pattes avant dans le sol : une fissure court
# jusqu'au cocon et QUATRE grandes pattes de pierre aux pointes de cristal grenat jaillissent de la terre et se
# referment sur lui (arrêt sur image), puis s'effritent en éclats et en poussière. Elle se remet en garde.
SPECIAL = [
    (0, {}),
    (100, dict(abd=1, legs={'L2': dict(k=(0, -1)), 'R1': dict(k=(0, -1))})),
    (270, dict(sp=(-2, 3), lean=-2, head=(0, 1), abd=2, near=(0, 1, 0), far=(-2, 1, -2), grin=0.4,
               legs={'R3': dict(k=(0, -2)), 'L1': dict(k=(0, -1))})),
    (460, dict(sp=(-3, -4), lean=-3, head=(0, -1), abd=1, near=(-1, -3, -4), far=(1, -3, 0), grin=1,
               legs={'R3': R3_HIGH, 'R4': R4_HIGH, 'L1': dict(k=(0, -2)), 'L2': dict(k=(0, -1))})),
    (610, dict(sp=(-2, -3), lean=-2, head=(0, -1), abd=0.5, near=(-1, -3, -4), far=(1, -3, 0), grin=1,
               legs={'R3': R3_HIGH, 'R4': R4_HIGH, 'L1': dict(k=(0, -2))})),
    (700, dict(sp=(-4, -2), lean=-4, head=(-1, 0), abd=1, near=(-2, -2, -6), far=(-1, -2, -2), grin=1,
               legs={'R3': R3_TUG, 'R4': R4_HIGH, 'L1': dict(k=(-1, -2)), 'L2': dict(k=(-1, -1))})),
    (735, dict(sp=(-4, -2), lean=-4, head=(-1, 0), abd=1, near=(-2, -2, -6), far=(-1, -2, -2), grin=1,
               legs={'R3': R3_TUG, 'R4': R4_HIGH, 'L1': dict(k=(-1, -2)), 'L2': dict(k=(-1, -1))})),
    (790, dict(sp=(3, 2), lean=3, head=(1, 1), near=(1, 1, 3), far=(2, 1, 2), grin=1,
               legs={'R3': R3_SLAM, 'R4': R4_SLAM, 'L1': dict(k=(1, 0))})),
    (1080, dict(sp=(3, 2), lean=3, head=(1, 0), near=(1, 1, 3), far=(2, 1, 2), grin=1,
                legs={'R3': R3_SLAM, 'R4': R4_SLAM})),
    (1300, dict(sp=(1, 1), lean=1, near=(0, 0, 0), far=(0, 0, 0), grin=0.6, legs={'R3': R3_SLAM, 'R4': R4_SLAM})),
    (1420, dict(sp=(1, 0), grin=0.4, legs={'R3': R3_BK, 'R4': R4_BK})),
    (1520, dict(legs={'R3': dict(k=(0, -1), t=(1, -2)), 'R4': R4_DN})),
    (1640, dict(abd=1, legs={'R4': dict(k=(0, -1)), 'L1': dict(k=(0, -1))})),
    (1780, {}),
]
SP_SLAM = 790
SP_FLASH = 860


# ======================================================================== la respiration et les pattes nerveuses (2 s)

def pulse(t, t0, up=0.06, hold=0.08, down=0.12):
    """Un petit sursaut : monte vite, tient, redescend (t en secondes, dans la boucle)."""
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


# chaque patte a son tressaillement, à son moment (jamais toutes ensemble) : (patte, instant, genou, pointe) ; les
# instants s'étalent sur la boucle du repos de 3 s depuis le 27/11 (×1,5 : elle durait 2 s)
TWITCH = [('L1', 0.18, (0, -1.0), (0, 0)), ('R4', 0.51, (0, -1.0), (0, 0)), ('R3', 0.84, (0.8, -1.8), (1.6, -2.6)),
          ('R2', 1.38, (-1.0, 0), (0, 0)), ('L2', 1.74, (0, -1.1), (0, 0)), ('L4', 2.01, (0.8, -0.4), (0, 0)),
          ('R1', 2.34, (0.9, -0.9), (0, 0)), ('L3', 2.67, (-0.9, -0.3), (0, 0))]

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : la marque rouge de l'abdomen (le losange entre ses deux crochets) s'allume lentement, comme une
    braise, puis s'éteint ; l'abdomen se gonfle un peu avec elle. Une pose partielle pour build() ; jouée au combat
    (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    k = 0.5 - 0.5 * math.cos(u)
    return dict(mk=k, abd=0.9 * k)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    t = T % IDLE_T
    d = dict(heady=0.35 * math.sin(u - 0.7) * 0.6, tilt=0.6 * math.sin(u - 1.0),
             abd=pulse(t, 0.15, 0.05, 0.05, 0.12) + 0.8 * pulse(t, 0.54, 0.05, 0.04, 0.14) + 0.6 * pulse(t, 1.8, 0.06, 0.06, 0.16),
             spy=0.35 * (0.5 - 0.5 * math.cos(u - 2.2)), fhy=0.3 * math.sin(u - 1.1), angF=1.2 * math.sin(u - 1.2),
             hy=0.3 * math.sin(u - 0.9), ang=-0.8 * math.sin(u - 0.9))
    for L, t0, dk, dt in TWITCH:
        p = pulse(t, t0, 0.05, 0.09 if L != 'R3' else 0.16, 0.12)
        if L == 'R3':
            p = pulse(t, t0, 0.06, 0.14, 0.1)
        d['%skx' % L] = dk[0] * p
        d['%sky' % L] = dk[1] * p
        d['%stx' % L] = dt[0] * p
        d['%sty' % L] = dt[1] * p
        # la cheville suit à moitié
        d['%sax' % L] = 0.5 * (dk[0] + dt[0]) * p
        d['%say' % L] = 0.5 * (dk[1] + dt[1]) * p
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
    # le frémissement de l'attaque (tout tremble d'un rien pendant la tenue)
    if action == 'attack' and 215 <= tl <= 360:
        j = math.sin(tl / 1000.0 * 2 * math.pi * 26)
        P['spx'] += 0.35 * j
        P['R3ky'] += 0.5 * j
        P['R4ky'] -= 0.5 * j
        P['angF'] += 1.0 * j
    sg = signe(T)                                  # le signe du repos : la marque de l'abdomen s'allume (anim.signe)
    out = dict(breath=w * br, sp=(P['spx'], P['spy']), lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'],
               abd=P['abd'] + w * sg['abd'], mk=w * sg['mk'], hand=(P['hx'], P['hy']), ang=P['ang'], handF=(P['fhx'], P['fhy']), angF=P['angF'],
               grin=P['grin'], smear=P['smear'], smearF=P['smearF'], ear=math.sin(3 * 2 * math.pi * T / IDLE_T) + 0.6 * P['lean'] / 4)   # 1 s (1,1 avant le 27/11)
    out['legs'] = {L: [S.LEGS0[L][0]] + [(P['%s%sx' % (L, c)], P['%s%sy' % (L, c)]) for c in 'kat'] for L in LEGN}
    out['blink'] = 1.0 if (w > 0.95 and 1.40 <= (T % IDLE_T) < 1.48) else 0.0
    return out


# ======================================================================== les effets (dessinés, un seul contour)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=INK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills if fl is not None)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def shaded(fig, shape, fill, shadow, light, cel=1.0, rim=0.5):
    """Un volume d'effet modelé comme les morceaux du héros : son remplissage, une bande d'ombre en bas à gauche et un
    liseré de lumière en haut à droite, découpés dans la forme."""
    cid = fig.uid('c')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, shape.d()))
    sd = shape.d()
    return ('<path d="%s" fill="%s"/><g clip-path="url(#%s)"><path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.9"/>'
            '<path d="%s%s" fill-rule="evenodd" fill="%s" opacity="0.85"/></g>') % (
        sd, fill, cid, sd, shape.move(cel * 0.8, -cel).d(), shadow, sd, shape.move(-rim * 0.75, rim).d(), light)


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


def dust(fig, cx, cy, r, op=1.0):
    """Une bouffée de poussière : quelques boules réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.3 * r, 0.72 * r), (cx - 0.8 * r, cy + 0.32 * r, 0.68 * r), (cx + 0.1 * r, cy - 0.55 * r, 0.6 * r)]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="#4a3446" stroke="#4a3446" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr)) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def chunk(fig, x, y, s=1.6, rot=0.0, op=1.0):
    """Un éclat de pierre (brun chaud, éclairé en haut à droite)."""
    base = [(-1, -0.6), (0.2, -1.1), (1.1, -0.3), (0.8, 0.9), (-0.6, 1.0)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in base]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, STONE[0]), (0.5, STONE[2]), (1, STONE[4])])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


def shard(fig, x, y, s=1.5, rot=0.0, op=1.0):
    """Un éclat de cristal grenat (losange effilé, une facette claire)."""
    a = math.radians(rot)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (x + s * (u[0] * i + v[0] * j), y + s * (u[1] * i + v[1] * j))
    sh = sm([P(-1.6, 0), P(0, -0.7), P(1.6, 0), P(0, 0.7)], sharp=(0, 1, 2, 3), t=0.3)
    face = sm([P(-1.4, 0), P(0, -0.6), P(1.4, 0)], sharp=(0, 1, 2), t=0.3)
    gr = g_lin(fig, P(1, -1), P(-1, 1), [(0, GARNET[1]), (0.5, GARNET[2]), (1, GARNET[3])])
    return outlined([(sh, gr, 1), (face, GARNET[0], 0.55)], ink=GINK, w=0.9, op=op)


def burst(fig, c, r, rot=0.0, op=1.0):
    """L'éclat de l'impact : une étoile à quatre branches inégales, aux flancs courbes (blanc au cœur, grenat au bord)."""
    if r < 0.4 or op <= 0.02:
        return ''
    pts = []
    arms = (1.0, 0.55, 0.85, 0.5)
    for i in range(4):
        a = math.radians(rot + 90 * i)
        pts.append((c[0] + r * arms[i] * math.cos(a), c[1] + r * arms[i] * math.sin(a)))
        b = math.radians(rot + 90 * i + 45)
        pts.append((c[0] + r * 0.24 * math.cos(b), c[1] + r * 0.24 * math.sin(b)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.9)
    core = sh.scale(0.55, 0.55, c[0], c[1])
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.35, GARNET[0]), (0.7, GARNET[1]), (1, GARNET[2])])
    return outlined([(sh, gr, 1), (core, '#fffaf4', 0.9)], ink=GINK, w=1.0, op=op)


def glow(fig, c, r, color, op):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), g_rad(fig, c, r, [(0, color, op), (0.5, color, op * 0.4), (1, color, 0)]))


def spindle(fig, p0, p1, w, stops):
    """Le souffle de l'estoc : un fuseau effilé (sans contour), de p0 (fin) à p1 (pointe)."""
    pts = [(p0[0] + (p1[0] - p0[0]) * i / 12, p0[1] + (p1[1] - p0[1]) * i / 12) for i in range(13)]
    ws = [max(0.08, w * math.sin(math.pi * i / 12) ** 0.8) for i in range(13)]
    return '<path d="%s" fill="%s"/>' % (ribbon(pts, ws).d(), g_lin(fig, p0, p1, stops))


# ---- l'attaque de base

def fx_attack(tl):
    def f(fig, ctx):
        tip = ctx['tipF']
        a = math.radians(ctx['angF'])
        u = (math.cos(a), math.sin(a))
        nrm = (-u[1], u[0])
        # le souffle de l'estoc pendant la détente (fuseau d'acier pâle le long de la lame, croissant d'air devant)
        for t0 in HITS:
            e = env(tl, t0 - 50, t0 - 15, t0 + 10, t0 + 90)
            if e > 0:
                p0 = (tip[0] - 30 * u[0], tip[1] - 30 * u[1])
                fig.fx_back.append(spindle(fig, p0, tip, 4.2 * e, [(0, '#c8d4ec', 0), (0.6, '#dfe8f6', 0.55 * e), (1, '#ffffff', 0.9 * e)]))
                q0 = (p0[0] + 4 * nrm[0] + 6 * u[0], p0[1] + 4 * nrm[1] + 6 * u[1])
                fig.fx_back.append(spindle(fig, q0, (tip[0] - 4 * u[0] + 2.5 * nrm[0], tip[1] - 4 * u[1] + 2.5 * nrm[1]), 1.8 * e,
                                           [(0, '#a6b6d4', 0), (1, '#e2ecf8', 0.7 * e)]))
        # l'impact : un éclat grenat à la pointe, des éclats de cristal projetés, la poussière sous les pattes plantées
        for i, t0 in enumerate(HITS):
            tau = (tl - t0) / 1000.0
            if tau < 0:
                continue
            c = (tip[0] + 1.5 * u[0], tip[1] + 1.5 * u[1])
            if i == 0 and 'c0' not in fig.ctx:
                pass
            e = env(tau, 0, 0.02, 0.08 if i == 0 else 0.05, 0.22 if i == 0 else 0.16)
            if e > 0:
                fig.fx_back.append(glow(fig, c, 9 * e, '#ff6a5a', 0.45))
                fig.fx_front.append(burst(fig, c, (6.5 if i == 0 else 5.0) * (0.5 + 0.5 * e), rot=-12 + 20 * i + 40 * tau, op=e))
            for j, (vx, vy) in enumerate(((60, -70), (85, -10), (35, -95), (70, 35), (100, -45))[:5 if i == 0 else 3]):
                if tau < 0.42:
                    x, y = ballistic(c, (vx, vy), 160, tau)
                    fig.fx_front.append(shard(fig, x, y, 1.1 if j % 2 else 1.4, rot=tau * 700 + j * 50, op=max(0, 1 - tau / 0.42)))
            if i == 0 and tau < 0.6:
                for L in ('R3', 'R4'):
                    tp = ctx['tips'][L]
                    if tp[1] >= GR - 1.5:
                        k = tau / 0.6
                        fig.fx_back.append(dust(fig, tp[0] + 2 + 3 * k, GR - 1.6 - 3 * k, 2.4 + 2.2 * k, op=0.9 * (1 - k)))
    return f


# ---- l'attaque spéciale : soie, cocon, fissure, pattes de pierre

def silk_curves(ctx):
    """Les deux fils : de la filière, ils passent haut au-dessus d'elle et retombent sur l'ennemi."""
    s0 = ctx['spinner']
    c = COCOON
    return [bez(s0, (s0[0] - 16, s0[1] - 70), (c[0] - 70, c[1] - 120), (c[0] - 2, c[1] - 12), 60),
            bez((s0[0] + 0.6, s0[1] + 1.2), (s0[0] - 6, s0[1] - 58), (c[0] - 40, c[1] - 104), (c[0] + 3, c[1] - 6), 60)]


def silk(fig, pts, a=0.0, b=1.0, w=0.75, sag=0.0):
    """Un fil de soie (un trait fin et pâle, son contour), de la fraction a à b de la courbe."""
    n = len(pts) - 1
    i0, i1 = int(a * n), max(int(a * n) + 2, int(b * n))
    seg = pts[i0:i1 + 1]
    if len(seg) < 3:
        return ''
    if sag:
        m = len(seg) - 1
        seg = [(x, y + sag * math.sin(math.pi * k / m)) for k, (x, y) in enumerate(seg)]
    ws = [0.15] + [w] * (len(seg) - 2) + [0.15]
    ink = ribbon(seg, [0.3] + [w + 0.9] * (len(seg) - 2) + [0.3])
    core = ribbon(seg, ws)
    hl = ribbon([(x + 0.12, y - 0.12) for x, y in seg], [0.05] + [w * 0.35] * (len(seg) - 2) + [0.05])
    return '<path d="%s" fill="#2a1c44" opacity="0.85"/><path d="%s" fill="%s"/><path d="%s" fill="#ffffff" opacity="0.9"/>' % (
        ink.d(), core.d(), SILK[2], hl.d())


def cocoon(fig, c, rx, ry, level=1.0, flash=False):
    """Le cocon de soie : un fuseau pâle (lumière en haut à droite), serré par des tours de fil."""
    sh = sm([(c[0], c[1] - ry), (c[0] + rx * 0.8, c[1] - ry * 0.55), (c[0] + rx, c[1] + ry * 0.1), (c[0] + rx * 0.7, c[1] + ry * 0.65),
             (c[0], c[1] + ry), (c[0] - rx * 0.75, c[1] + ry * 0.62), (c[0] - rx, c[1] + ry * 0.05), (c[0] - rx * 0.78, c[1] - ry * 0.55)],
            sharp=(0, 4), t=0.95)
    gr = g_lin(fig, (c[0] + rx, c[1] - ry), (c[0] - rx, c[1] + ry), [(0, SILK[0] if not flash else '#ffffff'), (0.45, SILK[1]), (1, SILK[3])])
    body = shaded(fig, sh, gr, SILK[3], '#ffffff', cel=1.6, rim=0.7)
    bands = []
    for k, (yy, tilt) in enumerate(((-0.62, 0.22), (-0.3, -0.16), (0.02, 0.2), (0.34, -0.14), (0.62, 0.18))):
        if k / 5 > level + 0.05:
            continue
        y = c[1] + ry * yy
        half = rx * math.sqrt(max(0.05, 1 - yy * yy)) * 1.02
        pts = [(c[0] - half, y + tilt * half), (c[0], y + 0.9 + 0.2 * k % 2), (c[0] + half, y - tilt * half)]
        bands.append('<path d="%s" fill="%s" opacity="0.85"/>' % (ribbon(pts, [0.2, 1.0, 0.2]).d(), SILK[3]))
        bands.append('<path d="%s" fill="#ffffff" opacity="0.8"/>' % ribbon([(x + 0.2, y_ - 0.55) for x, y_ in pts], [0.1, 0.45, 0.1]).d())
    cid = fig.uid('c')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, sh.d()))
    sil = '<path d="%s" fill="%s" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % (sh.d(), INK, INK)
    return sil + body + '<g clip-path="url(#%s)">%s</g>' % (cid, ''.join(bands))


def wrap_threads(fig, c, level):
    """Les fils qui s'enroulent autour de l'ennemi (des ellipses inclinées qui se resserrent)."""
    out = []
    for k, (rx, ry, tilt) in enumerate(((13, 5, 18), (11, 4.6, -16), (12, 4.4, 6))):
        pts = []
        for a in range(0, 290, 8):
            ex, ey = rx * math.cos(math.radians(a)), ry * math.sin(math.radians(a))
            t = math.radians(tilt)
            pts.append((c[0] + ex * math.cos(t) - ey * math.sin(t), c[1] - 8 + k * 6 + a / 60 + ex * math.sin(t) + ey * math.cos(t)))
        out.append(silk(fig, pts, 0, min(1, level * 1.4 - k * 0.15), w=0.65))
    return ''.join(out)


def crack(fig, x0, x1, seed=1):
    """Une fissure qui court au sol (un creux sombre ondulé, ses lèvres claires), de x0 à x1."""
    if x1 - x0 < 2:
        return ''
    n = max(3, int((x1 - x0) / 4))
    pts = [(x0 + (x1 - x0) * i / n, GR + 0.6 + 0.45 * math.sin(i * 1.9 + seed)) for i in range(n + 1)]
    ws = [0.2] + [1.3 + 0.4 * math.sin(i * 2.7) for i in range(1, n)] + [0.2]
    lip = ribbon([(x, y - 0.9) for x, y in pts], [0.1] + [0.7] * (n - 1) + [0.1])
    out = '<path d="%s" fill="%s" opacity="0.85"/><path d="%s" fill="#24121e"/>' % (lip.d(), STONE[1], ribbon(pts, ws).d())
    for bx in (0.33, 0.68):
        if (x1 - x0) * bx > 6:
            p = (x0 + (x1 - x0) * bx, GR + 0.6)
            br = [p, (p[0] + 2.2, p[1] - 0.8), (p[0] + 4.4, p[1] - 0.6)]
            out += '<path d="%s" fill="#24121e"/>' % ribbon(br, [0.9, 0.6, 0.1]).d()
    return out


def stone_claw(fig, base, knee, tip, w, flash=False, cut=1.0, far=False):
    """Une grande patte de pierre sortie du sol : cuisse épaisse qui monte en s'écartant, genou pointu cerclé de
    cristal, jambe en crochet qui redescend en pointe de cristal grenat. cut (0..1) : brisée, il n'en reste que cette
    part depuis le sol."""
    mid = (knee[0] + (tip[0] - knee[0]) * 0.5 + (tip[1] - knee[1]) * 0.1 * (1 if knee[0] < base[0] else -1),
           knee[1] + (tip[1] - knee[1]) * 0.5)
    pts = [base, knee, mid, tip]
    shape, c, ik_, ia, out = S.leg_geom(pts, (w, w * 0.62, w * 0.42, 0.6), spike=2.0, bulge=2.6)
    n = len(c)
    if cut < 1.0:
        m = max(3, int(n * cut))
        cc = c[:m]
        shape = S.limb(cc, [w - (w - w * 0.5) * i / max(1, m - 1) for i in range(len(cc))])
        # la cassure : un bout irrégulier
    st = (STONE_F if far else STONE) if not flash else [S.SKIN.hi, STONE[0], STONE[1], STONE[2], STONE[3]]
    gr = g_lin(fig, (max(p[0] for p in c), min(p[1] for p in c)), (min(p[0] for p in c), GR),
               [(0, st[1]), (0.5, st[2]), (1, st[3])])
    body = shaded(fig, shape, gr, st[3], st[0], cel=1.6, rim=0.8)
    cid = fig.uid('c')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, shape.d()))
    det = []
    # le cristal de la pointe (le dernier tiers de la jambe) et l'anneau de cristal au genou
    if cut >= 0.98:
        k0 = ia - 1
        tipc = c[k0:]
        ws = [w * 1.2] * len(tipc)
        cr = ribbon(tipc, ws)
        g2 = g_lin(fig, (tipc[0][0] + 2, tipc[0][1] - 2), tipc[-1], [(0, GARNET[0] if flash else GARNET[1]), (0.5, GARNET[2]), (1, GARNET[3])])
        det.append('<path d="%s" fill="%s"/>' % (cr.d(), g2))
        det.append('<path d="%s" fill="%s" opacity="0.7"/>' % (ribbon([(x + 0.4, y - 0.4) for x, y in tipc[:-1]], [0.1] + [0.8] * (len(tipc) - 3) + [0.1]).d(), GARNET[0]))
    if cut >= 0.55:
        bd, _ = S.band_at(c, ik_ + 1, 2.6, ws=w * 2, k=0.4)
        det.append('<path d="%s" fill="%s"/>' % (bd.d(), GARNET[2]))
        det.append('<path d="%s" fill="%s" opacity="0.8"/>' % (S.band_at(c, ik_ + 1, 0.9, ws=w * 2, k=-0.2)[0].d(), GARNET[1]))
    # une fêlure claire le long de la cuisse
    rid = [lerp_(c[1], c[ik_ - 1], t) for t in (0, 0.5, 1)]
    det.append('<path d="%s" fill="%s" opacity="0.6"/>' % (ribbon([(x + 1.0, y - 0.6) for x, y in rid], [0.1, 0.9, 0.1]).d(), st[0]))
    sil = '<path d="%s" fill="%s" stroke="%s" stroke-width="1.4" stroke-linejoin="round"/>' % (shape.d(), INK, INK)
    return sil + body + '<g clip-path="url(#%s)">%s</g>' % (cid, ''.join(det))


def lerp_(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# les quatre pattes de pierre autour de l'ennemi : (base x, genou x, genou hauteur, pointe x, pointe hauteur,
# épaisseur, devant ?) — x par rapport à l'ennemi, hauteurs au-dessus du sol
CLAWS = [(-11, -34, 68, -4, 32, 9.0, False), (11, 33, 63, 4, 30, 9.0, False),
         (-6, -25, 53, -1, 20, 8.0, True), (7, 24, 56, 2, 22, 8.0, True)]


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        P = ctx['P']
        # les fils de soie : ils jaillissent des filières, passent au-dessus d'elle, arrivent sur l'ennemi
        cur = silk_curves(ctx)
        if 400 <= t < SP_SLAM + 60:
            prog = min(1.0, max(0.0, (t - 400) / 210.0))
            prog = 1 - (1 - prog) ** 2
            taut = env(t, 690, 720, 760, 790)
            if t < SP_SLAM:
                for k, cv in enumerate(cur):
                    fig.fx_back.append(silk(fig, cv, 0, max(0.04, prog - 0.06 * k), sag=-3 * taut))
            else:
                # les fils cassent : deux bouts qui retombent
                k_ = (t - SP_SLAM) / 60.0
                for k, cv in enumerate(cur):
                    fig.fx_back.append(silk(fig, cv, 0, 0.12 - 0.08 * k_, sag=4 * k_))
                    fig.fx_back.append(silk(fig, cv, 0.88 + 0.08 * k_, 1.0, sag=3 * k_))
        # l'enroulement, puis le cocon
        if 580 <= t < 660:
            lv = (t - 580) / 80.0
            fig.fx_front.append(wrap_threads(fig, COCOON, lv))
            fig.fx_front.append(cocoon(fig, (COCOON[0], COCOON[1] + 4), 7 * lv, 13 * lv, level=lv))
        cocoon_on = 640 <= t < 1210
        # la poussière du coup des pattes avant
        if SP_SLAM <= t < SP_SLAM + 420:
            k = (t - SP_SLAM) / 420.0
            for L in ('R3', 'R4'):
                tp = ctx['tips'][L]
                fig.fx_back.append(dust(fig, tp[0] + 1 + 4 * k, GR - 2 - 4 * k, 3.0 + 2.6 * k, op=0.9 * (1 - k)))
        # la fissure qui court jusqu'au cocon
        if SP_SLAM <= t < 1560:
            x0 = ctx['tips']['R4'][0] + 3
            fr = min(1.0, (t - SP_SLAM) / 60.0)
            fade = 1 - env(t, 1300, 1560, 1600, 1700) if t > 1300 else 1
            x1 = x0 + (FOE[0] - 8 - x0) * fr
            fig.fx_back.append('<g opacity="%g">%s</g>' % (max(0, fade), crack(fig, x0, x1)))
        # le sol se soulève sous l'ennemi
        if 820 <= t < 880:
            lv = (t - 820) / 40.0
            mound = sm([(FOE[0] - 13, GR + 0.6), (FOE[0] - 6, GR - 5 * min(1, lv)), (FOE[0] + 6, GR - 5.5 * min(1, lv)), (FOE[0] + 13, GR + 0.6)], t=0.9)
            fig.fx_front.append(outlined([(mound, g_lin(fig, (FOE[0] + 6, GR - 6), (FOE[0] - 6, GR), [(0, STONE[1]), (1, STONE[3])]), 1)], w=1.3))
        # les pattes de pierre jaillissent, se referment, s'effritent
        if SP_FLASH - 10 <= t < 1420:
            rise = min(1.0, (t - (SP_FLASH - 10)) / 60.0)
            rise = 1 - (1 - rise) ** 3
            close = env(t, 1000, 1080, 2000, 2100)
            crumble = min(1.0, max(0.0, (t - 1180) / 220.0))
            flash = SP_FLASH <= t < SP_FLASH + 90
            for fr_ in (False, True):
                if fr_ and cocoon_on:
                    sq = close
                    fig.fx_front.append(cocoon(fig, (COCOON[0], COCOON[1] + 2 * sq), 9 - 1.6 * sq, 18 - 2.6 * sq, flash=flash))
                for (bx, kx, kh, px, ph, w, front) in CLAWS:
                    if front != fr_:
                        continue
                    sink = (1 - rise) * (kh + 6)
                    sg = -1 if kx < 0 else 1
                    base = (FOE[0] + bx, GR + 3 + sink * 0.2)
                    knee = (FOE[0] + kx - sg * 3 * close, GR - kh + sink + 2 * close)
                    tip = (FOE[0] + px - sg * 3 * close, GR - ph + sink + 5 * close)
                    layer = fig.fx_front
                    # découpe au sol : ce qui est sous la terre ne se voit pas (un rectangle de découpe)
                    cid = fig.uid('c')
                    fig.defs.append('<clipPath id="%s"><rect x="-200" y="-200" width="800" height="%s"/></clipPath>' % (cid, fm(GR + 200 + 0.8)))
                    layer.append('<g clip-path="url(#%s)">%s</g>' % (cid, stone_claw(fig, base, knee, tip, w, flash=flash, cut=1.0 - 0.75 * crumble, far=not front)))
        elif cocoon_on:
            fig.fx_front.append(cocoon(fig, COCOON, 9, 18))
        # l'éclair (arrêt sur l'image) : un éclat clair qui part du cocon
        fl = env(t, SP_FLASH - 10, SP_FLASH, SP_FLASH + 30, SP_FLASH + 150)
        if fl > 0:
            c = (COCOON[0], COCOON[1] - 4)
            fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(120), g_rad(
                fig, c, 120, [(0, '#ffffff', 0.85 * fl), (0.14, '#ffe2d4', 0.5 * fl), (0.45, '#ff8a74', 0.14 * fl), (1, '#e2384c', 0)])))
        # éclats de pierre et de cristal projetés, puis poussière
        if SP_FLASH <= t < 1700:
            tau = (t - SP_FLASH) / 1000.0
            for j, (vx, vy, kind) in enumerate(((-60, -110, 'c'), (55, -125, 's'), (-95, -70, 's'), (90, -80, 'c'), (-25, -150, 'c'),
                                                (30, -140, 's'), (-120, -40, 'c'), (125, -50, 's'), (5, -170, 'c'))):
                st = 0 if j < 5 else 0.3
                tt = tau - st
                if 0 <= tt < 0.75:
                    x, y = ballistic((FOE[0] + (j - 4) * 2.5, GR - 12), (vx, vy), 300, tt)
                    if y < GR - 0.5:
                        fig.fx_front.append(chunk(fig, x, y, 1.6, rot=tt * 600 + j * 50) if kind == 'c' else shard(fig, x, y, 1.4, rot=tt * 800 + j * 40))
        if 1180 <= t < 1760:
            k = (t - 1180) / 580.0
            o = env(k, 0, 0.12, 0.5, 1.0)
            for j, (dx, rr, sp) in enumerate(((-24, 5.2, 10), (23, 5.0, 12), (-12, 4.2, 18), (13, 4.0, 16), (0, 5.6, 22))):
                fig.fx_front.append(dust(fig, FOE[0] + dx * (1 + 0.3 * k), GR - 3 - sp * k, rr * (0.7 + 0.6 * k), op=0.9 * o))
        # pendant la charge : l'abdomen gonflé luit d'un rouge sourd (la marque s'allume)
        ch = env(t, 150, 300, 560, 700)
        if ch > 0:
            fig.under.append((ctx['spinner'][0] + 22, ctx['spinner'][1] - 14, 26, 22, '#ff5a4a', 0.16 * ch, None))
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
    cx = (64 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 60 * k, fy - 3.2 * k, cx + 60 * k, fy + 3.2 * k], fill=(10, 4, 24, 150))
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
    return S.build(ow=ow, pose=P, fx=fx, frame=view).svg()


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


SPRITE_FEET = (59, 115)          # les pieds dans l'image pixel de la pose (src/game/hd-figures.ts)


def pixel_frames(name):
    """Les images d'une animation pixel art (ses GIF de contrôle, fond clair retiré), à l'échelle 1, avec leurs durées
    et la place du dessin de la pose dans ces images."""
    import numpy as np
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-arachne-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (a[:, :, 2] == 242)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.open(os.path.join(ROOT, 'public', 'art', 'hd', 'pose', 'myths-10.webp'))
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de son clan, le pixel art à gauche et le vectoriel à
    droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
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
        moments = [1.0, 1.5, a_s + 0.3, a_s + 0.42, a_s + 0.47, a_s + 0.7, a_s + 0.9,
                   s_s + 0.27, s_s + 0.5, s_s + 0.62, s_s + 0.72, s_s + 0.8, s_s + 0.88, s_s + 1.05, s_s + 1.25, s_s + 1.45]
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
        dst = os.path.join('/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-soyane', 'planche.png')
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
