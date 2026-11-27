# Le Canonnier vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/canonnier/build.py)
# — pose (le colosse qui souffle), attaque de base « Coup de canon », attaque spéciale « Ricochet » — dans le style lisse
# de l'interface, à 24 images par seconde (même méthode que les héros : ../../heros/kael/anim.py, ../../heros/barzul/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/canonnier/anim.py              # → anim.mp4 + anim.gif (pixel/sortie/ui/vecto/canonnier/)
#   python3 refonte-graphique/ui-moderne/monstres/canonnier/anim.py --planche [instants en s]   # planche d'images clés
#
# Méthode : le dessin (canonnier.py) est fait de morceaux ; chaque image le redessine dans une POSE (squelette) : le
# souffle soulève la tête, les épaules et le haut des bras (le canon et les mains restent), le haut du corps se penche
# depuis les hanches (le recul le rejette sur sa jambe de bois, les pieds restent à plat), la tête suit avec un temps de
# retard ; le canon pivote autour du poing proche (il se cabre au coup, il s'abaisse pour la spéciale) et recule le long
# de son axe ; les deux bras sont placés par cinématique inverse depuis les mains posées sur le canon (rien ne se
# décroche). Poses clés et durées : celles du pixel art, reliées par des courbes douces sans dépassement.
# Effets (formes rondes et courbes, dégradés, un contour, aucun flou ; jamais de rayons droits) : la mèche qui grésille
# sur la lumière, l'éclair rond du coup, le boulet de fonte, les grosses bouffées de fumée blanche en volutes, la
# poussière aux talons ; pour la spéciale : l'eau de mer qui s'enroule autour de la bouche, le boulet enveloppé d'eau
# qui rase le sol et ricoche trois fois (gerbes en couronne, la troisième énorme, arrêt sur l'image), la vague qui roule
# vers la droite ; il éclate de rire. Outils d'effets recopiés de Barzul (son capitaine) : mêmes bleus, même fumée.
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import canonnier as B  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, lock, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of, taper, crpath  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'canonnier')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-canonnier'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-22.0, -42.0, 336.0, 189.0)  # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = B.GRD
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']   # l'eau (celle de Barzul, Kesha, Ilian)
WINK = '#0c1846'                     # le contour de l'eau
SMOKE = ['#ffffff', '#f4f2f8', '#dedcea', '#b8b6d0', '#8e8cae']               # la fumée de poudre (jamais de noir)
SINK = '#3a3660'                     # le contour de la fumée
FIRE = ['#fffce4', '#ffe46e', '#ffa03c', '#e0583a']                           # le feu de la poudre
FINK = '#6a1a14'
IRON = ['#d0d4ea', '#73769a', '#3e3a58', '#241e36']                           # les boulets de fonte
DUST = ['#fbf2e0', '#eee2ca', '#d4c2a2', '#b09a80', '#86705e']                # la poussière (terre claire, ombre brun gris)
DINK = '#5a4640'


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


PAIRS = {'head': ('headx', 'heady')}
SCAL = ['crouch', 'lean', 'shift', 'tilt', 'sq', 'cri', 'cang', 'crec', 'tl', 'sh', 'rn', 'rf', 'b']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: B.REST.get(n, 0.0) for n in SCAL}
    for key, (a, b) in PAIRS.items():
        d[a], d[b] = B.REST[key]
    for key, v in k.items():
        if key in PAIRS:
            d[PAIRS[key][0]], d[PAIRS[key][1]] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, durées du pixel art)
# 2) « Coup de canon » : il se ramasse et vise (il plisse les yeux, la bouche du canon descend un peu) ; la mèche
# grésille sur la lumière, il tient… BOUM : l'éclair, le boulet part vers la droite ; le recul le rejette en arrière sur
# sa jambe de bois (le canon se cabre et recule, poussière aux talons, grosse fumée blanche) ; il revient lourdement,
# se tasse en place et montre les dents ; un filet de fumée monte de la bouche du canon.
AIM = dict(crouch=1.6, lean=1.2, head=(0.0, 0.5), sq=1.0, tilt=-1.2, cang=2.4, tl=0.4)
ATTACK = [
    (0, {}),
    (130, dict(crouch=1.2, lean=1.0, head=(0.0, 0.8), sq=1.0, tilt=-1.0, cang=2.0, tl=0.5)),
    (270, dict(AIM)),
    (490, dict(AIM, cang=2.6)),
    (530, dict(crouch=0.6, lean=-3.6, head=(0.6, 0.0), sq=0.6, tilt=2.0, cang=-6.0, crec=2.4, shift=-0.6, tl=-1.2, sh=-1.0)),
    (600, dict(crouch=0.2, lean=-5.0, head=(-0.2, 0.0), sq=0.3, tilt=4.0, cang=-9.0, crec=3.0, shift=-1.0, tl=-1.6, sh=-1.4, rn=0.6)),
    (700, dict(crouch=0.6, lean=-3.4, head=(-0.6, 0.0), tilt=2.6, cang=-5.0, crec=1.6, shift=-0.8, tl=0.6, sh=0.4)),
    (820, dict(crouch=1.0, lean=-1.0, head=(0.0, 0.4), tilt=1.0, cang=-1.2, crec=0.4, shift=-0.2, tl=1.0, sh=0.8)),
    (960, dict(crouch=0.8, head=(0.0, 0.6), cri=0.35, tl=-0.4)),
    (1150, dict(crouch=0.3, head=(0.0, -0.3), cri=0.3)),
    (1340, {}),
]
ATT_FUSE = (140, 490)        # la mèche grésille
ATT_SHOT = 490               # BOUM

# 3) « Ricochet » : il se ramasse et abaisse son canon vers le sol ; l'eau de mer monte du sol et s'enroule autour de la
# bouche ; la mèche grésille… BOUM : l'anneau d'eau éclate, le recul le rejette loin ; un boulet enveloppé d'eau rase
# le sol et ricoche trois fois vers la droite — à chaque rebond une gerbe d'eau, la troisième (sur le premier rang
# ennemi) la plus grosse : arrêt sur l'image, une vague roule au sol vers la droite ; il éclate de rire (la tête et les
# épaules sautent), puis se tasse en place ; un filet de fumée monte encore du canon.
LOW = dict(crouch=1.8, lean=2.0, head=(0.0, 0.4), sq=1.0, tilt=-2.0, cang=10.0, tl=0.6)
SPECIAL = [
    (0, {}),
    (110, dict(crouch=1.2, lean=1.0, head=(0.0, 0.8), sq=1.0, tilt=-1.0, cang=5.0, tl=0.6)),
    (230, dict(LOW)),
    (470, dict(LOW, cang=10.6)),
    (520, dict(crouch=0.4, lean=-4.6, head=(0.8, 0.0), tilt=2.0, cang=2.0, crec=2.6, shift=-0.8, tl=-1.4, sh=-1.2)),
    (600, dict(crouch=0.0, lean=-6.0, head=(0.0, 0.0), tilt=3.5, cang=-4.0, crec=3.6, shift=-1.2, tl=-1.8, sh=-1.6, rn=0.6)),
    (700, dict(crouch=0.4, lean=-4.0, head=(-0.6, 0.0), tilt=2.4, cang=-2.0, crec=2.0, shift=-0.8, tl=0.6, sh=0.4)),
    (850, dict(crouch=1.0, lean=-1.2, head=(0.0, 0.5), tilt=0.6, crec=0.4, shift=-0.2, tl=1.0, sh=0.8)),
    (920, dict(crouch=0.6, head=(0.0, -0.4), cri=1.0, tilt=-1.0, b=0.8, rn=0.6, rf=0.6)),
    (1010, dict(crouch=1.1, head=(0.0, 1.0), cri=1.0, tilt=0.6, b=0.2, rn=0.0, rf=0.0, tl=-0.6)),
    (1100, dict(crouch=0.4, head=(0.0, -0.9), cri=1.0, tilt=-1.0, b=1.0, rn=1.0, rf=1.0, tl=0.8)),
    (1190, dict(crouch=1.1, head=(0.0, 1.0), cri=1.0, tilt=0.6, b=0.2, rn=0.0, rf=0.0, tl=-0.6)),
    (1290, dict(crouch=0.5, head=(0.0, -0.5), cri=0.9, tilt=-0.6, b=0.8, rn=0.7, rf=0.7, tl=0.5)),
    (1450, dict(crouch=0.7, head=(0.0, 0.4), cri=0.5, b=0.3)),
    (1660, dict(crouch=0.4, head=(0.0, 0.0), cri=0.0)),
    (2070, {}),
]
SP_FUSE = (230, 470)
SP_SHOT = 470
BOUNCES = [(190.0, 640.0, 0.62), (227.0, 780.0, 0.85), (262.0, 920.0, 1.4)]   # les rebonds (x, instant en ms, taille)
FREEZE = (920, 1180)                 # le troisième coup : arrêt sur l'image (les effets ralentissent)
FOE_X = 262.0


def fx_time(t):
    """Le temps des effets de la spéciale : il ralentit pendant l'arrêt sur l'image."""
    a, b = FREEZE
    if t <= a:
        return t
    if t <= b:
        return a + (t - a) * 0.22
    return a + (b - a) * 0.22 + (t - b)


# ======================================================================== la pose (le colosse qui souffle, 1,6 s)
IDLE_T = 1.6


def idle_offsets(T):
    """Il souffle (la tête, les épaules et le haut des bras montent ; le canon et les mains restent), il se tasse un peu
    à l'expiration, la tête suit avec retard, les pans du bandana et de la ceinture se balancent."""
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    d = dict(crouch=0.45 * (0.5 - 0.5 * math.cos(u - 2.6)), heady=0.35 * math.sin(u - 0.8), tilt=-0.5 * math.sin(u - 1.0),
             rn=0.5 * (0.5 - 0.5 * math.cos(u - 0.3)), rf=0.4 * (0.5 - 0.5 * math.cos(u - 0.7)),
             tl=0.8 * math.sin(u + 0.4), sh=0.6 * math.sin(u + 1.0), lean=0.25 * math.sin(u - 0.5))
    return d, br


def pose_at(T, action=None, t0=0.0):
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 280)) / 280))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {}
    for n in NUM:
        P[n] = src[n] + w * idl.get(n, 0.0)
    out = dict(breath=min(1.3, br * w + P['b']), crouch=P['crouch'], lean=P['lean'], shift=P['shift'],
               head=(P['headx'], P['heady']), tilt=P['tilt'], sq=max(0.0, min(1.0, P['sq'])), cri=max(0.0, P['cri']),
               cang=P['cang'], crec=max(0.0, P['crec']), tl=P['tl'], sh=P['sh'], rn=P['rn'], rf=P['rf'])
    # un clignement de temps en temps (pas pendant les attaques, où il plisse les yeux)
    out['blink'] = 1.0 if (w > 0.95 and 2.30 <= (T % 3.2) < 2.39) else 0.0
    return out


# ======================================================================== les effets (dégradés, aucun flou)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, r if ry is None else ry, stops)


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
    if op <= 0.01:
        return ''
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r), fm(ry), fig.rad(
        c[0], c[1], r, ry, [(0, color, op), (0.45, color, op * 0.4), (1, color, 0)]))


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour ; une 4e valeur = pas de silhouette (reflet peint dedans)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, 2 * op)), sil, col)


def stroke_shape(center, widths):
    left, right = sides(center, widths)
    pts = [center[0]] + left[1:-1] + [center[-1]] + right[1:-1][::-1]
    return sm(pts, sharp=(0, len(left) - 1), t=0.85)


def spiral(p, d, r0, turn, s, n=14):
    """Une volute : depuis p dans la direction d, elle s'enroule (s = +1 sens horaire à l'écran) sur `turn` degrés."""
    L = math.hypot(*d) or 1
    dx, dy = d[0] / L, d[1] / L
    nx, ny = (-dy * s, dx * s)
    C = (p[0] + nx * r0, p[1] + ny * r0)
    a0 = math.atan2(p[1] - C[1], p[0] - C[0])
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = a0 + s * math.radians(turn) * t
        r = r0 * (1 - 0.65 * t)
        out.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    return out


# ---- la fumée de poudre : des boules blanches réunies sous un contour doux, l'ombre lavande en bas à gauche

def smoke(fig, cx, cy, r, op=1.0, k=0):
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.85, 0.25, 0.72), (-0.86, 0.3, 0.7), (0.25, -0.6, 0.66), (-0.4, -0.42, 0.55), (1.3, -0.2, 0.45)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in J[:4 + (k % 3)]]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.8, cy + r), [(0, SMOKE[0]), (0.45, SMOKE[1]), (0.8, SMOKE[2]), (1, SMOKE[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), SINK, SINK)
                  for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    # le dessous de la bouffée, dans l'ombre (lavande), puis un reflet en haut à droite
    sh = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.5"/>' % (fm(x - rr * 0.25), fm(y + rr * 0.35), fm(rr * 0.7), SMOKE[3])
                 for x, y, rr in balls[:2])
    hi = '<circle cx="%s" cy="%s" r="%s" fill="#ffffff" opacity="0.9"/>' % (fm(cx + 0.35 * r), fm(cy - 0.35 * r), fm(0.28 * r))
    return '<g opacity="%g">%s%s%s%s</g>' % (max(0, min(1, op)), sil, col, sh, hi)


def curl(fig, p, d, r0, turn, s, w, op=1.0, tones=None):
    """Une volute de fumée (ou d'écume) : un ruban qui s'enroule, effilé au bout."""
    if op <= 0.02 or r0 < 0.3:
        return ''
    c = [p] + spiral(p, d, r0, turn, s, 16)
    n = len(c)
    ws = [max(0.08, w * (1 - i / (n - 1)) ** 0.8 * min(1, 2.5 * i / (n - 1) + 0.3)) for i in range(n)]
    sh = stroke_shape(c, ws)
    tones = tones or SMOKE
    gr = g_lin(fig, c[0], c[-1], [(0, tones[1]), (1, tones[3])])
    return outlined([(sh, gr, 1)], ink=SINK, w=0.9, op=op)


# ---- le feu de la poudre : un éclair rond, quelques langues arrondies (jamais de rayons réguliers)

def flash(fig, c, r, facing=0.0, op=1.0):
    if op <= 0.02 or r < 0.3:
        return ''
    out = glow(fig, c, r * 2.6, FIRE[1], 0.55 * op)
    lobes = [(0, 1.0), (55, 0.62), (-60, 0.7), (150, 0.45), (-140, 0.5), (100, 0.4)]
    pts = []
    for i, (da, L) in enumerate(lobes):
        a = math.radians(facing + da)
        pts.append((da, L))
    pts.sort()
    ring = []
    for da, L in pts:
        a = math.radians(facing + da)
        ring.append((c[0] + r * L * 1.25 * math.cos(a), c[1] + r * L * 1.25 * math.sin(a)))
        a2 = math.radians(facing + da + 22)
        ring.append((c[0] + r * 0.5 * math.cos(a2), c[1] + r * 0.5 * math.sin(a2)))
    body = sm(ring, t=0.75)
    core = body.scale(0.55, 0.55, c[0], c[1])
    gr = g_rad(fig, c, r * 1.3, [(0, FIRE[0]), (0.4, FIRE[1]), (0.8, FIRE[2]), (1, FIRE[3])])
    out += outlined([(body, gr, 1), (core, FIRE[0], 0.9, 'n')], ink=FINK, w=1.0, op=op)
    return out


def spark(fig, c, r, op=1.0, rot=0.0):
    """Une étincelle : une étoile à quatre branches inégales aux flancs courbes (blanc au cœur)."""
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
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.4, FIRE[0]), (1, FIRE[1])])
    return glow(fig, c, r * 1.3, FIRE[1], 0.45 * op) + '<path d="%s" fill="%s" opacity="%g"/>' % (sh.d(), gr, op)


# ---- l'eau (mêmes outils et mêmes couleurs que Kesha et Ilian)

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
    return '<g opacity="%g">%s%s%s</g>' % (max(0, min(1, 2 * op)), sil, col, hi)


def sheet(fig, base, ang, length, bend, w, op=1.0, tail=0.0):
    """Une nappe d'eau qui jaillit : un ruban courbe, large à la base, fin et clair au bout, qui se casse en goutte."""
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
    rr = max(0.6, w * 0.2)
    bead = ellipse(p3[0] + d[0] * rr * 0.6, p3[1] + d[1] * rr * 0.6, rr, rr)
    return outlined([(sh, gr, 1), (bead, WATER[1], 1), (core, gc, 0.75, 'n'),
                     (ellipse(p3[0] + d[0] * rr * 0.6 + rr * 0.3, p3[1] + d[1] * rr * 0.6 - rr * 0.35, rr * 0.35, rr * 0.3), '#ffffff', 1, 'n')], op=op)


def mound(fig, X, h, L, op=1.0, foamy=1.0):
    """Une bosse d'eau posée au sol (le sol qui bouillonne, la base de la gerbe) : dos courbe, écume sur le dessus."""
    if h < 0.6 or op <= 0.02:
        return ''
    G = GR + 0.4
    sh = sm([(X - L, G), (X - L * 0.6, G - h * 0.55), (X - L * 0.2, G - h), (X + L * 0.25, G - h * 0.95), (X + L * 0.65, G - h * 0.45),
             (X + L, G)], sharp=(0, 5), t=0.9)
    gr = g_lin(fig, (X + L * 0.5, G - h), (X - L * 0.6, G), [(0, WATER[2]), (0.45, WATER[3]), (1, WATER[4])])
    crest = sm([(X - L * 0.55, G - h * 0.58), (X - L * 0.2, G - h * 0.98), (X + L * 0.25, G - h * 0.93), (X + L * 0.6, G - h * 0.5),
                (X + L * 0.2, G - h * 0.68), (X - L * 0.2, G - h * 0.72)], t=0.9)
    glint = ribbon([(X - L * 0.7, G - h * 0.2), (X - L * 0.5, G - h * 0.45), (X - L * 0.3, G - h * 0.62)], [0.2, max(0.5, h * 0.06), 0.2])
    return outlined([(sh, gr, 1), (crest, '#ffffff', min(1, foamy), 'n'), (glint, WATER[1], 0.6, 'n')], w=1.4, op=op)


# (la colonne d'eau de Kesha, ../kesha/anim.py)
def column(fig, X, top, wb, wt, sway, t, op=1.0):
    """La grande gerbe : une colonne d'eau qui monte du sol (plus large en bas), ses bords ondulent ; la lumière à
    droite ; une couronne d'écume au sommet et deux lèvres qui retombent en volute de chaque côté."""
    if GR - top < 2 or op <= 0.02:
        return ''
    G = GR + 0.4
    H = G - top
    n = 8
    left, right = [], []
    for i in range(n + 1):
        k = i / n
        y = G - H * k
        w = wb + (wt - wb) * k ** 0.8
        wob = 0.9 * math.sin(k * 7 + t * 9) * (0.3 + k)
        x = X + sway * k * k
        left.append((x - w / 2 + wob, y))
        right.append((x + w / 2 + wob * 0.6, y))
    sh = sm(left + right[::-1], sharp=(0, 2 * n + 1), t=0.9)
    gr = g_lin(fig, (X - wb / 2, 0), (X + wb / 2, 0), [(0, WATER[4]), (0.35, WATER[3]), (0.75, WATER[2]), (1, WATER[1])])
    hi = taper([(r[0] - wt * 0.22, r[1]) for r in right[1:-1]], wb * 0.07, wt * 0.08, tip='round')
    dk = taper([(l_[0] + wt * 0.16, l_[1]) for l_ in left[1:-2]], wb * 0.08, wt * 0.05, tip='round')
    items = [(sh, gr, 1), (hi, '#ffffff', 0.7, 'n'), (dk, WATER[5], 0.35, 'n')]
    # la couronne d'écume déborde un peu de chaque côté
    cx = X + sway
    out = outlined(items, w=1.5, op=op)
    for j, (dx, dy, rr) in enumerate(((-0.62, 2.6, 0.22), (0.66, 2.2, 0.22), (-0.42, -0.6, 0.3), (0.4, -0.8, 0.32),
                                      (-0.16, -2.6, 0.38), (0.18, -3.4, 0.4), (0.0, -5.6, 0.34))):
        out += foam(fig, cx + dx * wt, top + dy * (wt / 14.0), rr * wt * (1 + 0.07 * math.sin(t * 11 + j * 1.7)), op=op, seed=j)
    return out


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def splash_crown(fig, X, k, big=1.0, seed=0):
    """La gerbe en couronne là où tombe un boulet : des nappes qui s'ouvrent en couronne, de l'écume, des gouttes
    (k : 0 → 1 le temps de la gerbe)."""
    out_b, out_f = [], []
    if k <= 0 or k >= 1:
        return out_b, out_f
    e = math.sin(math.pi * min(1, k * 1.25)) if k < 0.8 else max(0, (1 - k) / 0.2) * math.sin(math.pi * 0.999)
    e = max(0.0, e)
    PET = ((-7, -128, 13, -46, 5.6), (-2, -100, 20, -26, 6.4), (3, -76, 19, 28, 6.4), (7, -52, 13, 46, 5.6))
    if seed % 2:
        PET = tuple((dx, a + 6, L * 0.92, bd, w) for dx, a, L, bd, w in PET)
    for j, (dx, ang, L, bd, w) in enumerate(PET):
        L_ = 1.45 * L * big * (0.4 + 0.6 * min(1, k * 2.2)) * (1 - 0.35 * max(0, k - 0.5) * 2)
        (out_b if j in (0, 3) else out_f).append(sheet(fig, (X + dx * big, GR + 0.2), ang, L_, bd, w * big ** 0.8,
                                                          op=min(1, e * 1.6), tail=max(0, k - 0.45) * 1.2))
    out_f.append(mound(fig, X, 5 * big * e, 14 * big, op=min(1, e * 1.5)))
    for j, (vx, vy) in enumerate(((-55, -120), (40, -135), (-90, -80), (85, -95), (-20, -150), (15, -160), (110, -60))):
        tau = k * 0.75 - 0.03 * (j % 3)
        if 0 < tau < 0.75:
            x, y = ballistic((X, GR - 3), (vx * big ** 0.6, vy * big ** 0.6), 330, tau)
            if y < GR:
                out_f.append(drop(fig, x, y, vx, vy + 330 * tau, (1.1 if j % 2 else 0.85) * big ** 0.4))
    for j in range(3):
        out_f.append(foam(fig, X - 7 * big + 7 * big * j, GR - 1.2, 1.8 * big * e, op=min(1, e * 1.5), seed=j + seed))
    return out_b, out_f


def stream(fig, pts, w0, w1, op=1.0, light=False):
    """Un filet d'eau le long d'une courbe : fin derrière, plein devant, crête claire."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=20)
    sh = taper(c, w0, w1, tip='round')
    crest = taper([(x + 0.25, y - 0.35) for x, y in c[4:]], w0 * 0.2, w1 * 0.3, tip='round')
    gr = g_lin(fig, c[0], c[-1], [(0, WATER[2] if light else WATER[3]), (0.6, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.85, 'n')], w=1.1, op=op)




def dust(fig, cx, cy, r, op=1.0, k=0):
    """Une bouffée de poussière (terre claire) : des boules réunies sous un contour doux, l'ombre en bas à gauche."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.9, 0.2, 0.7), (-0.85, 0.25, 0.66), (0.3, -0.55, 0.62), (-0.45, -0.4, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in J[:3 + (k % 3)]]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r * 0.8, cy + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[3])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.9"/>' % (fm(x), fm(y), fm(rr), DINK, DINK)
                  for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    sh = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.45"/>' % (fm(x - rr * 0.25), fm(y + rr * 0.35), fm(rr * 0.7), DUST[3])
                 for x, y, rr in balls[:2])
    return '<g opacity="%g">%s%s%s</g>' % (max(0, min(1, op)), sil, col, sh)


def cannonball(fig, c, r):
    """Un boulet de fonte (noir bleuté, reflet en haut à droite)."""
    return outlined([(ellipse(c[0], c[1], r, r), g_rad(fig, (c[0] + r * 0.3, c[1] - r * 0.35), r * 1.4,
                                                        [(0, IRON[0]), (0.35, IRON[1]), (0.75, IRON[2]), (1, IRON[3])]), 1),
                     (ellipse(c[0] + r * 0.35, c[1] - r * 0.4, r * 0.3, r * 0.22, -30), '#ffffff', 0.85, 'n')], ink='#160f26', w=1.2)


SHOT = {}


def shot_at(action):
    """La bouche du canon (et sa direction) à l'instant du coup : la fumée y reste."""
    if action not in SHOT:
        t = (ATT_SHOT if action == 'attack' else SP_SHOT) / 1000.0
        ctx = B.build(pose=pose_at(t, action, 0.0)).ctx
        SHOT[action] = (ctx['muzzle'], ctx['muzzle_dir'])
    return SHOT[action]


def fuse(fig, ctx, t, t0, t1):
    """La mèche qui grésille sur la lumière : de petites étincelles qui sautent, une lueur orange."""
    if not (t0 <= t <= t1 + 30):
        return
    e = env(t, t0, t0 + 40, t1 - 10, t1 + 30)
    v = ctx['vent']
    fig.fx_front.append(glow(fig, (v[0], v[1] - 0.6), 3.4, FIRE[2], 0.5 * e))
    for j in range(3):
        ph = (t / 70.0 + j * 0.37) % 1.0
        a = math.radians(-120 + 70 * j + 25 * math.sin(t / 37.0 + j))
        d = 1.0 + 3.2 * ph
        p = (v[0] + d * math.cos(a), v[1] - 0.6 + d * math.sin(a) + 2.0 * ph * ph)
        fig.fx_front.append(spark(fig, p, (1.5 - 1.1 * ph) * e + 0.2, op=e * (1 - ph * 0.7), rot=37 * j + t / 9.0))


def smoke_cloud(fig, M0, D0, t, dur, big=1.0, seed=0):
    """La grosse fumée blanche du coup : des bouffées poussées vers l'avant, qui ralentissent, gonflent, montent et se
    défont ; deux volutes."""
    PUFFS = [(6.0, -1.0, 4.4, 0), (13.0, -3.0, 5.4, 15), (21.0, -5.0, 5.0, 30), (29.0, -7.6, 4.0, 45), (3.0, -4.4, 3.2, 25),
             (17.0, 1.6, 3.4, 40)]
    CURLS = [((32.0, -10.0), (1, -0.6), 3.6, 1), ((2.0, -8.0), (-0.6, -1), 2.8, -1)]
    out = []
    a = math.atan2(D0[1], D0[0])
    ca, sa = math.cos(a), math.sin(a)
    rotp = lambda dx, dy: (M0[0] + (dx * ca - dy * sa) * big, M0[1] + (dx * sa + dy * ca) * big)
    k = t / dur
    for j, (dx, dy, r, dl) in enumerate(PUFFS):
        kk = max(0.0, min(1.0, (t - dl) / (dur - dl)))
        if kk <= 0:
            continue
        go = 1 - (1 - min(1, kk * 2.6)) ** 3
        c = rotp(dx * go + 3.0 * kk, dy * go)
        c = (c[0], c[1] - kk * 6.0)
        rr = big * r * (0.35 + 0.65 * go) * (1 + 0.35 * kk) * (1 - smooth((kk - 0.62) / 0.38) * 0.75)
        op = 1 - smooth((kk - 0.55) / 0.45)
        out.append(smoke(fig, c[0], c[1], rr, op=op, k=j + seed))
    for j, ((dx, dy), d, r0, s) in enumerate(CURLS):
        e = env(k, 0.18, 0.35, 0.6, 0.9)
        if e > 0:
            p = rotp(dx + 2 * k, dy)
            p = (p[0], p[1] - 5 * k)
            out.append(curl(fig, p, d, r0 * big * (0.6 + 0.4 * e), 200 + 120 * e, s, 1.6 * big * e, op=e))
    return out


def heel_dust(fig, t, t0, big=1.0):
    """La poussière soulevée aux talons par le recul (derrière la jambe de bois et la botte)."""
    out = []
    k = (t - t0) / 520.0
    if not (0 < k < 1):
        return out
    for j, (x, dx, r) in enumerate(((44.0, -9.0, 2.6), (40.0, -14.0, 1.9), (73.0, -8.0, 2.4), (69.0, -12.0, 1.7))):
        kk = max(0.0, min(1.0, k * 1.2 - 0.08 * (j % 2)))
        go = 1 - (1 - kk) ** 2
        rr = big * r * (0.5 + 0.7 * go) * (1 - smooth((kk - 0.55) / 0.45) * 0.8)
        out.append(dust(fig, x + dx * go * big, GR - 1.2 - rr * 0.6 - 2.0 * kk, rr, op=1 - smooth((kk - 0.5) / 0.5), k=j))
    return out


def wisp(fig, m, k):
    """Le filet de fumée qui monte encore de la bouche du canon."""
    e = env(k, 0, 0.2, 0.6, 1)
    if e <= 0.02:
        return ''
    pts = [(m[0] + 0.5, m[1] - 1.0), (m[0] + 1.8 + 1.2 * math.sin(k * 6), m[1] - 5 - 4 * k),
           (m[0] + 0.6 + 2.0 * math.sin(k * 6 + 1.5), m[1] - 10 - 7 * k), (m[0] + 2.4 + 2.4 * math.sin(k * 5 + 3), m[1] - 15 - 9 * k)]
    c = crpath(pts, 14)
    sh = taper(c, 0.5, 1.6 * e + 0.2, tip='round')
    return outlined([(sh, g_lin(fig, c[0], c[-1], [(0, SMOKE[2]), (1, SMOKE[0])]), 1)], ink=SINK, w=0.8, op=e)


# ======================================================================== 2) l'attaque : « Coup de canon »

def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        fuse(fig, ctx, t, *ATT_FUSE)
        M0, D0 = shot_at('attack')
        # l'éclair rond du coup à la bouche du canon
        if ATT_SHOT - 5 <= t <= ATT_SHOT + 130:
            e = env(t, ATT_SHOT - 5, ATT_SHOT + 10, ATT_SHOT + 45, ATT_SHOT + 130)
            fig.fx_front.append(flash(fig, add(M0, D0, 4.0 + 3 * e), 7.0 * e + 0.8, facing=ang_of(D0), op=e))
        # le boulet file vers la droite (une traînée d'eau de mer derrière lui) et sort du cadre
        if ATT_SHOT <= t <= ATT_SHOT + 260:
            k = (t - ATT_SHOT) / 1000.0
            x = M0[0] + 4 + 900 * k
            y = M0[1] + D0[1] / max(0.2, D0[0]) * 900 * k * 0.25 + 30 * k * k
            tail = [(x - 6 - 40 * min(1, k * 8), y - 0.6), (x - 3 - 20 * min(1, k * 8), y - 0.2), (x - 1.0, y)]
            fig.fx_front.append(stream(fig, tail, 0.3, 2.6, op=min(1, k * 30)))
            fig.fx_front.append(cannonball(fig, (x, y), 2.8))
        # la grosse fumée blanche : elle reste là où le coup est parti
        if ATT_SHOT + 10 <= t <= 1340:
            fig.fx_front += smoke_cloud(fig, M0, D0, t - ATT_SHOT - 10, 1340 - ATT_SHOT - 10, big=1.6)
        # la poussière aux talons (le recul)
        fig.fx_back += heel_dust(fig, t, ATT_SHOT + 30)
        # le filet de fumée qui monte encore du canon
        if 880 <= t <= 1340:
            fig.fx_front.append(wisp(fig, ctx['muzzle'], (t - 880) / 460.0))
    return f


# ======================================================================== 3) la spéciale : « Ricochet »

def ball_path(te):
    """La place du boulet (temps des effets, ms) : il part de la bouche, rase le sol jusqu'au premier rebond, puis fait
    deux petits bonds (des arcs) jusqu'au premier rang ennemi. Renvoie (point, direction) ou None."""
    M0, D0 = shot_at('special')
    pts = [(SP_SHOT, M0)] + [((ms), (x, GR - 3.0)) for x, ms, _ in BOUNCES]
    if te < SP_SHOT or te > BOUNCES[-1][1]:
        return None
    for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
        if ta <= te <= tb:
            k = (te - ta) / (tb - ta)
            x = pa[0] + (pb[0] - pa[0]) * k
            y = pa[1] + (pb[1] - pa[1]) * k
            if ta != SP_SHOT:
                y -= (9.0 if pb[0] < 250 else 12.0) * 4 * k * (1 - k)      # le bond
            return (x, y)
    return None


def water_ring(fig, M, D, r, ph, op=1.0, w=1.6):
    """L'eau de mer qui s'enroule autour de la bouche du canon : deux filets en anneau (vu de biais : une ellipse étroite
    le long de l'axe), qui tournent."""
    out = []
    a = math.atan2(D[1], D[0])
    ca, sa = math.cos(a), math.sin(a)
    for j in range(2):
        pts = []
        for i in range(11):
            th = ph + j * math.pi + i / 10 * math.pi * 1.25
            lx, ly = 0.35 * r * math.cos(th), r * math.sin(th)
            pts.append((M[0] + lx * ca - ly * sa, M[1] + lx * sa + ly * ca))
        out.append(stream(fig, pts, 0.3, w, op=op, light=True))
    return out


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        te = fx_time(t)
        back, front = [], []
        M0, D0 = shot_at('special')
        m = ctx['muzzle']
        # l'eau de mer monte du sol et s'enroule autour de la bouche du canon
        eg = env(t, 0, 200, SP_SHOT - 10, SP_SHOT + 30)
        if eg > 0:
            for j, (x0, sw) in enumerate(((m[0] + 4.0, 1), (m[0] + 11.0, -1))):
                top = add(m, (2.0 + 4.0 * j, -2.0 + 4.0 * j))
                k = min(1.0, t / 260.0)
                pts = [(x0, GR), (x0 + 3 * sw, GR - 8 * k), lerp((x0 + 2 * sw, GR - 14 * k), top, k * 0.6), lerp((x0, GR - 16), top, k)]
                back.append(stream(fig, pts, 0.6, 3.2 * eg, op=eg))
            front += water_ring(fig, m, ctx['muzzle_dir'], 7.2 + 1.0 * math.sin(t / 60.0), t / 90.0, op=eg, w=1.8)
            for j in range(3):
                ph = (t / 260.0 + j / 3) % 1.0
                front.append(drop(fig, m[0] + 3 + 6 * j, m[1] + 4 + 10 * ph, 0, 40, 0.8, op=eg * (1 - ph)))
        fuse(fig, ctx, t, *SP_FUSE)
        # BOUM : l'éclair, l'anneau d'eau qui éclate en couronne de gouttes
        if SP_SHOT - 5 <= t <= SP_SHOT + 160:
            e = env(t, SP_SHOT - 5, SP_SHOT + 10, SP_SHOT + 50, SP_SHOT + 160)
            front.append(flash(fig, add(M0, D0, 4.0 + 3 * e), 7.0 * e + 0.8, facing=ang_of(D0), op=e))
            k = (t - SP_SHOT) / 160.0
            for j in range(7):
                a = math.radians(-150 + 50 * j)
                v = (80 * math.cos(a) + 60, 80 * math.sin(a) - 20)
                p = ballistic(add(M0, D0, 3), v, 200, k * 0.25)
                front.append(drop(fig, p[0], p[1], v[0], v[1], 0.9 if j % 2 else 1.1, op=1 - k))
        # le boulet enveloppé d'eau, qui rase le sol et ricoche
        bp = ball_path(te)
        if bp:
            trail = [ball_path(max(SP_SHOT, te - 70 + 7 * i)) for i in range(11)]
            trail = [p for p in trail if p]
            if len(trail) > 3 and math.dist(trail[0], trail[-1]) > 2:
                front.append(stream(fig, trail, 0.4, 4.4))
                # le filet d'eau claire qui s'enroule autour de sa course
                hel = []
                for i, p in enumerate(trail):
                    q = trail[min(len(trail) - 1, i + 1)] if i < len(trail) - 1 else add(p, sub(p, trail[i - 1]))
                    d = norm(sub(q, p))
                    hel.append(add(p, (-d[1], d[0]), 3.2 * (i / (len(trail) - 1)) ** 0.7 * math.sin(te / 25.0 + i * 0.9)))
                front.append(outlined([(taper(crpath(hel, 18), 0.2, 1.2, tip='round'),
                                        g_lin(fig, hel[0], hel[-1], [(0, WATER[2]), (1, '#ffffff')]), 1)], w=0.9))
            front.append(cannonball(fig, bp, 3.2))
        # les gerbes à chaque rebond (la troisième, sur le premier rang, la plus grosse, avec sa colonne d'eau)
        for j, (X, ms, big) in enumerate(BOUNCES):
            ks = (te - ms) / (560.0 if j < 2 else 900.0)
            if 0 < ks < 1:
                b, fr = splash_crown(fig, X, ks, big, seed=j)
                if j == 2:
                    up = env(ks, 0, 0.12, 0.4, 0.75)
                    if up > 0:
                        hgt = 46 * up
                        wb = 20 * (0.7 + 0.3 * up)
                        back.append(column(fig, X, GR - hgt, wb, wb * 0.6, 1.5 * math.sin(ks * 7), ks, op=min(1, up * 1.8)))
                back += b
                front += fr
        # la vague qui roule au sol vers la droite, depuis le troisième coup
        tw = te - FREEZE[0] - 60
        if 0 < tw < 900:
            k = tw / 900.0
            e = env(k, 0, 0.15, 0.6, 1)
            X = FOE_X - 4 + 40 * k
            front.append(mound(fig, X, 9.0 * e, 18, op=e))
            front.append(curl(fig, (X + 10, GR - 6.0 * e), (1, -0.3), 3.2 * e + 0.4, 240, 1, 1.6 * e, op=e,
                              tones=WATER[::-1][1:] + ['#ffffff']))
            for j in range(3):
                front.append(foam(fig, X - 8 + 7 * j, GR - 5.4 * e - 0.6 * j, 1.8 * e, op=e, seed=j))
        # l'écume s'étale au sol, puis disparaît
        ef = env(te, 1100, 1300, 1650, 2050)
        if ef > 0:
            for j, (dx, r) in enumerate(((-30, 2.0), (-14, 2.6), (2, 2.4))):
                front.append(foam(fig, FOE_X + dx - 3 * (te - 1100) / 800, GR - 1.0, r * ef, op=ef, seed=j))
        # la grosse fumée du coup, la poussière aux talons, le filet de fumée à la fin
        if SP_SHOT + 10 <= t <= 2070:
            front += smoke_cloud(fig, M0, D0, t - SP_SHOT - 10, 2070 - SP_SHOT - 10, big=1.7, seed=1)
        back += heel_dust(fig, t, SP_SHOT + 30, big=1.2)
        if 1550 <= t <= 2070:
            front.append(wisp(fig, m, (t - 1550) / 520.0))
        fig.fx_back += back
        fig.fx_front += front
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre (même fond que les héros)."""
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
    return im


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous lui (elle suit un peu le recul)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 + P.get('shift', 0) + 0.3 * P.get('lean', 0) - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 38 * k, fy - 2.8 * k, cx + 38 * k, fy + 2.8 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    seq = [('idle', 2 * IDLE_T + 0.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.1), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
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
    return B.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    job = {'w': w, 'h': h, 'frames': []}
    for i, svg in enumerate(frames_svg):
        p = os.path.join(TMP, '%s%04d.svg' % (prefix, i))
        open(p, 'w').write(svg)
        job['frames'].append([p, os.path.join(TMP, '%s%04d.png' % (prefix, i))])
    jp = os.path.join(TMP, prefix + 'job.json')
    json.dump(job, open(jp, 'w'))
    subprocess.run(['node', os.path.join(B.HEROS, 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def compose(pngs, Ps, w, h, view):
    bg = background(w, h, view)
    for p, P in zip(pngs, Ps):
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view, P))
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)


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
        moments = [0.4, 1.2, a_s + 0.3, a_s + 0.47, a_s + 0.5, a_s + 0.6, a_s + 0.75, a_s + 1.0,
                   s_s + 0.2, s_s + 0.4, s_s + 0.49, s_s + 0.6, s_s + 0.68, s_s + 0.8, s_s + 0.95, s_s + 1.1,
                   s_s + 1.3, s_s + 1.5, s_s + 1.8, s_s + 2.0]
        args = [a for a in sys.argv[1:] if a not in ('--planche',)]
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, [r[1] for r in res], 640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = Image.open(p)
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255))
            sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r[0] for r in res], VW, VH, 'a')
    compose(pngs, [r[1] for r in res], VW, VH, VIEW)
    for i, p in enumerate(pngs):
        os.replace(p, os.path.join(TMP, 'v%04d.png' % i))
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
