# Barzul vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/barzul/build.py)
# — pose (le crâneur qui tangue), attaque de base « Coup de pistolet », attaque spéciale « Bordée ! » — dans le style
# lisse de l'interface, à 24 images par seconde (même méthode que Kael, Myrr, Kesha : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/barzul/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/barzul/
#   python3 refonte-graphique/ui-moderne/heros/barzul/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (barzul.py) est fait de morceaux ; chaque image le redessine dans une POSE : le haut du corps
# tangue depuis les hanches comme sur le pont d'un navire (les bottes restent à plat), le souffle soulève le buste, la
# tête suit avec un temps de retard ; plume, queue de cheval, basques, pans de l'écharpe et lame qui pend suivent avec
# plus de retard (ils ne font que se balancer). Le bras tendu tourne autour de l'épaule (recul), le pistolet tourne
# dans la main puis autour de l'index (la main s'ouvre, seul l'index le tient) ; le bras proche est placé par
# cinématique inverse depuis le poignet (le coude tourne sur un arc, rien ne se décroche), la lame suit le poing.
# Les poses clés et les durées reprennent celles du pixel art.
# Effets (formes rondes et courbes, dégradés, un contour, aucun flou) : étincelle de la batterie, éclair du coup,
# balle, bouffées de fumée blanche qui s'enroulent en volutes, traînée d'acier du pistolet qui tourne ; pour la
# spéciale : éclat qui court sur la lame, canons du navire qui tonnent hors du cadre (éclairs, gros nuages de fumée),
# trois boulets de fonte enveloppés d'eau de mer (traînée qui s'enroule, gouttes) qui passent en arc au-dessus de lui
# et s'abattent sur l'ennemi en gerbes d'eau en couronne (l'eau : mêmes outils et mêmes bleus que Kesha et Ilian).
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
import barzul as B  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, lock, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of, taper, crpath  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'barzul')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-barzul-corr'
TMP = os.environ.get('BARZUL_TMP', os.path.join(DBG, '_images'))
FPS = 24
VIEW = (-48, -60, 330.0, 185.625)    # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = B.GRD
FOE_X = 214.0                        # l'ennemi (milieu)

WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']   # l'eau (celle de Kesha et d'Ilian)
WINK = '#0c1846'                     # le contour de l'eau
SMOKE = ['#ffffff', '#f4f2f8', '#dedcea', '#b8b6d0', '#8e8cae']               # la fumée de poudre (jamais de noir)
SINK = '#3a3660'                     # le contour de la fumée
FIRE = ['#fffce4', '#ffe46e', '#ffa03c', '#e0583a']                           # le feu de la poudre
FINK = '#6a1a14'
IRON = ['#d0d4ea', '#73769a', '#3e3a58', '#241e36']                           # les boulets de fonte
STEELFX = ['#f4f8ff', '#c4d0ea', '#8494bc']


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


# les réglages animés (voir barzul.py) ; b : souffle en plus ; nwx / nwy : le poignet proche
BASE = dict(lean=0.0, headx=0.0, heady=0.0, tilt=0.0, pl=0.0, q=0.0, cl=0.0, bl=0.0, sq=0.0, cri=0.0, aim=0.0, back=0.0,
            ptilt=0.0, spin=0.0, fired=0.0, open=0.0, nwx=B.NW0[0], nwy=B.NW0[1], sang=B.SANG0, b=0.0, glint=0.0)
NUM = list(BASE)
MI = dict(nw=(38.6, 57.0), sang=245.0)          # il tire le sabre vers le haut, devant l'épaule (la lame déjà debout)
LEVE = dict(nw=(34.6, 42.0), sang=255.0)        # le sabre dressé au ciel
FEU = dict(nw=(34.6, 39.4), sang=258.0)         # « Feu ! » : le poing monte encore


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'nw':
            d['nwx'], d['nwy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Coup de pistolet » : il vise (penché sur son bras, la tête au-dessus du canon, l'œil plissé)
# et tient. Le chien s'abat : une étincelle jaillit de la batterie. Le coup part : éclair rond à la bouche du canon, la
# balle file et sort du cadre ; le recul relève le pistolet et ramène la main, le buste et la tête reculent. Une
# grosse bouffée de fumée blanche reste là où le coup est parti : elle gonfle, monte, s'enroule en volutes et se défait.
# Le pistolet, relevé par le recul, continue sa course : la main s'ouvre et il fait un tour complet autour de l'index
# (canon en haut, en arrière, en bas — une traînée d'acier en arc) ; il le rattrape en joue, en crâneur (menton levé),
# un filet de fumée monte encore du canon, le pouce réarme le chien.
ATTACK = [
    (0, {}),
    (110, dict(lean=0.8, head=(0.9, 0.3), sq=1, pl=-0.8, q=0.8)),
    (340, dict(lean=0.8, head=(0.9, 0.3), sq=1, pl=-0.6, q=0.8, cl=0.6)),
    (370, dict(lean=0.8, head=(0.9, 0.3), sq=1, pl=-0.3, q=0.8, cl=0.6, fired=1)),
    (400, dict(lean=0.3, head=(0.3, 0.1), sq=1, pl=0.4, q=0.4, cl=0.3, fired=1, aim=-3.5, back=1.6, ptilt=-14)),
    (470, dict(lean=-0.8, head=(-0.8, 0.0), sq=0.5, pl=1.6, q=-0.6, cl=-0.6, fired=1, aim=-7, back=1.0, ptilt=-30, bl=0.6)),
    (530, dict(lean=-0.8, head=(-0.8, 0.0), pl=1.8, q=-0.8, cl=-0.8, fired=1, aim=-6, back=0.6, ptilt=-30, open=1, spin=-40, bl=0.8)),
    (580, dict(lean=-0.3, head=(-0.3, 0.0), pl=1.2, q=-0.8, cl=-0.6, fired=1, aim=-4, back=0.3, ptilt=-20, open=1, spin=-140)),
    (630, dict(lean=0.0, head=(0.0, 0.0), pl=0.4, q=-0.2, cl=0.0, fired=1, aim=-2, ptilt=-8, open=1, spin=-245, bl=-0.6)),
    (680, dict(lean=0.0, head=(0.0, 0.6), pl=-0.6, q=0.6, cl=0.6, fired=1, aim=1.6, ptilt=0, open=0.4, spin=-352, bl=-0.8)),
    (720, dict(lean=0.0, head=(0.0, 0.5), pl=-0.9, q=0.9, cl=0.8, fired=1, aim=1.2, open=0, spin=-360, bl=-0.6)),
    (850, dict(lean=0.0, head=(0.0, -0.9), b=0.6, pl=-0.6, q=0.9, cl=0.6, fired=1, spin=-360, tilt=-2.5)),
    (940, dict(lean=0.0, head=(0.0, -0.8), b=0.6, pl=-0.2, q=0.5, cl=0.3, fired=0, spin=-360, tilt=-2.5)),
    (1110, dict(spin=-360)),
]
ATT_SPARK = 355       # le chien s'abat : étincelle
ATT_SHOT = 400        # le coup part
ATT_SPIN = (520, 700)  # le pistolet tourne autour de l'index

# 3) La spéciale « Bordée ! » : le capitaine tire son sabre vers le haut et le dresse au ciel, la poitrine gonflée, le
# menton levé ; il crie « Feu ! » (la bouche s'ouvre, le poing monte d'un coup, un éclat court sur la lame). Derrière
# lui, hors du cadre, les canons de son navire tonnent l'un après l'autre (trois éclairs au bord gauche, trois gros
# nuages de fumée blanche). Trois boulets de fonte enveloppés d'eau de mer passent en arc au-dessus de sa tête et
# s'abattent sur l'ennemi : à chaque coup une gerbe d'eau en couronne jaillit du sol ; le troisième, le plus gros coup :
# arrêt sur l'image. Les gerbes retombent en pluie, l'écume s'étale ; il rit, puis rabaisse son sabre et se remet en joue.
SPECIAL = [
    (0, {}),
    (90, dict(MI, lean=-0.8, pl=1.2, q=-0.8, cl=-0.8, bl=0)),
    (200, dict(LEVE, b=1, lean=-0.8, head=(0, -0.8), pl=1.8, q=-0.8, cl=-0.6)),
    (280, dict(FEU, b=1, lean=-0.8, head=(0, -1.0), cri=1, pl=1.2, cl=-0.2, glint=0.1)),
    (440, dict(FEU, b=1, lean=-0.8, head=(0, -1.0), cri=1, pl=0.4, q=0.2, cl=0.4, glint=1.0)),
    (530, dict(FEU, b=1, lean=-0.8, head=(0, -1.0), cri=1, pl=-0.6, q=0.8, cl=0.8, glint=1.0)),
    (600, dict(FEU, b=1, lean=-0.8, head=(0, -1.0), cri=0.7, pl=0, q=0.8, cl=0.8)),
    (700, dict(LEVE, b=1, lean=0, head=(0, -0.8), cri=0, pl=0.8, q=0, cl=0)),
    (810, dict(LEVE, b=1, lean=0, head=(0, 0), pl=0.4, q=0)),
    (900, dict(LEVE, b=1, lean=0.8, head=(0.4, 0), pl=-0.8, q=0.8, cl=-0.8)),
    (990, dict(LEVE, b=1, lean=0.9, head=(0.4, -1.0), cri=1, pl=-0.9, q=0.9, cl=-0.9)),
    (1240, dict(LEVE, b=1, lean=0.8, head=(0.3, -1.0), cri=1, pl=-0.8, q=0.9, cl=-0.8)),
    (1300, dict(LEVE, b=0, lean=0, head=(0, 0.2), cri=0.3, pl=0, q=0)),
    (1370, dict(LEVE, b=1, lean=0, head=(0, -0.9), cri=0.9, pl=0.9, q=-0.7)),
    (1440, dict(LEVE, b=0.5, lean=0, head=(0, 0.1), cri=0.4, pl=0.5, q=-0.4)),
    (1520, dict(MI, b=0, lean=0, head=(0, 0), pl=1.0, q=-0.9, cl=-0.8)),
    (1630, dict(head=(0, 0.8), pl=0, q=0, cl=0, bl=-1.0)),
    (1770, dict(head=(0, 0), pl=-0.8, q=0.8, cl=0.8, bl=1.0)),
    (1920, {}),
]
SG_FLIP = (60, 1560)                 # le sabre levé : la lame se courbe vers l'arrière, le fil vers l'ennemi
BOOMS = [(-52.0, 42.0), (-46.0, 22.0), (-56.0, 62.0)]   # les bouches des canons du navire, hors du cadre à gauche
BOOM_AT = [460, 530, 600]
FLIGHT = 350                         # le vol d'un boulet (ms)
IMPACT_X = [FOE_X - 26.0, FOE_X + 26.0, FOE_X]
IMPACT_BIG = [1.35, 1.3, 2.1]
APEX = [96.0, 104.0, 110.0]         # la hauteur de l'arc au-dessus de la corde
FREEZE = (990, 1240)                 # le troisième coup : arrêt sur l'image (les effets ralentissent)


def fx_time(t):
    """Le temps des effets de la spéciale : il ralentit pendant l'arrêt sur l'image."""
    a, b = FREEZE
    if t <= a:
        return t
    if t <= b:
        return a + (t - a) * 0.22
    return a + (b - a) * 0.22 + (t - b)


# ======================================================================== la pose (2 s… le crâneur qui tangue)
IDLE_T = 1.4


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u - 0.3)
    d = dict(lean=0.85 * math.sin(u), headx=0.35 * math.sin(u - 0.7), heady=-0.35 * (0.5 - 0.5 * math.cos(u - 0.9)),
             pl=-1.1 * math.sin(u - 1.3), q=-0.9 * math.sin(u - 1.45), cl=-0.75 * math.sin(u - 1.2),
             bl=-0.7 * math.sin(u - 1.6), tilt=0.5 * math.sin(u - 1.0))
    return d, br


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : pose qui tangue (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0
    keys = None
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
    br = br * w + P['b']
    out = dict(breath=min(1.2, br), lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'], pl=P['pl'], q=P['q'],
               cl=P['cl'], bl=P['bl'], sq=max(0, P['sq']), cri=max(0, P['cri']), aim=P['aim'], back=P['back'],
               ptilt=P['ptilt'], spin=P['spin'], fired=max(0, min(1, P['fired'])), open=max(0, min(1, P['open'])),
               nw=(P['nwx'], P['nwy']), sang=P['sang'], glint=max(0, min(1, P['glint'])) if action == 'special' else 0.0)
    out['sg'] = -1 if (action == 'special' and SG_FLIP[0] <= tl < SG_FLIP[1]) else 1
    # un clignement de temps en temps (pas pendant l'attaque, où il plisse l'œil)
    out['blink'] = 1.0 if (w > 0.95 and 2.10 <= (T % 3.6) < 2.19) else 0.0
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
    PET = ((-7, -126, 15, -40, 3.6), (-3, -104, 22, -22, 4.2), (3, -78, 21, 22, 4.2), (7, -56, 15, 40, 3.6), (0, -90, 13, 0, 3.0))
    if seed % 2:
        PET = tuple((dx, a + 6, L * 0.92, bd, w) for dx, a, L, bd, w in PET)
    for j, (dx, ang, L, bd, w) in enumerate(PET):
        L_ = 1.45 * L * big * (0.4 + 0.6 * min(1, k * 2.2)) * (1 - 0.35 * max(0, k - 0.5) * 2)
        (out_b if j in (0, 3, 4) else out_f).append(sheet(fig, (X + dx * big, GR + 0.2), ang, L_, bd, w * big ** 0.8,
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


# ======================================================================== 2) l'attaque : le coup de pistolet

SHOT = {}                              # là où le coup est parti (la bouche du canon à l'instant du coup)


def shot_at():
    if 'm' not in SHOT:
        P = pose_at(0.0, 'attack', -ATT_SHOT / 1000.0)
        ctx = B.build(pose=P).ctx
        SHOT['m'] = ctx['muzzle']
        SHOT['d'] = ctx['muzzle_dir']
    return SHOT['m'], SHOT['d']


# la fumée du coup : des bouffées poussées vers l'avant qui ralentissent, gonflent, montent et se défont ;
# (décalage final depuis la bouche, rayon final, retard en ms)
SMOKE_PUFFS = [(5.0, -1.0, 3.6, 0), (11.0, -2.6, 4.4, 15), (18.0, -4.0, 4.0, 30), (24.0, -6.4, 3.2, 45), (2.0, -3.6, 2.6, 25)]
SMOKE_CURLS = [((26.0, -8.0), (1, -0.6), 3.0, 1), ((0.0, -6.0), (-0.6, -1), 2.4, -1)]


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        # l'étincelle de la batterie, quand le chien s'abat
        if ATT_SPARK - 10 <= t <= ATT_SPARK + 70:
            e = env(t, ATT_SPARK - 10, ATT_SPARK + 5, ATT_SPARK + 25, ATT_SPARK + 70)
            p = ctx['pan']
            fig.fx_front.append(spark(fig, (p[0] + 0.5, p[1] - 1.0), 3.2 * e + 0.6, op=e, rot=12))
            fig.fx_front.append(spark(fig, (p[0] + 2.6, p[1] - 3.2), 1.6 * e, op=e, rot=-20))
        M0, D0 = shot_at()
        # l'éclair du coup à la bouche du canon
        if ATT_SHOT - 5 <= t <= ATT_SHOT + 110:
            e = env(t, ATT_SHOT - 5, ATT_SHOT + 10, ATT_SHOT + 35, ATT_SHOT + 110)
            c = add(M0, D0, 3.2 + 2 * e)
            fig.fx_front.append(flash(fig, c, 4.6 * e + 0.6, facing=ang_of(D0), op=e))
        # la balle file et sort du cadre (une courte traînée pâle)
        if ATT_SHOT <= t <= ATT_SHOT + 160:
            k = (t - ATT_SHOT) / 1000.0
            x = M0[0] + 6 + 1100 * k
            y = M0[1] - 6 * k
            tail = [(x - 14 - 30 * min(1, k * 8), y + 0.3), (x - 7, y + 0.15), (x, y)]
            fig.fx_front.append('<path d="%s" fill="%s" opacity="0.75"/>' % (taper(tail, 0.2, 1.4, tip='round').d(), STEELFX[1]))
            fig.fx_front.append(outlined([(ellipse(x, y, 1.15, 1.05), IRON[1], 1), (ellipse(x + 0.35, y - 0.35, 0.4, 0.32), IRON[0], 1, 'n')],
                                         ink=IRON[3], w=0.9))
        # la bouffée de fumée : elle reste là où le coup est parti
        if ATT_SHOT + 20 <= t <= 1110:
            k = (t - ATT_SHOT - 20) / (1110 - ATT_SHOT - 20)
            for j, (dx, dy, r, dl) in enumerate(SMOKE_PUFFS):
                kk = max(0.0, min(1.0, (t - ATT_SHOT - 20 - dl) / (1110 - ATT_SHOT - 20 - dl)))
                if kk <= 0:
                    continue
                go = 1 - (1 - min(1, kk * 2.6)) ** 3                    # poussée vers l'avant, qui ralentit
                rise = kk * 4.5
                c = (M0[0] + dx * go + 2.5 * kk, M0[1] + dy * go - rise)
                rr = r * (0.35 + 0.65 * go) * (1 + 0.35 * kk) * (1 - smooth((kk - 0.62) / 0.38) * 0.75)
                op = 1 - smooth((kk - 0.55) / 0.45)
                fig.fx_front.append(smoke(fig, c[0], c[1], rr, op=op, k=j))
            for j, ((dx, dy), d, r0, s) in enumerate(SMOKE_CURLS):
                e = env(k, 0.18, 0.35, 0.6, 0.9)
                if e > 0:
                    p = (M0[0] + dx + 2 * k, M0[1] + dy - 4 * k)
                    fig.fx_front.append(curl(fig, p, d, r0 * (0.6 + 0.4 * e), 200 + 120 * e, s, 1.4 * e, op=e))
        # la traînée d'acier du pistolet qui tourne autour de l'index
        if ATT_SPIN[0] <= t <= ATT_SPIN[1] + 40:
            P = ctx['P']
            pv = ctx['pivot']
            R = math.dist(B.PV, (124.4, 55.0))
            a_now = ang_of(ctx['muzzle_dir'])
            e = env(t, ATT_SPIN[0], ATT_SPIN[0] + 30, ATT_SPIN[1] - 20, ATT_SPIN[1] + 40)
            a0 = a_now + 95 * e
            n = 22
            pts, ws = [], []
            off = math.degrees(math.atan2(55.0 - B.PV[1], 124.4 - B.PV[0]))      # la bouche, vue du pivot
            for i in range(n + 1):
                tt = i / n
                a = math.radians(a0 + (a_now - a0) * tt + off)
                pts.append((pv[0] + R * math.cos(a), pv[1] + R * math.sin(a)))
                ws.append(max(0.05, 3.2 * e * tt ** 1.3))
            if e > 0.05:
                band = stroke_shape(pts, ws)
                gr = g_lin(fig, pts[0], pts[-1], [(0, STEELFX[2], 0), (0.6, STEELFX[1], 0.6 * e), (1, STEELFX[0], 0.9 * e)])
                fig.fx_back.append('<path d="%s" fill="%s"/>' % (band.d(), gr))
        # le filet de fumée qui monte encore du canon (en crâneur)
        if 740 <= t <= 1110:
            k = (t - 740) / 370.0
            m = ctx['muzzle']
            e = env(k, 0, 0.2, 0.6, 1)
            pts = [(m[0] + 0.5, m[1] - 1.0), (m[0] + 1.8 + 1.2 * math.sin(k * 6), m[1] - 4 - 4 * k),
                   (m[0] + 0.6 + 2.0 * math.sin(k * 6 + 1.5), m[1] - 8 - 7 * k), (m[0] + 2.4 + 2.4 * math.sin(k * 5 + 3), m[1] - 12 - 9 * k)]
            c = crpath(pts, 14)
            sh = taper(c, 0.4, 1.3 * e + 0.2, tip='round')
            fig.fx_front.append(outlined([(sh, g_lin(fig, c[0], c[-1], [(0, SMOKE[2]), (1, SMOKE[0])]), 1)], ink=SINK, w=0.8, op=e))
    return f


# ======================================================================== 3) la spéciale : « Bordée ! »

def ball_pos(j, k):
    A = BOOMS[j]
    Bp = (IMPACT_X[j], GR - 2.0)
    x = A[0] + (Bp[0] - A[0]) * k
    y = A[1] + (Bp[1] - A[1]) * k - APEX[j] * 4 * k * (1 - k)
    return (x, y)


def cannonball(fig, c, r, v):
    """Un boulet de fonte enveloppé d'eau de mer : la traînée d'eau, un filet clair qui s'enroule autour de sa course."""
    return outlined([(ellipse(c[0], c[1], r, r), g_rad(fig, (c[0] + r * 0.3, c[1] - r * 0.35), r * 1.4,
                                                        [(0, IRON[0]), (0.35, IRON[1]), (0.75, IRON[2]), (1, IRON[3])]), 1),
                     (ellipse(c[0] + r * 0.35, c[1] - r * 0.4, r * 0.3, r * 0.22, -30), '#ffffff', 0.85, 'n')], ink='#160f26', w=1.2)


def fx_ball_flight(fig, j, k):
    out = []
    r = 2.6 if j < 2 else 3.4
    c = ball_pos(j, k)
    # la traînée d'eau (derrière le boulet, le long de sa course)
    k0 = max(0.0, k - 0.32)
    pts = [ball_pos(j, k0 + (k - k0) * i / 10) for i in range(11)]
    if k - k0 > 0.02:
        out.append(stream(fig, pts, 0.4, r * 1.9))
        # le filet d'eau claire qui s'enroule autour de la course
        n = 16
        hel = []
        for i in range(n + 1):
            kk = k0 + (k - k0) * i / n
            p = ball_pos(j, kk)
            q = ball_pos(j, kk + 0.002)
            d = norm(sub(q, p))
            nr = (-d[1], d[0])
            amp = r * 1.3 * (i / n) ** 0.7
            hel.append(add(p, nr, amp * math.sin(kk * 60 + j)))
        sh = taper(crpath(hel, 18), 0.2, 1.1, tip='round')
        out.append(outlined([(sh, g_lin(fig, hel[0], hel[-1], [(0, WATER[2]), (1, '#ffffff')]), 1)], w=0.9))
        # des gouttes qui s'en détachent
        for i in range(3):
            kk = k - 0.08 - 0.07 * i
            if kk > 0:
                p = ball_pos(j, kk)
                out.append(drop(fig, p[0] - 1.5 + 2.5 * i, p[1] + 3 + 2.4 * i + 6 * (k - kk), 0, 40, 0.8 if i else 1.0,
                                op=1 - (k - kk) * 3))
    q = ball_pos(j, min(1, k + 0.01))
    out.append(cannonball(fig, c, r, sub(q, c)))
    return out


def fx_boom(fig, j, t):
    """Un canon du navire tonne hors du cadre : un éclair au bord, un gros nuage de fumée blanche qui roule."""
    out = []
    A = BOOMS[j]
    e = env(t, 0, 20, 60, 150)
    if e > 0:
        out.append(flash(fig, (A[0] + 4, A[1]), 7 * e + 1, facing=-25, op=e))
    if t > 10:
        k = min(1.0, (t - 10) / 1100.0)
        for i, (dx, dy, r, dl) in enumerate(((8, 0, 7, 0), (17, -5, 6, 30), (6, -10, 5.4, 60), (22, 3, 4.6, 40), (13, -15, 4.2, 90))):
            kk = max(0.0, min(1.0, (t - 10 - dl) / 1100.0))
            if kk <= 0:
                continue
            go = 1 - (1 - min(1, kk * 3.5)) ** 3
            rr = r * (0.4 + 0.6 * go) * (1 + 0.3 * kk) * (1 - 0.7 * smooth((kk - 0.6) / 0.4))
            op = 1 - smooth((kk - 0.55) / 0.45)
            out.append(smoke(fig, A[0] + dx * go + 10 * kk, A[1] + dy * go - 10 * kk, rr, op=op, k=i + j))
    return out


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        te = fx_time(t)
        back, front = [], []
        # l'éclat qui court sur la lame : peint par le dessin (glint) ; une petite étoile à la pointe au « Feu ! »
        e = env(t, 380, 420, 460, 560)
        if e > 0:
            front.append(spark(fig, ctx['tip'], 3.4 * e, op=e, rot=10))
        # les canons tonnent
        for j in range(3):
            tb = te - BOOM_AT[j]
            if 0 <= tb <= 1250:
                back += fx_boom(fig, j, tb)
        # les boulets passent en arc au-dessus de lui
        for j in range(3):
            k = (te - BOOM_AT[j] - 20) / FLIGHT
            if 0 <= k <= 1:
                front += fx_ball_flight(fig, j, k)
        # les gerbes
        for j in range(3):
            ks = (te - BOOM_AT[j] - 20 - FLIGHT) / (640.0 if j < 2 else 820.0)
            if 0 < ks < 1:
                b, fr = splash_crown(fig, IMPACT_X[j], ks, IMPACT_BIG[j], seed=j)
                # le corps de la gerbe : une colonne d'eau qui jaillit et s'effondre (plus haute au troisième coup)
                up = env(ks, 0, 0.14, 0.4, 0.75)
                if up > 0:
                    hgt = (26 if j < 2 else 44) * up
                    wb = (12 if j < 2 else 20) * (0.7 + 0.3 * up)
                    back.append(column(fig, IMPACT_X[j], GR - hgt, wb, wb * 0.6, 1.5 * math.sin(ks * 7 + j), ks, op=min(1, up * 1.8)))
                back += b
                front += fr
                # le bouillon d'écume et un peu de fumée grise à l'impact
                eb = env(ks, 0, 0.08, 0.3, 0.6)
                if eb > 0:
                    front.append(smoke(fig, IMPACT_X[j] - 4, GR - 6 - 10 * ks, 3.2 * IMPACT_BIG[j] * eb, op=eb * 0.8, k=j))
        # l'écume s'étale au sol en volutes, puis disparaît
        ef = env(te, 1050, 1250, 1500, 1820)
        if ef > 0:
            for j, (dx, r) in enumerate(((-30, 2.0), (-14, 2.6), (2, 2.4), (18, 2.8), (32, 2.0))):
                front.append(foam(fig, FOE_X + dx + 4 * (te - 1050) / 800 * (1 if dx > 0 else -1), GR - 1.0, r * ef, op=ef, seed=j))
            front.append(mound(fig, FOE_X, 3.2 * ef, 36, op=ef, foamy=0.7))
            for s_, x_ in ((-1, FOE_X - 40), (1, FOE_X + 40)):
                front.append(curl(fig, (x_, GR - 1.2), (s_, -0.2), 2.2 * ef + 0.4, 240, -s_, 1.1 * ef, op=ef, tones=WATER[::-1][1:] + ['#ffffff']))
        fig.fx_back += back
        fig.fx_front += front
    return f


def fx_idle(T):
    """Au repos : un rien de reflet qui passe sur l'or (rien d'autre)."""
    return lambda fig, ctx: None


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
    glow_ = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow_).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow_.filter(ImageFilter.GaussianBlur(h * 0.12)))
    return im


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre au sol sous lui."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (66 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 24 * k, fy - 2.8 * k, cx + 24 * k, fy + 2.8 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    seq = [('idle', 2 * IDLE_T + 0.2), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.1), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.5)]
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
    subprocess.run(['node', os.path.join(HERE, '..', 'rendu-lot.cjs'), jp], check=True)
    return [f_[1] for f_ in job['frames']]


def find_offset(sprite, frame):
    """Où le dessin pixel art (image 128 × 120, pieds en (64, 116)) est posé dans une image d'animation."""
    import numpy as np
    s = np.asarray(sprite.convert('RGBA')).astype(int)
    f_ = np.asarray(frame.convert('RGBA')).astype(int)
    ys, xs = np.nonzero(s[:, :, 3] > 200)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = s[y0:y1, x0:x1]
    mask = s[:, :, 3] > 200
    best = None
    for oy in range(0, f_.shape[0] - s.shape[0] + 1):
        for ox in range(0, f_.shape[1] - s.shape[1] + 1):
            sub_ = f_[oy:oy + s.shape[0], ox:ox + s.shape[1], :3]
            dd = np.abs(sub_ - s[:, :, :3])[mask].mean()
            if best is None or dd < best[0]:
                best = (dd, ox, oy)
    return best[1] - x0, best[2] - y0


def pixel_frames(name):
    """Les images d'une animation pixel art (GIF de contrôle, fond clair retiré), à l'échelle 1, et la place du
    point « sol » (64, 116) du dessin dans ces images."""
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd'))
    import hd
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-barzul-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('barzul'), 0), 'RGBA')
    ref = out[0][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat de son clan, le pixel art à gauche et le vectoriel à
    droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'barzul.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (150, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.4), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (B.FEET[0] - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
    pngs = render([frame_svg(i / FPS, segs, view=view, ow=1.25)[0] for i in range(n)], PW, PH, 'b')
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
        layer.paste(big, (round(feet[0] - (ox + 64) * SC), round(feet[1] - (oy + 116) * SC)), big)
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


def compose(pngs, w, h, view):
    bg = background(w, h, view)
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view))
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
        moments = [0.35, 1.0, a_s + 0.2, a_s + 0.36, a_s + 0.41, a_s + 0.48, a_s + 0.56, a_s + 0.61, a_s + 0.66, a_s + 0.85,
                   s_s + 0.05, s_s + 0.2, s_s + 0.42, s_s + 0.62, s_s + 0.75, s_s + 0.9, s_s + 1.0, s_s + 1.15, s_s + 1.4,
                   s_s + 1.5, s_s + 1.6]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, 640, 360, VIEW)
        cols = 4
        sheet = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = Image.open(p)
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255))
            sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(DBG, exist_ok=True)
        dst = os.path.join(DBG, 'planche.png')
        sheet.save(dst)
        print('planche :', dst, 'attaque à', a_s, 'spéciale à', s_s)
        shutil.rmtree(TMP)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    res = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([r[0] for r in res], VW, VH, 'a')
    compose(pngs, VW, VH, VIEW)
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
