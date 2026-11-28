# Solenn vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/solenn/build.py) —
# souffle bourru de nain, attaque de base « Coup de masse », attaque spéciale « Rempart du nain » (sort d'équipe) — dans
# le style lisse de l'interface, à 24 images par seconde (même méthode que Kael, Mira et Taurok : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/solenn/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/solenn/
#   python3 refonte-graphique/ui-moderne/heros/solenn/anim.py --planche [instants…]   # une planche d'images clés (brouillon)
#
# Méthode : le dessin (solenn.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et
# se penche depuis les hanches, la tête suit avec un léger retard, les flammes de la crinière ondulent à la pointe, la
# barbe et les pinceaux des tresses se balancent en retard ; la masse est tenue par le poing (point de prise et angle),
# le bras proche est placé par cinématique inverse depuis le poignet (épaule, coude, poignet : les vraies jointures,
# la cubitière suit le coude) ; le bouclier suit le buste. C'est un nain : court et lourd — préparations brèves mais
# tenues, coups secs, il se plante sur ses jambes. Les poses clés et les durées reprennent celles du pixel art,
# reliées par des courbes douces sans dépassement.
# Effets de la terre (mêmes formes et mêmes tons que Taurok) : poussière ocre, mottes et éclats de roche, fissure et
# lueur dorée, étincelles de fer, traînée de la masse ; la spéciale (sort d'équipe : tout naît sur lui et s'étend EN
# CERCLE autour de lui) : l'emblème du bouclier s'allume, il lève la masse et tape du pied, une veine d'or court en
# anneau au sol et un rempart de dalles de pierre jaillit tout autour de lui, s'illumine d'or (lancement), se rassoit ;
# puis le défi : la masse frappe la face du bouclier, il crie, une lueur rouge douce épouse sa silhouette. Aucun flou
# SVG ; jamais de rayons droits répétés.
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
import solenn as M  # noqa: E402
from atelier import sm, ribbon, ellipse, rpoly, mapp, mchain, mT, mR, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of  # noqa: E402

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'solenn')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-solenn'
TMP = os.path.join(DBG, '_images')
FPS = 24
VIEW = (-76, -30, 280.0, 157.5)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = M.GRD
E = ['#fff6ce', '#ffd45c', '#e09638', '#c8a070', '#8e664a', '#5e404a', '#3e2a36']   # la lueur et la roche de la terre
EINK = '#3e2a36'                     # le contour de la terre et des roches
SINK = '#4a3e5e'                     # le contour du souffle
RING_C = (64.0, GR + 1.0)            # le centre de l'anneau de pierres (sous lui)
RING_RX, RING_RY = 58.0, 8.5


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


# les réglages animés (voir solenn.py) ; gx, gy : le point de prise de la masse ; shx, shy : le bouclier ;
# lnx, lny : le pied proche (le genou monte, il tape du pied)
BASE = dict(lean=0.0, crouch=0.0, headx=0.0, heady=0.0, tilt=0.0, mouth=0.0, fury=0.0, flare=0.0, bd=0.0,
            gx=M.G0[0], gy=M.G0[1], ang=M.ANG0, shx=0.0, shy=0.0, sht=0.0, glow=0.0, stretch=0.0, lnx=0.0, lny=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'G':
            d['gx'], d['gy'] = v
        elif key == 'sh':
            d['shx'], d['shy'] = v
        elif key == 'leg':
            d['lnx'], d['lny'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Coup de masse » (pixel : ATTAQUE, 1,11 s) : un coup de nain, court, sec, de tout son poids. Il
# arme la masse derrière la tête (la boule tombe dans son dos), le bouclier se lève d'un cran, le talon proche se lève
# — tenu, les yeux s'allument. Puis il abat la masse par-dessus l'épaule en tapant du pied : la boule frappe droit
# devant, à hauteur de poitrine, par-dessus le bouclier (le bouclier recule, le buste se jette en avant). Arrêt sur
# l'image : éclat d'or, gerbe d'étincelles de fer, le pied fend la terre et fait sauter des mottes. La masse rebondit,
# revient en garde. Angles de la masse en degrés (y vers le bas : −90 = droit vers le ciel).
HITG = dict(G=(73.0, 66.0), ang=8, crouch=3.0, lean=4.0, sh=(-5.0, 2.0), head=(1.0, 2.0), tilt=2.0, bd=-1.0, mouth=0.35,
            fury=0.6)
ATTACK = [
    (0, {}),
    (100, dict(crouch=0.6)),
    (190, dict(G=(31.0, 41.0), ang=-120, crouch=1.0, lean=-1.0, sh=(1.0, -2.0), head=(0.0, 1.0), leg=(0.8, -1.2), bd=0.6)),
    (300, dict(G=(27.0, 44.0), ang=-158, crouch=1.0, lean=-2.0, sh=(2.0, -3.0), head=(-1.0, 1.0), tilt=-2.0, leg=(1.4, -2.2),
               flare=1.0, fury=1.0, bd=1.0)),
    (420, dict(G=(26.6, 44.4), ang=-160, crouch=1.1, lean=-2.2, sh=(2.0, -3.0), head=(-1.0, 1.0), tilt=-2.4, leg=(1.4, -2.4),
               flare=1.0, fury=1.0, bd=1.0)),
    (460, dict(G=(50.0, 38.0), ang=-62, crouch=1.0, lean=1.0, sh=(0.0, -2.0), head=(0.0, 0.0), leg=(1.0, -1.6), stretch=2.0,
               flare=0.6, fury=1.0, bd=0.0)),
    (500, dict(G=(70.0, 60.0), ang=-2, crouch=2.0, lean=3.0, sh=(-3.0, 0.0), head=(1.0, 1.0), stretch=2.0, fury=1.0, bd=-0.6)),
    (540, HITG),
    (710, dict(HITG, G=(73.0, 65.6), ang=7)),
    (810, dict(G=(70.0, 62.0), ang=-30, crouch=2.0, lean=3.0, sh=(-4.0, 1.0), head=(1.0, 1.0), bd=0.4, fury=0.3)),
    (920, dict(G=(46.0, 56.0), ang=-100, crouch=1.0, lean=1.0, sh=(-1.0, 0.0), head=(0.0, 1.0), bd=0.6)),
    (1050, dict(crouch=1.0, bd=-0.3)),
    (1180, {}),
]
ATT_BEHIND = (150, 445)   # la masse armée passe derrière la tête et le corps
ATT_SWING = (430, 540)    # la frappe (la traînée suit la boule)
ATT_HIT = 540             # l'impact (il tape du pied)

# 3) L'attaque spéciale « Rempart du nain » (pixel : SPECIALE, 1,92 s ; sort d'équipe : bouclier sur toute l'équipe,
# provocation). Il lève la masse droit au ciel, monte le genou (l'emblème du bouclier s'allume d'or, la poussière
# tourne à ses pieds, des cailloux se soulèvent) : tenu. Il TAPE DU PIED : une veine d'or court au sol en anneau autour
# de lui et un anneau de dalles de pierre en jaillit (elles dépassent un peu, puis se posent). LANCEMENT : le rempart
# dressé s'illumine d'or, des étincelles rondes scintillent au sommet des pierres, des grains d'or montent. Les dalles
# se rassoient. Le défi : il arme la masse au-dessus de la tête et l'abat sur la face de son bouclier (éclat, étincelles,
# le bouclier tremble), il crie, une lueur rouge douce épouse sa silhouette (elle gonfle puis s'éteint). Il revient.
RAISED = dict(G=(39.0, 27.0), ang=-96)
WINDP = dict(G=(42.0, 36.0), ang=-128, crouch=1.0, lean=-1.0, sh=(1.0, -1.0))
CLANG = dict(G=(64.0, 72.0), ang=-24, crouch=2.0, lean=2.0, sh=(2.0, -1.0), head=(1.0, 1.0), mouth=1.0, fury=1.0, bd=-0.8)
SPECIAL = [
    (0, {}),
    (90, dict(crouch=0.4)),
    (200, dict(G=(40.0, 33.0), ang=-93, lean=-1.0, leg=(0.8, -1.8), glow=1.0, sh=(0.0, -1.0), bd=0.5)),
    (380, dict(RAISED, crouch=-1.0, lean=-1.0, leg=(1.6, -5.0), glow=2.0, flare=1.0, head=(0.0, -1.0), sh=(1.0, -2.0), fury=1.0, bd=0.8)),
    (440, dict(RAISED, crouch=-1.0, lean=-1.0, leg=(1.6, -5.2), glow=2.0, flare=1.0, head=(0.0, -1.0), sh=(1.0, -2.0), fury=1.0, bd=0.8)),
    (500, dict(RAISED, crouch=3.0, glow=3.0, flare=1.0, head=(0.0, 1.0), fury=1.0, bd=-1.0)),
    (630, dict(RAISED, crouch=2.0, glow=3.0, flare=1.0, head=(0.0, 1.0), fury=1.0, bd=-0.4)),
    (700, dict(RAISED, crouch=1.0, glow=3.0, flare=1.0, sh=(0.0, -1.0), fury=1.0)),
    (840, dict(RAISED, crouch=1.0, glow=3.0, flare=1.0, sh=(0.0, -1.0), fury=1.0)),
    (940, dict(RAISED, crouch=1.0, glow=2.0, sh=(0.0, -1.0), fury=0.6)),
    (1010, dict(RAISED, crouch=1.0, glow=1.0, sh=(0.0, -1.0))),
    (1160, dict(WINDP, glow=1.0, bd=0.6)),
    (1210, dict(CLANG, glow=2.0, flare=1.0, sht=-3.0)),
    (1300, dict(CLANG, glow=1.4, flare=1.0, sht=2.0, sh=(1.0, -1.0))),
    (1380, dict(CLANG, glow=1.0, sht=0.0, sh=(1.0, -1.0), head=(1.0, 0.0))),
    (1500, dict(CLANG, G=(62.0, 68.0), ang=-34, glow=0.5, sh=(1.0, -1.0), head=(1.0, 0.0), mouth=0.6)),
    (1600, dict(G=(46.0, 56.0), ang=-100, crouch=1.0, lean=1.0, sh=(-1.0, 0.0), head=(0.0, 1.0), bd=0.5)),
    (1710, dict(crouch=1.0, bd=-0.3)),
    (1850, {}),
]
SP_GATHER = (90, 470)     # la poussière tourne, les cailloux se soulèvent
SP_STOMP = 500            # il tape du pied : la veine d'or, les dalles jaillissent
SP_LAUNCH = (700, 940)    # LANCEMENT : le rempart dressé s'illumine d'or
SP_SINK = (940, 1180)     # les dalles se rassoient
SP_CLANG = 1210           # la masse frappe le bouclier
SP_TAUNT = (1210, 1640)   # la lueur rouge du défi


# ======================================================================== la respiration (3 s)
IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (1,5 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : le signe gravé du bouclier (losange et pic de montagne) s'allume lentement d'or puis s'éteint, et
    les flammes de la crinière ondulent plus fort (deux vagues par boucle). Une pose partielle pour build() ; jouée
    au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(emb=0.85 * (0.5 - 0.5 * math.cos(u)), wv=1.2, sw=2 * u)


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    # la tête suit le souffle avec retard ; il se tasse un peu en expirant (il se campe) ; la boule de la masse penche
    # en retard sur le bras ; la barbe et les tresses se balancent (elles pendent)
    d = dict(heady=-0.3 * (0.5 - 0.5 * math.cos(u - 0.6)), tilt=0.3 * math.sin(u - 1.0), crouch=0.35 * (1 - br),
             ang=0.9 * math.sin(u - 0.9), bd=0.7 * math.sin(u - 1.5))
    return d, br


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) de la vidéo : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 120), max(0.0, (tl - (dur - 200)) / 200))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    br *= w
    behind = action == 'attack' and ATT_BEHIND[0] <= tl < ATT_BEHIND[1]
    sg = signe(T)                                  # le signe du repos : le bouclier s'allume (anim.signe)
    out = dict(breath=br, lean=P['lean'], crouch=P['crouch'], head=(P['headx'], P['heady']), tilt=P['tilt'],
               mouth=max(0.0, P['mouth']), fury=max(0.0, P['fury']), sw=sg['sw'], flare=P['flare'], wv=w * sg['wv'],
               bd=P['bd'], brd=0.8 * math.sin(2 * math.pi * T / IDLE_T - 2.0) + 0.6 * P['bd'],
               grip=(P['gx'], P['gy']), ang=P['ang'], sh=(P['shx'], P['shy']), sht=P['sht'],
               glow=max(0.0, P['glow']), emb=w * sg['emb'],
               stretch=P['stretch'], legn=(P['lnx'], min(0.0, P['lny'])), behind=behind)
    out['blink'] = 1.0 if (w > 0.95 and 1.10 <= (T % IDLE_T) < 1.19) else 0.0
    return out


def ball_at(P):
    """Où est la boule de la masse dans cette pose (même calcul que solenn.build)."""
    U = mchain(mT(P['lean'] * 0.3, P['crouch'] * 0.8), mR(P['lean'] * 1.0, 64, 104))
    G = mapp(U, P['grip'])
    a = P['ang'] + P['lean']
    return add(G, unit(a), M.S_BALL + P['stretch']), G, a


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


def outlined(shapes_fills, ink=EINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs)."""
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%.3f">%s%s</g>' % (op, sil, col)


def puff(fig, cx, cy, r, op=1.0, kind='dust'):
    """Une bouffée (poussière ocre ou souffle gris tiède) : quelques boules sous un contour doux, éclairées en haut à
    droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    balls = [(cx, cy, r), (cx + 0.75 * r, cy + 0.25 * r, 0.75 * r), (cx - 0.8 * r, cy + 0.3 * r, 0.7 * r), (cx + 0.15 * r, cy - 0.55 * r, 0.62 * r)]
    if kind == 'dust':
        stops, ink = [(0, '#fff2d4'), (0.5, '#dcb486'), (1, '#9a7058')], '#5a3e46'
    else:
        stops, ink = [(0, '#fbfaff'), (0.5, '#d4cee0'), (1, '#9e94b2')], SINK
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), stops)
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.1"/>' % (fm(x), fm(y), fm(rr), ink, ink) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%.3f">%s%s</g>' % (op, sil, col)


def curl(fig, c, r, a0, turn, w, op=1.0, kind='dust'):
    """Une volute qui s'enroule (un ruban courbe qui s'affine), sous un contour doux."""
    if op <= 0.02:
        return ''
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + turn * t)
        rr = r * (1 - 0.55 * t)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sh = ribbon(pts, [w * 0.4] + [w * (1 - 0.6 * i / n) for i in range(1, n)] + [0.15])
    if kind == 'steam':
        gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fbfaff'), (0.6, '#d4cee0'), (1, '#9e94b2')])
        return outlined([(sh, gr, 1)], ink=SINK, w=1.0, op=op)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, '#fff2d4'), (0.6, '#dcb486'), (1, '#9a7058')])
    return outlined([(sh, gr, 1)], ink='#5a3e46', w=1.0, op=op)


def hsh(i, k):
    """Un « hasard » fixe (même valeur à chaque image)."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1


def rock(fig, c, r, seed=0, rot=0.0, op=1.0):
    """Un éclat de roche ou une motte : un polygone irrégulier à facettes (face éclairée en haut à droite)."""
    if r < 0.25 or op <= 0.02:
        return ''
    n = 6
    pts = []
    for i in range(n):
        a = math.radians(rot + 360 * i / n + 25 * (hsh(seed, i) - 0.5))
        rr = r * (0.72 + 0.4 * hsh(seed, i + 7))
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    body = rpoly(pts, r * 0.18)
    lit = sorted(range(n), key=lambda i: -((pts[i][0] - c[0]) * 0.6 - (pts[i][1] - c[1]) * 0.8))[:2]
    lit.sort()
    cc = (c[0] + r * 0.08, c[1] - r * 0.1)
    face = rpoly([cc, pts[lit[0]], pts[lit[1]]], r * 0.1)
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, E[3]), (0.55, E[4]), (1, E[5])])
    return outlined([(body, gr, 1), (face, E[3], 0.85)], w=1.1, op=op)


def stone(fig, base, h, w, seed=0, gold=0.0, op=1.0):
    """Une dalle de pierre du rempart, plantée dans le sol : deux faces (la droite éclairée), un sommet cassé ; gold :
    la face éclairée devient dorée et une lueur court sur l'arête (le lancement)."""
    if h < 0.8 or op <= 0.02:
        return ''
    bx, g = base
    tl = (bx - w * 0.48, g - h * (0.8 + 0.14 * hsh(seed, 1)))
    tm = (bx - w * 0.06, g - h)
    tr = (bx + w * 0.46, g - h * (0.72 + 0.18 * hsh(seed, 2)))
    bl, bm, br_ = (bx - w * 0.55, g), (bx - w * 0.02, g + 0.5), (bx + w * 0.55, g)
    left = rpoly([bl, tl, tm, bm], 0.5)
    right = rpoly([bm, tm, tr, br_], 0.5)
    gl = g_lin(fig, tm, bl, [(0, E[4]), (1, E[5])])
    if gold > 0:
        gr = g_lin(fig, tr, bm, [(0, '#fff6ce'), (0.5, E[1]), (1, E[2])])
    else:
        gr = g_lin(fig, tr, bm, [(0, E[3]), (1, E[4])])
    crack_ = ribbon([lerp(tm, bm, 0.2), add(lerp(tm, bm, 0.5), (0.7, 0)), lerp(tm, bm, 0.8)], [0.1, 0.5, 0.1])
    top = ribbon([tl, tm, tr], [0.1, 0.8, 0.1])
    items = [(left, gl, 1)]
    if 0 < gold < 1:
        items.append((right, g_lin(fig, tr, bm, [(0, E[3]), (1, E[4])]), 1))
        items.append((right, gr, gold))
    else:
        items.append((right, gr, 1))
    items += [(top, '#fff6d8', 0.7 if gold <= 0 else 1), (crack_, E[6], 0.5)]
    return outlined(items, w=1.2, op=op)


def pop(fig, c, r, facing=0.0, op=1.0):
    """Un éclat d'impact doré : un coeur et des lobes arrondis, coeur blanc, bord or puis ambre ; un seul contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    lobes = [(c[0], c[1], r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        lobes.append((c[0] + r * 0.95 * math.cos(a), c[1] + r * 0.95 * math.sin(a), r * (0.62 if abs(da) < 80 else 0.45)))
    gr = g_rad(fig, (c[0] + 0.2 * r, c[1] - 0.2 * r), r * 1.65, [(0, '#fffef4'), (0.35, E[0]), (0.65, E[1]), (0.9, E[2]), (1, '#b86a2a')])
    return outlined([(ellipse(x, y, rr), gr, 1) for x, y, rr in lobes], ink='#6a3a1e', w=1.3, op=op)


def sparks(fig, c, k, seed=0, scale=1.0, facing=0.0, spread=150):
    """La gerbe d'étincelles de fer : de petites virgules courbes de longueurs inégales, qui volent et retombent
    (blanc doré puis ambre) ; k : 0..1 le temps de la gerbe."""
    if not 0 <= k < 1:
        return ''
    out = []
    n = 9
    for i in range(n):
        a = math.radians(facing - spread / 2 + spread * (i + 0.5 * hsh(seed, i)) / n)
        sp = (10 + 9 * hsh(seed, i + 3)) * scale
        bend = (hsh(seed, i + 5) - 0.5) * 6
        t = k
        p = (c[0] + math.cos(a) * sp * t, c[1] + math.sin(a) * sp * t + 14 * t * t * scale)
        q = (c[0] + math.cos(a) * sp * max(0, t - 0.22), c[1] + math.sin(a) * sp * max(0, t - 0.22) + 14 * max(0, t - 0.22) ** 2 * scale)
        mid = add(lerp(p, q, 0.5), (-math.sin(a) * bend * 0.1, math.cos(a) * bend * 0.1))
        w = (0.9 + 0.5 * hsh(seed, i + 8)) * (1 - 0.6 * k) * scale
        sh = ribbon([q, mid, p], [0.1, w, 0.2])
        col = '#fffbe4' if k < 0.35 else (E[1] if k < 0.7 else E[2])
        out.append('<path d="%s" fill="%s" opacity="%.3f"/>' % (sh.d(), col, 1 - k * 0.8))
    return ''.join(out)


def sparkle(fig, c, r, op=1.0):
    """Un scintillement rond (une étoile à quatre branches courbes, coeur blanc), pour le haut des pierres."""
    if r < 0.2 or op <= 0.02:
        return ''
    x, y = c
    pts = []
    for i in range(8):
        a = math.radians(-90 + 45 * i)
        rr = r if i % 2 == 0 else r * 0.3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    sh = sm(pts, sharp=(0, 2, 4, 6), t=0.6)
    gr = g_rad(fig, c, r, [(0, '#ffffff'), (0.5, '#fff0b0'), (1, E[1])])
    return '<g opacity="%.3f"><path d="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="#ffffff"/></g>' % (
        op, sh.d(), gr, fm(x), fm(y), fm(r * 0.22))


def crack(fig, x, half, level, seed=0, op=1.0, y=GR):
    """Le sol qui se fend au ras du sol (couché par la perspective) : une lueur dorée, le creux, le cœur d'or."""
    if op <= 0.02 or half < 1:
        return []
    out = []
    gl = g_rad(fig, (x, y), half * 1.4, [(0, E[1], 0.6 * op * min(1, 0.4 + 0.3 * level)), (1, E[2], 0)])
    out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(y), fm(half * 1.4), fm(half * 0.28), gl))
    for side in (-1, 1):
        pts = [(x, y + 0.2)]
        n = 4
        for i in range(1, n + 1):
            t = i / n
            pts.append((x + side * half * t, y + 0.2 + (1.2 * hsh(seed + side, i) - 0.6) * (1 - t) + 0.25 * t))
        w = 1.0 + 0.4 * level
        sh = ribbon(pts, [w] + [w * (1 - i / n) + 0.1 for i in range(1, n)] + [0.05])
        core = ribbon(pts, [w * 0.45] + [w * 0.45 * (1 - i / n) + 0.05 for i in range(1, n)] + [0.02])
        out.append('<g opacity="%.3f"><path d="%s" fill="%s"/><path d="%s" fill="%s"/></g>' % (
            op, sh.d(), E[6], core.d(), E[1] if level < 2 else E[0]))
    return out


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def trail(fig, path_out, path_in, op=1.0):
    """La traînée de la masse : un croissant d'acier clair entre le chemin de la boule et celui du manche, qui
    s'efface vers l'arrière, bordé d'or."""
    if len(path_out) < 3 or op <= 0.02:
        return ''
    n = len(path_out)
    inner = [lerp(path_out[i], path_in[i], 0.2 + 0.8 * (1 - i / (n - 1)) ** 0.7) for i in range(n)]
    body = sm(path_out + inner[::-1], sharp=(0, n - 1, n), t=0.6)
    rim = ribbon(path_out, [0.2] + [1.6 * i / (n - 1) + 0.2 for i in range(1, n - 1)] + [1.4])
    g1 = g_lin(fig, path_out[0], path_out[-1], [(0, '#c8d0ea', 0), (1, '#f4f6ff', 0.75 * op)])
    g2 = g_lin(fig, path_out[0], path_out[-1], [(0, E[2], 0), (0.6, E[1], 0.8 * op), (1, E[0], op)])
    return '<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (body.d(), g1, rim.d(), g2)


# ---- le souffle bourru : une bouffée sort sous la moustache, roule vers l'avant et s'enroule

def breath_puff(fig, mouth, k, big=1.0):
    if not 0 < k < 1:
        return
    o = env(k, 0, 0.15, 0.55, 1)
    x, y = mouth[0] + 2 + 7 * k * big, mouth[1] + 1.5 + 2.5 * k
    fig.fx_front.append(puff(fig, x, y, (0.8 + 1.5 * k) * big, op=0.75 * o, kind='steam'))
    if k > 0.35:
        fig.fx_front.append(curl(fig, (x + 3.2 * big, y - 0.8), 1.8 * big, 200, 250, 1.0 * big, op=0.7 * o, kind='steam'))


# ---- l'attaque de base

_ATT = {}


def fx_attack(tl):
    def f(fig, ctx):
        # la fureur : une lueur dorée derrière la tête pendant l'armé
        o = env(tl, 200, 300, 430, 520)
        if o > 0:
            hx, hy = ctx['head']
            fig.fx_back.append('<ellipse cx="%s" cy="%s" rx="22" ry="18" fill="%s"/>' % (
                fm(hx - 6), fm(hy - 6), g_rad(fig, (hx - 6, hy - 6), 22, [(0, E[1], 0.35 * o), (1, E[1], 0)], 18)))
        # la traînée de la masse pendant la frappe (le chemin réel de la boule et du manche, sur les 90 ms passées)
        if ATT_SWING[0] <= tl <= ATT_SWING[1] + 60:
            outp, inp = [], []
            for j in range(10, -1, -1):
                tt = max(ATT_SWING[0] - 40, min(ATT_SWING[1], tl - j * 9))
                Pk = keyed(ATTACK, tt)
                Pk = dict(lean=Pk['lean'], crouch=Pk['crouch'], grip=(Pk['gx'], Pk['gy']), ang=Pk['ang'], stretch=Pk['stretch'])
                b, G, a = ball_at(Pk)
                outp.append(add(b, unit(a), 4.0))
                inp.append(add(G, unit(a), 20.0))
            op = 1.0 if tl <= ATT_SWING[1] else 1 - (tl - ATT_SWING[1]) / 60
            fig.fx_front.insert(0, trail(fig, outp, inp, op))
        # l'impact : éclat d'or, gerbe d'étincelles de fer (arrêt sur l'image)
        if tl >= ATT_HIT - 5:
            if 'hit' not in _ATT:
                _ATT['hit'] = ctx['ball']
            hx, hy = _ATT['hit']
            k = (tl - ATT_HIT) / 260
            if 0 <= k < 1:
                o = env(tl, ATT_HIT - 5, ATT_HIT + 20, ATT_HIT + 120, ATT_HIT + 260)
                fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="14" ry="14" fill="%s"/>' % (
                    fm(hx), fm(hy), g_rad(fig, (hx, hy), 14, [(0, '#fff6ce', 0.7 * o), (0.5, E[1], 0.3 * o), (1, E[1], 0)])))
                fig.fx_front.append(pop(fig, (hx + 2, hy), 5.6 * (1 - 0.5 * k), facing=0, op=o))
                fig.fx_front.append(sparks(fig, (hx + 3, hy), min(0.99, k * 1.1), seed=3, scale=1.1, facing=-10, spread=170))
            # il tape du pied : la terre se fend sous le pied proche, des mottes sautent, la poussière roule
            fx_, fy_ = ctx['feet'][0]
            tau = (tl - ATT_HIT) / 1000
            if 0 <= tau < 0.6:
                o = env(tau, 0, 0.04, 0.2, 0.5)
                fig.fx_back.extend(crack(fig, fx_ + 2, 13, 2, seed=5, op=o))
                for i, (vx, vy, r) in enumerate(((-40, -46, 1.4), (-58, -30, 1.0), (30, -50, 1.1), (50, -34, 0.9), (-22, -60, 0.8))):
                    x, y = ballistic((fx_ + 2, GR - 1.5), (vx, vy), 190, tau)
                    if y < GR and tau < 0.5:
                        fig.fx_front.append(rock(fig, (x, y), r, seed=11 + i, rot=tau * 500 + i * 40, op=1 - tau / 0.5))
                od = env(tau, 0, 0.06, 0.25, 0.55)
                fig.fx_back.append(puff(fig, fx_ - 12 - 10 * tau, GR - 3 - 3 * tau, 2.6 + 3.0 * tau, op=0.85 * od))
                fig.fx_front.append(puff(fig, fx_ + 14 + 10 * tau, GR - 2.0, 2.0 + 2.2 * tau, op=0.8 * od))
                fig.fx_front.append(puff(fig, fx_ - 4 - 4 * tau, GR - 1.6, 1.6 + 1.2 * tau, op=0.75 * od))
        else:
            _ATT.pop('hit', None)
    return f


# ---- la spéciale

STONES = []     # (angle en degrés — 90 = devant lui, vers nous ; 270 = derrière —, hauteur, largeur, graine)
for _i in range(15):
    _a = 90 + 24 * _i + 6 * (hsh(_i, 1) - 0.5)
    _s = math.sin(math.radians(_a))
    _h = 17 - 7.5 * _s + 3 * (hsh(_i, 2) - 0.5)          # devant plus basses (on voit ses pieds), derrière plus hautes
    STONES.append((_a % 360, _h, 11.0 + 2.5 * hsh(_i, 3), 20 + _i))


def ring_pt(deg, s=1.0):
    a = math.radians(deg)
    return (RING_C[0] + RING_RX * s * math.cos(a), RING_C[1] + RING_RY * s * math.sin(a))


def gold_ring(fig, s, level, back):
    """La veine d'or au sol en anneau (la moitié de derrière ou de devant) et sa lueur."""
    if s <= 0.02 or level <= 0.01:
        return ''
    a0, a1 = (180, 360) if back else (0, 180)
    pts = [ring_pt(a0 + (a1 - a0) * i / 40, s) for i in range(41)]
    w = 0.9 + 0.5 * level
    out = ''
    if back:
        gl = g_rad(fig, RING_C, RING_RX * s * 1.05, [(0, E[1], 0.0), (0.7, E[1], 0.16 * level), (0.95, E[0], 0.3 * level), (1, E[1], 0)],
                   RING_RY * s * 1.05)
        out += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(RING_C[0]), fm(RING_C[1]), fm(RING_RX * s * 1.05),
                                                                     fm(RING_RY * s * 1.05), gl)
    out += '<path d="%s" fill="%s" opacity="%.3f"/>' % (ribbon(pts, [0.2] + [w * 2.2] * 39 + [0.2]).d(), E[2], 0.55 * min(1, level))
    out += '<path d="%s" fill="%s"/>' % (ribbon(pts, [0.1] + [w] * 39 + [0.1]).d(), E[1])
    out += '<path d="%s" fill="%s"/>' % (ribbon(pts, [0.05] + [w * 0.4] * 39 + [0.05]).d(), E[0])
    return out


def fx_special(tl):
    def f(fig, ctx):
        # 1) le rassemblement : la poussière tourne à ses pieds, des cailloux se soulèvent
        o = env(tl, SP_GATHER[0], SP_GATHER[0] + 120, SP_GATHER[1] - 60, SP_STOMP + 40)
        if o > 0:
            for i in range(3):
                ph = tl / 1000 * 5 + i * 2.1
                cx = 64 + 30 * math.cos(ph)
                cy = GR - 2 + 3 * math.sin(ph)
                fig.fx_back.append(curl(fig, (cx, cy), 3.0, math.degrees(ph) + 90, 240, 1.2, op=0.7 * o))
            for i in range(5):
                lift = smooth((tl - SP_GATHER[0] - 60 * i) / 260) * (3 + 3 * hsh(i, 9))
                x = 64 + (-34 + 17 * i) + 2 * math.sin(tl / 90 + i)
                fig.fx_front.append(rock(fig, (x, GR - 0.8 - lift), 0.9 + 0.4 * hsh(i, 4), seed=40 + i, rot=tl * 0.3 + i * 60, op=o))
        # 2) le coup de pied : la veine d'or court en anneau, les dalles jaillissent, puis se rassoient
        if SP_STOMP <= tl < SP_SINK[1] + 80:
            s = smooth((tl - SP_STOMP) / 120) * 0.45 + 0.55 if tl < SP_STOMP + 120 else 1.0
            lv = 2.0 * env(tl, SP_STOMP, SP_STOMP + 30, SP_LAUNCH[1], SP_SINK[1]) + 1.0 * env(tl, SP_LAUNCH[0] - 20, SP_LAUNCH[0], SP_LAUNCH[1] - 60, SP_LAUNCH[1] + 40)
            fig.fx_back.append(gold_ring(fig, s, lv, True))
            fig.fx_front.insert(0, gold_ring(fig, s, lv, False))
            gold = env(tl, SP_LAUNCH[0] - 30, SP_LAUNCH[0] + 10, SP_LAUNCH[1] - 40, SP_LAUNCH[1] + 60)
            back, front = [], []
            for i, (a, h, w, seed) in enumerate(STONES):
                # les dalles de derrière et des côtés sortent d'abord, celles de devant juste après
                d0 = SP_STOMP + (0 if math.sin(math.radians(a)) < 0.3 else 50)
                rise = smooth((tl - d0) / 110)
                over = 0.12 * env(tl, d0 + 60, d0 + 120, d0 + 140, d0 + 220)
                sink = smooth((tl - SP_SINK[0] - (0 if math.sin(math.radians(a)) > 0.3 else 60)) / 170)
                hh = h * (rise + over) * (1 - sink)
                if hh < 0.8:
                    continue
                sc = 0.86 + 0.18 * (math.sin(math.radians(a)) + 1) / 2
                base = ring_pt(a)
                svg = stone(fig, base, hh * sc, w * sc, seed=seed, gold=gold)
                (back if math.sin(math.radians(a)) < 0 else front).append((base[1], svg, base, hh * sc, w * sc, i))
            back.sort()
            front.sort()
            for _, svg, *_ in back:
                fig.fx_back.append(svg)
            for _, svg, *_ in front:
                fig.fx_front.append(svg)
            # le lancement : des étincelles rondes au sommet des pierres, des grains d'or qui montent
            if gold > 0:
                for _, _, base, hh, w, i in back + front:
                    if i % 3 == int(tl / 70) % 3:
                        tgt = fig.fx_back if math.sin(math.radians(STONES[i][0])) < 0 else fig.fx_front
                        tgt.append(sparkle(fig, (base[0] - w * 0.06, base[1] - hh - 0.6), 2.6, op=gold))
                for j in range(0, 10, 2):
                    tt = ((tl - SP_LAUNCH[0]) / 600 + hsh(j, 5)) % 1
                    a = 360 * hsh(j, 6)
                    p = ring_pt(a, 0.4 + 0.5 * hsh(j, 7))
                    y = p[1] - 30 * tt
                    fig.fx_front.append(EP.etincelle(fig, p[0], y, 0, -50, 0.6 + 0.4 * hsh(j, 8), 'or', op=gold * (1 - tt)))
            # la poussière soulevée par les dalles
            od = env(tl, SP_STOMP, SP_STOMP + 60, SP_STOMP + 200, SP_STOMP + 420) + env(tl, SP_SINK[0], SP_SINK[0] + 60, SP_SINK[0] + 160, SP_SINK[1] + 60)
            if od > 0:
                for j in range(3):
                    a = 30 + 120 * j
                    p = ring_pt(a, 1.04)
                    tgt = fig.fx_back if math.sin(math.radians(a)) < 0 else fig.fx_front
                    tgt.append(puff(fig, p[0], p[1] - 1.5, 2.2 + 0.8 * hsh(j, 3), op=0.7 * min(1, od)))
            # le pied qui frappe : la fissure d'or
            fx_, fy_ = ctx['feet'][0]
            oc = env(tl, SP_STOMP, SP_STOMP + 20, SP_STOMP + 200, SP_STOMP + 400)
            fig.fx_back.extend(crack(fig, fx_ + 2, 12, 2, seed=8, op=oc))
        # 3) le défi : la masse frappe la face du bouclier (éclat, étincelles), il crie (souffle), lueur rouge
        if tl >= SP_CLANG - 5:
            if 'clang' not in _ATT:
                _ATT['clang'] = ctx['ball']
            cx, cy = _ATT['clang']
            k = (tl - SP_CLANG) / 240
            if 0 <= k < 1:
                o = env(tl, SP_CLANG - 5, SP_CLANG + 15, SP_CLANG + 90, SP_CLANG + 240)
                fig.fx_front.append(pop(fig, (cx + 1, cy - 1), 4.6 * (1 - 0.5 * k), facing=-60, op=o))
                fig.fx_front.append(sparks(fig, (cx + 1, cy - 1), min(0.99, k * 1.1), seed=17, scale=0.9, facing=-80, spread=200))
            kb = (tl - SP_CLANG - 80) / 420
            breath_puff(fig, ctx['mouth'], kb, big=1.2)
        else:
            _ATT.pop('clang', None)
    return f


def special_tint(tl):
    """(or, rouge) : la lueur d'or du lancement (un voile sur lui), la lueur rouge du défi (des liserés autour de lui)."""
    g = env(tl, SP_LAUNCH[0] - 30, SP_LAUNCH[0] + 10, SP_LAUNCH[1] - 60, SP_LAUNCH[1] + 60)
    r = env(tl, SP_TAUNT[0] - 10, SP_TAUNT[0] + 60, SP_TAUNT[0] + 180, SP_TAUNT[1])
    if r > 0:
        r *= 0.85 + 0.15 * math.sin((tl - SP_TAUNT[0]) / 45)
    return g, r


def fx_idle(T):
    """Au repos : le souffle bourru par la moustache, à chaque expiration (une fois sur deux)."""
    def f(fig, ctx):
        cyc = T / IDLE_T
        if int(cyc) % 2 == 0:
            k = ((cyc % 1) - 0.05) / 0.5
            breath_puff(fig, ctx['mouth'], k, big=0.8)
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
    ImageDraw.Draw(sh).ellipse([cx - 34 * k, fy - 3.0 * k, cx + 34 * k, fy + 3.0 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


def timeline():
    a = ATTACK[-1][0] / 1000
    seq = [('idle', 2 * IDLE_T), ('attack', a), ('idle', 0.7), ('attack', a), ('idle', 0.9),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
    out, T = [], 0.0
    for a_, d in seq:
        out.append((a_, T, T + d))
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
    tl = (T - t0) * 1000
    if act:
        fx = [fx_attack(tl) if act == 'attack' else fx_special(tl)]
    else:
        fx = [fx_idle(T)]
    fig = M.build(ow=ow, pose=P, fx=fx, frame=view)
    if act == 'special':
        g, r = special_tint(tl)
        if g > 0:
            fig.veil = ('#ffd45c', 0.22 * g)
        if r > 0:
            fig.auras = (('#ff3a52', 4.2 * r, 0.16 * r), ('#ff5a5a', 2.6 * r, 0.24 * r), ('#ff7a66', 1.2 * r, 0.4 * r))
    return fig.svg(), P


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
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-solenn-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('solenn'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan de la terre (Arachné), le pixel art à gauche
    et le vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')).convert('RGBA')
    SC = 1.22
    CW, CH = 440, 250
    cx0, cy0 = 20, 690
    feet = (200, 200)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.5), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.9)]
    segs, T = [], 0.0
    for a_, d in seq:
        segs.append((a_, T, T + d))
        T += d
    n = int(round(T * FPS))
    view = (M.FEET[0] - feet[0] / SC, GR - feet[1] / SC, CW / SC, CH / SC)
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
    bg.alpha_composite(shadow_layer(w, h, view))
    for p in pngs:
        im = bg.copy()
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
        moments = [0.8, a_s + 0.19, a_s + 0.35, a_s + 0.47, a_s + 0.5, a_s + 0.56, a_s + 0.7, a_s + 0.92,
                   s_s + 0.2, s_s + 0.42, s_s + 0.53, s_s + 0.62, s_s + 0.8, s_s + 1.05, s_s + 1.22, s_s + 1.4]
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



# ======================================================================== la spéciale « pro » (28/11)
# Demande du propriétaire : des effets d'une seule silhouette, aux courbes continues, sans formes empilées. Pendant la
# spéciale seulement : la veine d'or au sol en rubans d'un seul tenant, la fente du sol une courbe lisse, les
# cailloux en galets aux arêtes adoucies, la poussière en bouffées fondues, l'éclat du coup en lumière et étincelles ;
# les menhirs (la matière du sort) et l'attaque gardent leur dessin.
import effets_pro as EP  # noqa: E402

_PIERRE = ('#f6e6c8', E[3], E[4], E[5], E[6], '#24142e')


def _gold_ring(fig, s, level, back):
    if s <= 0.02 or level <= 0.01:
        return ''
    a0, a1 = (180, 360) if back else (0, 180)
    out = EP.ruban(fig, EP.arc_ell(RING_C, RING_RX * s, RING_RY * s, a0, a1, 18), (2.2 + 1.2 * level) * 1.4, 'or',
                   op=min(1, 0.4 + 0.5 * level) * (0.8 if back else 1), kind='fuseau', halo=0.6)
    if back:
        out = EP.lumiere(fig, RING_C, RING_RX * s * 0.9, 0.25 * level, 'or') + out
    return out


def _crack(fig, x, half, level, seed=0, op=1.0, y=GR):
    if op <= 0.02 or half < 1:
        return []
    return [EP.fissure(fig, [(x - half * 1.4, y + 0.4), (x - half * 0.3, y + 0.9), (x + half * 0.5, y + 0.3), (x + half * 1.4, y + 0.6)],
                       2.6, 'terre', op=op, glow=min(1, 0.5 + 0.3 * level), pierre=_PIERRE)]


def _sparks(fig, c, k, seed=0, scale=1.0, facing=0.0, spread=150):
    return EP.group(EP.choc(fig, c, k, 7 * scale, 'or', ang=facing, n=3, seed=seed))


EP.accrocher(sys.modules[__name__], {
    'gold_ring': _gold_ring,
    'crack': _crack,
    'sparks': _sparks,
    'curl': lambda fig, c, r, a0, turn, w, op=1.0, kind='dust': EP.ruban(
        fig, [(c[0] + r * (1 - 0.6 * i / 8) * math.cos(math.radians(a0 + turn * i / 8)), c[1] + r * (1 - 0.6 * i / 8) * math.sin(math.radians(a0 + turn * i / 8)))
              for i in range(9)], w * 1.8, 'terre', op=op, kind='pointe', halo=0.2),
    'rock': lambda fig, c, r, seed=0, rot=0.0, op=1.0: EP.caillou(fig, c[0], c[1], r * 1.2, rot, seed=seed, op=op, pierre=_PIERRE),
    'puff': lambda fig, cx, cy, r, op=1.0, kind='dust': EP.nuage(fig, cx, cy, r * 1.15, 'terre', op=op, seed=int(cx) % 3, flat=0.75),
    'sparkle': lambda fig, c, r, op=1.0: EP.lumiere(fig, c, r * 2.0, op, 'or'),
    'pop': lambda fig, c, r, facing=0.0, op=1.0: EP.lumiere(fig, c, r * 2.4, op, 'or'),
})


if __name__ == '__main__':
    main()
