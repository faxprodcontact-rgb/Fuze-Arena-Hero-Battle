# Myrr vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/myrr/build.py)
# — respiration, attaque de base « Appel du héraut », attaque spéciale « Trompette de Grâce » (sort d'équipe) — dans
# le style lisse de l'interface, à 24 images par seconde (même méthode que Kael, Néfira, Eldra : ../kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/myrr/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/myrr/
#   python3 refonte-graphique/ui-moderne/heros/myrr/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (myrr.py) est fait de morceaux ; chaque image le redessine dans une POSE : le buste respire et
# se penche depuis les hanches, la tête suit avec un léger retard, l'auréole flotte (en retard sur la tête) ; les ailes
# tournent autour de leur racine et passent d'un état à l'autre (repliées, à moitié ouvertes, grandes ouvertes en V,
# coup d'aile) : c'est le même squelette d'aile (bord d'attaque, plumes, couvertures) qui change de réglages, rien ne
# se décroche ; la trompette passe de la hanche aux lèvres ; le bras lointain est placé par cinématique inverse depuis
# le poing qui la tient (le coude tourne sur un arc) ; goutte d'oreille et bas de la robe suivent avec retard.
# Les poses clés et les durées reprennent celles du pixel art.
# Effets du vent (mêmes formes et mêmes tons qu'Eldra, l'autre héroïne du vent) : rubans qui s'enroulent en volutes,
# croissant du souffle, éclats, bouffées ; pour la spéciale (sort d'équipe : tout naît sur elle et s'étend EN CERCLE
# autour d'elle) : anneau de vent, plumes de lumière qui pleuvent en cercle, taches sombres qui s'évaporent, auréole
# embrasée et grand halo doré. Aucun flou SVG ; jamais de rayons droits répétés.
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
import myrr as M  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, mchain, mT, mR, mS, mapp, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of, taper  # noqa: E402

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'myrr')
TMP = os.path.join(HERE, '_images')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-myrr'
FPS = 24
VIEW = (-70, -52, 330.0, 185.6)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = M.GRD
FOE = (206.0, GR - 40)               # le milieu de l'ennemi
HIT_AT = (204.0, GR - 54)            # là où l'onde le frappe (à hauteur de poitrine)
CEN = (68.0, GR - 1.0)               # le centre du cercle au sol, sous elle (la spéciale)

WIND = ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470']   # le vent (celui d'Eldra)
WINK = '#123c4a'                     # le contour des effets de vent
GOLDFX = ['#fffbe8', '#fff0b0', '#ffd45c', '#e0962e', '#a8601e']
SPECK = ['#3e284a', '#6a4e7a', '#b8acc4']   # les taches sombres (le mal que la spéciale chasse)


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


# les réglages animés (voir myrr.py) ; tb : la trompette va de la hanche (0) aux lèvres (1), ta : son angle aux lèvres ;
# wo : les ailes s'ouvrent (0 repliées, 1 à moitié, 2 grandes ouvertes en V), wb : coup d'aile (battue) ; aura : liseré
# de lumière autour d'elle
BASE = dict(lean=0.0, crouch=0.0, lift=0.0, headx=0.0, heady=0.0, tilt=0.0, halo=0.0, glow=0.0, wl=0.0, wo=0.0, wb=0.0,
            wph=0.0, tb=0.0, ta=-5.0, gs=M.GS0, nh=0.0, hem=0.0, cheek=0.0, gold=0.0, aura=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    """La pose d'une action à l'instant t (ms) : chaque réglage suit sa courbe entre les clés."""
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# 2) L'attaque de base « Appel du héraut » : elle lève la trompette (inspiration, buste en arrière, ailes soulevées),
# la tient aux lèvres un temps (joues gonflées), puis souffle : éclat blanc au pavillon, une onde de vent part vers
# l'ennemi (deux rubans, blanc et jade, enroulés l'un autour de l'autre derrière un grand croissant de souffle, une
# plume emportée) ; l'onde frappe (éclat, volutes qui s'ouvrent), se défait en bouffées ; elle abaisse la trompette.
ATTACK = [
    (0, {}),
    (110, dict(tb=0.5, ta=-28, lean=-0.6, wl=1.4, head=(-0.2, -0.2), gs=19.0, halo=0.2)),
    (230, dict(tb=1.0, ta=-5, lean=-1.6, wl=2.6, head=(-0.6, -0.4), tilt=-2.0, cheek=1, gs=14.0, halo=0.5)),
    (330, dict(tb=1.0, ta=-5, lean=-2.0, wl=3.0, head=(-0.8, -0.5), tilt=-2.6, cheek=1, gs=14.0, halo=0.6)),
    (370, dict(tb=1.0, ta=-3, lean=1.2, wl=-0.8, head=(0.4, 0.0), tilt=0.6, cheek=1, gs=14.0, halo=-0.3, hem=0.6)),
    (450, dict(tb=1.0, ta=-3, lean=2.0, wl=-1.8, head=(0.6, 0.1), tilt=1.0, cheek=1, gs=14.0, halo=-0.5, hem=1.0)),
    (620, dict(tb=1.0, ta=-3, lean=1.6, wl=-0.6, head=(0.5, 0.1), tilt=0.8, cheek=0.7, gs=14.0, halo=0.2, hem=0.4)),
    (740, dict(tb=0.7, ta=-16, lean=0.6, wl=0.4, head=(0.2, 0.0), gs=16.0, halo=0.3, hem=-0.3)),
    (890, dict(tb=0.12, ta=-48, crouch=0.5, gs=22.5, hem=-0.4)),
    (1000, dict(crouch=0.3, hem=0.2)),
    (1130, {}),
]
ATT_BLOW = 345        # elle souffle
ATT_FLY = (350, 560)  # l'onde vole jusqu'à l'ennemi
ATT_HIT = 560         # l'onde frappe

# 3) La spéciale « Trompette de Grâce » (sort d'équipe : soin, purification, résurrection) : elle se ramasse (le vent
# se lève à ses pieds), déploie grand ses ailes et s'élève ; suspendue, ailes levées en V, elle porte la trompette aux
# lèvres, pavillon vers le ciel (l'auréole s'illumine). Elle sonne (LANCEMENT 1, 680 ms : soin et purification) : éclair
# doux blanc et or, sa silhouette s'éclaire, de petites taches sombres apparaissent sur elle ; coup d'aile ; un anneau
# de vent naît autour de sa taille et s'élargit tout autour d'elle (arrêt sur l'image), puis se défait en volutes ;
# des plumes de lumière pleuvent en cercle et se posent ; les taches se détachent et s'évaporent. Seconde note, plus
# douce (LANCEMENT 2, 1310 ms : résurrection) : l'auréole s'embrase, un grand halo doré pulse une fois autour d'elle
# avec un anneau d'or au sol, puis s'éteint en lueurs qui montent. Elle redescend, replie ses ailes.
SPECIAL = [
    (0, {}),
    (100, dict(crouch=1.0, wl=1.0, hem=0.6, head=(0, 0.3))),
    (250, dict(crouch=2.0, lean=-0.8, wl=-3.0, hem=1.0, head=(0, 0.6), halo=0.4)),
    (330, dict(lift=3.0, wo=0.7, hem=-0.6, tb=0.3, ta=-50, gs=20, head=(0, -0.2), halo=0.8)),
    (420, dict(lift=7.5, wo=2.0, tb=1.0, ta=-40, gs=15, hem=-0.9, halo=-0.6, glow=0.5, cheek=1, head=(-0.3, -0.4), tilt=-3)),
    (620, dict(lift=9.0, wo=2.0, tb=1.0, ta=-40, gs=15, hem=-0.3, halo=-0.2, glow=1.0, cheek=1, head=(-0.4, -0.5), tilt=-4)),
    (680, dict(lift=8.0, wo=1.1, wb=1.0, tb=1.0, ta=-38, gs=15, hem=0.8, lean=1.0, glow=1.0, cheek=1, aura=1.0, head=(0.2, -0.2), tilt=-2)),
    (880, dict(lift=8.0, wo=1.1, wb=1.0, tb=1.0, ta=-38, gs=15, hem=0.5, lean=1.0, glow=1.0, cheek=0.8, aura=0.6, head=(0.2, -0.2), tilt=-2)),
    (970, dict(lift=9.0, wo=1.5, wb=0.3, tb=1.0, ta=-39, gs=15, hem=-0.2, glow=1.0, cheek=0.3, aura=0.3, tilt=-3)),
    (1060, dict(lift=9.2, wo=2.0, tb=1.0, ta=-40, gs=15, hem=-0.5, glow=1.0, aura=0.1, tilt=-3)),
    (1190, dict(lift=9.0, wo=2.0, tb=1.0, ta=-40, gs=15, hem=-0.2, glow=1.0, cheek=1, tilt=-4, head=(-0.3, -0.4))),
    (1310, dict(lift=8.6, wo=2.0, tb=1.0, ta=-41, gs=15, hem=0.2, glow=1.6, gold=1, cheek=1, aura=0.7, tilt=-4, head=(-0.3, -0.5))),
    (1510, dict(lift=8.0, wo=2.0, tb=1.0, ta=-40, gs=15, hem=0.1, glow=1.2, gold=0.4, cheek=0.4, aura=0.2, tilt=-3)),
    (1610, dict(lift=7.0, wo=1.0, tb=0.7, ta=-26, gs=17, hem=-0.2, glow=0.6, tilt=-1)),
    (1720, dict(lift=4.0, wo=0.4, tb=0.3, ta=-50, gs=21, wl=-2.0, hem=-0.4, glow=0.2)),
    (1840, dict(lift=1.0, wo=0.05, wl=-1.0, hem=0.3, crouch=0.3)),
    (1980, dict(crouch=0.8, hem=-0.5, halo=0.5)),
    (2130, {}),
]
SP_GATHER = (0, 330)
SP_BLOW = 680         # LANCEMENT 1 : le soin et la purification partent vers l'équipe (l'anneau de vent naît)
SP_NOTE2 = 1310       # LANCEMENT 2 : la résurrection (le grand halo doré au plus large)


# ======================================================================== la respiration (2 s)

def idle_offsets(T):
    u = 2 * math.pi * T / 2.0
    br = 0.5 - 0.5 * math.cos(u)
    # la tête suit le souffle avec un temps de retard, l'auréole avec un peu plus ; les ailes se soulèvent à
    # l'inspiration, les plumes ondulent ; le bas de la robe ondule ; la trompette se balance d'un rien
    d = dict(heady=-0.25 * (0.5 - 0.5 * math.cos(u - 0.6)), tilt=0.4 * math.sin(u - 1.0),
             halo=0.55 * math.sin(u - 1.9), wl=1.6 * (0.5 - 0.5 * math.cos(u - 0.5)),
             hem=0.25 * math.sin(u - 2.0), nh=0.08 * (0.5 - 0.5 * math.cos(u - 1.2)), ta=0.0)
    return d, br


def wing_state(wo, wb):
    if wo <= 1:
        st = M.mix_state('fold', 'demi', max(0.0, wo))
    else:
        st = M.mix_state('demi', 'grande', min(1.0, wo - 1))
    if wb > 0:
        st = M.mix_state(st, 'battue', wb)
    return st


def mouth_pre(P, br):
    """Les lèvres (le bout de l'embouchure), dans le repère d'avant le haut du corps (comme TM0)."""
    Hm = mchain(mT(0, -0.6 * br), mT(P['headx'], P['heady']), mR(P['tilt'], M.H0[0], M.H0[1] - 4), mS(1.1, 1.1, *M.H0))
    return mapp(Hm, (82.9, 42.4))


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
    br *= w
    # la trompette : de la hanche aux lèvres
    tb = max(0.0, min(1.0, P['tb']))
    mp = mouth_pre(P, br)
    ta_ = P['ta']
    tm = lerp(M.TM0, mp, tb)
    tang = M.TANG0 + (ta_ - M.TANG0) * tb
    # au repos, elle se balance d'un rien avec le souffle
    tang += w * 0.8 * math.sin(2 * math.pi * T / 2.0 - 0.9)
    st = wing_state(P['wo'], P['wb'])
    # le battement des ailes ouvertes : les plumes ondulent plus quand elles sont ouvertes
    out = dict(breath=br, lean=P['lean'], crouch=P['crouch'], lift=P['lift'], head=(P['headx'], P['heady']), tilt=P['tilt'],
               halo=P['halo'], glow=P['glow'], wing=st, wl=P['wl'], wlF=P['wl'] * 0.8,
               wph=2 * math.pi * T / 2.0 * (1 + 0.6 * min(2, P['wo'])) + P['wph'],
               tm=tm, tang=tang, gs=P['gs'], nh=P['nh'], hem=P['hem'], cheek=P['cheek'], gold=P['gold'],
               ear=math.sin(2 * math.pi * T * 0.8 - 0.5) + 0.6 * P['lean'], tb=tb)
    out['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % 4.0) < 1.39) else 0.0
    out['aura'] = P['aura']
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


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (sh.d(), ink, ink, fm(w))
                  for sh, fl, _ in shapes_fills if fl is not None and w > 0)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (min(1, op), sil, col)


def stroke_shape(center, widths):
    """Un ruban fermé le long d'une ligne, largeur donnée en chaque point (bouts pointus)."""
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


def gust(fig, p0, p1, p2, p3, w, curl=4.0, s=-1, tail=0.0, op=1.0, turn=290):
    """Une rafale : un ruban effilé le long d'une courbe, qui s'enroule en volute au bout. tail : l'arrière s'efface."""
    if op <= 0.02 or w < 0.15:
        return ''
    c = resample(bez(p0, p1, p2, p3, 30), 18)
    d = (p3[0] - p2[0], p3[1] - p2[1])
    if curl > 0.3:
        c = c + spiral(p3, d, curl, turn, s, 14)
    n = len(c)
    i0 = int(tail * (n - 4))
    c = c[i0:]
    n = len(c)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        ws.append(max(0.08, w * (math.sin(math.pi * min(1, t * 1.25)) ** 0.8) * (1 - 0.55 * t)))
    ws[0] = ws[-1] = 0.05
    sh = stroke_shape(c, ws)
    core = stroke_shape(c, [x * 0.42 for x in ws])
    gr = g_lin(fig, c[0], c[-1], [(0, WIND[3]), (0.35, WIND[2]), (0.7, WIND[1]), (1, WIND[2])])
    return outlined([(sh, gr, 1), (core, WIND[0], 0.85)], w=1.0, op=op)


def arc_band(C, R, a0, a1, w, taper_=0.8, n=28, ry=None):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    k = 1.0 if ry is None else ry / R
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper_)
        outer.append((C[0] + R * math.cos(a), C[1] + k * R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + k * (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def lens(C, R, a0, a1, w, ry=None, n=28):
    """Un croissant effilé aux DEUX bouts le long d'un arc d'ellipse (anneau de vent, onde)."""
    k = 1.0 if ry is None else ry / R
    pts = [(C[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + k * R * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    ws = [max(0.05, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]
    return pts, ws


def pop(fig, c, r, facing=0.0, op=1.0, gold=False):
    """L'éclat du vent : une boule de lumière blanc-cyan (dégradé), un croissant d'onde du côté visé."""
    if op <= 0.02 or r < 0.3:
        return ''
    tones = [GOLDFX[0], GOLDFX[1], GOLDFX[2], GOLDFX[3]] if gold else [WIND[0], WIND[1], WIND[3], WIND[4]]
    out = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(c[0]), fm(c[1]), fm(r * 2.2), g_rad(
        fig, c, r * 2.2, [(0, '#ffffff', 0.92 * op), (0.3, tones[1], 0.65 * op), (0.65, tones[2], 0.25 * op), (1, tones[3], 0)]))
    ring = arc_band(c, r * 1.25, facing - 70, facing + 70, r * 0.5, taper_=0.0)
    out += outlined([(ring, tones[1], 1)], w=1.0, op=op * 0.9)
    return out


def puff(fig, cx, cy, r, op=1.0, k=0):
    """Une bouffée de vent : quelques boules blanc-cyan réunies sous un contour doux, éclairées en haut à droite."""
    if r < 0.3 or op <= 0.02:
        return ''
    j = [(0, 0, 1), (0.8, 0.3, 0.72), (-0.82, 0.28, 0.7), (0.2, -0.55, 0.62), (-0.35, -0.35, 0.5)]
    balls = [(cx + r * dx, cy + r * dy, r * rr) for dx, dy, rr in j[:4 + (k % 2)]]
    gr = g_lin(fig, (cx + r, cy - r), (cx - r, cy + r), [(0, WIND[0]), (0.5, WIND[1]), (1, WIND[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), WINK, WINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


def sparkle(fig, c, r, op=1.0, rot=0.0):
    """Un éclat d'or : une étoile à quatre branches inégales aux flancs courbes (blanc au cœur)."""
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


def plume(fig, c, ang, s=1.0, op=1.0, light=False):
    """Une petite plume (emportée par le vent, ou plume de lumière) : vexille en amande courbe, rachis clair ;
    un seul contour (bleu nuit) ou aucun (plume de lumière, avec un halo doré)."""
    if op <= 0.02:
        return ''
    a = math.radians(ang)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    P = lambda i, j: (c[0] + s * (u[0] * i + v[0] * j), c[1] + s * (u[1] * i + v[1] * j))
    body = sm([P(-2.6, 0.1), P(-1.0, -0.9), P(1.2, -0.95), P(2.8, -0.2), P(1.6, 0.85), P(-0.8, 0.9)], sharp=(0, 3), t=0.9)
    quill = ribbon([P(-3.4, 0.25), P(-0.6, 0.05), P(2.4, -0.25)], [0.15 * s, 0.32 * s, 0.08])
    if light:
        gr = g_lin(fig, P(2, -1), P(-2, 1), [(0, '#ffffff'), (0.45, GOLDFX[1]), (1, GOLDFX[2])])
        return '<g opacity="%g">%s<path d="%s" fill="%s"/><path d="%s" fill="#ffffff" opacity="0.85"/></g>' % (
            op, glow(fig, c, 4.2 * s, GOLDFX[1], 0.55), body.d(), gr, quill.d())
    gr = g_lin(fig, P(2, -1), P(-2, 1), [(0, '#ffffff'), (0.55, '#e6ecfc'), (1, '#aab3de')])
    return outlined([(body, gr, 1), (quill, '#ffffff', 0.9)], ink='#2a2c5a', w=0.9, op=op)


# ---- 2) l'attaque : l'onde du souffle

def bezp(p0, p1, p2, p3, t):
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


_BELL = []


def fx_attack(tl):
    def f(fig, ctx):
        bell = ctx['bell']
        if tl < ATT_BLOW:
            _BELL[:] = [bell, ctx['tang']]
            # l'inspiration : de fines volutes d'air entrent dans le pavillon
            k = env(tl, 170, 240, 300, 345)
            for j in range(2):
                ph = (tl - 170) / 175
                a0 = 60 + 120 * j
                p0 = add(bell, unit(a0), 12 - 7 * ph)
                fig.fx_front.append(gust(fig, p0, add(p0, unit(a0 + 120), 3), add(bell, unit(a0 + 40), 4), add(bell, unit(a0), 2.0),
                                         1.4, curl=0, op=0.6 * k))
            return
        B0, ang0 = _BELL if _BELL else (bell, ctx['tang'])
        D = add(B0, unit(ang0), 2)
        # le chemin de l'onde : du pavillon à l'ennemi, en une légère courbe
        p0, p3 = D, HIT_AT
        p1 = add(p0, (26, -5))
        p2 = add(p3, (-28, -4))
        # l'éclat au pavillon
        k = env(tl, ATT_BLOW - 5, ATT_BLOW + 25, ATT_BLOW + 60, ATT_BLOW + 170)
        fig.fx_front.append(pop(fig, bell, 3.4 * (0.6 + 0.6 * k), facing=ang0, op=k))
        if ATT_FLY[0] <= tl <= ATT_HIT + 60:
            t = smooth((tl - ATT_FLY[0]) / (ATT_FLY[1] - ATT_FLY[0]))
            t = min(1.0, t)
            head = bezp(p0, p1, p2, p3, t)
            tg = norm(sub(bezp(p0, p1, p2, p3, min(1, t + 0.02)), bezp(p0, p1, p2, p3, max(0, t - 0.02))))
            fade = 1 - smooth((tl - ATT_HIT) / 60)
            # les deux rubans tressés (blanc et jade), de la queue (qui s'efface) jusqu'à la tête de l'onde
            t0 = max(0.0, t - 0.55)
            n = 26
            base = [bezp(p0, p1, p2, p3, t0 + (t - t0) * i / n) for i in range(n + 1)]
            for j, (tones, ph) in enumerate(((WIND[2], WIND[0]), (WIND[4], WIND[2]))):
                pts = []
                for i, q in enumerate(base):
                    u = i / n
                    tgq = norm(sub(base[min(n, i + 1)], base[max(0, i - 1)]))
                    nq = (-tgq[1], tgq[0])
                    amp = 3.4 * math.sin(math.pi * u) ** 0.6
                    pts.append(add(q, nq, amp * math.sin(2 * math.pi * (1.6 * u - tl / 260) + j * math.pi)))
                ws = [max(0.06, 3.0 * (u ** 1.1) * (1 - 0.15 * u)) for u in [i / n for i in range(n + 1)]]
                ws[0] = 0.05
                body = stroke_shape(pts, ws)
                core = stroke_shape(pts, [x * 0.42 for x in ws])
                gr = g_lin(fig, pts[0], pts[-1], [(0, tones[0]), (1, tones[1] if j == 0 else WIND[3])])
                fig.fx_front.append(outlined([(body, gr, 1), (core, WIND[0] if j == 0 else WIND[2], 0.85)], w=0.8, op=fade))
            # le grand croissant du souffle, devant, tourné vers l'ennemi
            R = 9.0 + 4.0 * t
            C = add(head, tg, -R + 2.0)
            a = ang_of(tg)
            cr = arc_band(C, R, a - 62, a + 62, 3.6, taper_=0.0, n=30)
            cr2 = arc_band(add(C, tg, -1.2), R - 1.6, a - 50, a + 50, 1.6, taper_=0.0, n=30)
            # bouts effilés : on reprend un croissant en lentille
            pts, ws = lens(C, R, a - 64, a + 64, 3.8)
            body = stroke_shape(pts, ws)
            pts2, ws2 = lens(C, R - 0.6, a - 50, a + 50, 1.5)
            core = stroke_shape(pts2, ws2)
            del cr, cr2
            gr = g_lin(fig, add(head, tg, -8), head, [(0, WIND[3]), (0.6, WIND[1]), (1, WIND[0])])
            fig.fx_front.append(glow(fig, head, 9, WIND[1], 0.35 * fade))
            fig.fx_front.append(outlined([(body, gr, 1), (core, '#ffffff', 0.9)], w=1.1, op=fade))
            # la plume emportée, qui tourne près du croissant
            fp = add(add(head, tg, -6), (-tg[1], tg[0]), -5 + 1.5 * math.sin(tl / 50))
            fig.fx_front.append(plume(fig, fp, a + 30 * math.sin(tl / 70) - 20, 1.05, op=fade))
        # l'impact : un éclat, deux volutes qui s'ouvrent (haut et bas), des bouffées
        if tl >= ATT_HIT - 10:
            u = (tl - ATT_HIT) / 340
            k2 = env(tl, ATT_HIT - 10, ATT_HIT + 30, ATT_HIT + 80, ATT_HIT + 260)
            fig.fx_front.append(pop(fig, HIT_AT, 4.6 * (0.7 + 0.6 * k2), facing=0, op=k2))
            ko = 1 - smooth((tl - ATT_HIT - 160) / 200)
            if 0 <= u <= 1.2 and ko > 0.02:
                g = smooth(min(1, u * 1.6))
                for s_, dy in ((-1, -1), (1, 1)):
                    q0 = add(HIT_AT, (-2, 2 * dy))
                    fig.fx_front.append(gust(fig, q0, add(q0, (5 * g, 8 * dy * g)), add(q0, (12 * g, 11 * dy * g)),
                                             add(q0, (16 * g, 6 * dy * g)), 2.6, curl=3.6 * g + 0.5, s=s_, tail=0.3 * u, op=ko))
                for j, (dx, dy, r) in enumerate(((6, -9, 3.4), (10, 6, 3.0), (-2, 12, 2.6), (14, -2, 2.2))):
                    fig.fx_front.append(puff(fig, HIT_AT[0] + dx * (0.5 + 0.7 * g), HIT_AT[1] + dy * (0.5 + 0.7 * g) - 3 * u,
                                             r * (0.6 + 0.6 * g) * (1 - 0.4 * u), op=ko * 0.95, k=j))
                fp = add(HIT_AT, (8 + 14 * u, -6 - 10 * u + 6 * u * u))
                fig.fx_front.append(plume(fig, fp, -20 + 160 * u, 1.05, op=ko))
    return f


# ---- 3) la spéciale

def ring_pts(c, rx, ry, a0, a1, n=40):
    return [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def wind_ring(fig, c, rx, ry, w, op, back):
    """L'anneau de vent qui s'élargit autour d'elle (posé à plat : une ellipse). La moitié de derrière passe derrière
    elle, celle de devant devant : deux rubans effilés aux bouts, un fil blanc dessus."""
    if op <= 0.02:
        return ''
    out = ''
    arcs = ((190, 350),) if back else ((10, 170),)
    for a0, a1 in arcs:
        pts = ring_pts(c, rx, ry, a0, a1, 36)
        ws = [max(0.05, w * math.sin(math.pi * i / 36) ** 0.6) for i in range(37)]
        body = stroke_shape(pts, ws)
        core = stroke_shape([(x, y - 0.25 * w) for x, y in pts], [x * 0.38 for x in ws])
        gr = g_lin(fig, pts[0], pts[-1], [(0, WIND[3]), (0.5, WIND[1]), (1, WIND[3])])
        out += outlined([(body, gr, 1), (core, '#ffffff', 0.85)], w=1.0, op=op * (0.75 if back else 1))
    return out


def gold_ring(fig, c, rx, ry, w, op, back):
    """L'anneau d'or au sol (même construction, en or)."""
    if op <= 0.02:
        return ''
    a0, a1 = (190, 350) if back else (10, 170)
    pts = ring_pts(c, rx, ry, a0, a1, 36)
    ws = [max(0.05, w * math.sin(math.pi * i / 36) ** 0.6) for i in range(37)]
    body = stroke_shape(pts, ws)
    core = stroke_shape([(x, y - 0.25 * w) for x, y in pts], [x * 0.4 for x in ws])
    gr = g_lin(fig, pts[0], pts[-1], [(0, GOLDFX[3]), (0.5, GOLDFX[1]), (1, GOLDFX[3])])
    return outlined([(body, gr, 1), (core, GOLDFX[0], 0.9)], ink='#5a2a18', w=0.9, op=op * (0.8 if back else 1))


# les taches sombres sur elle (repère du dessin au repos) : apparaissent à l'éclair, se détachent, s'évaporent
SPECKS = [(66, 64, 1.3), (80, 84, 1.1), (58, 92, 1.2), (74, 98, 1.0), (40, 50, 1.1), (98, 40, 1.0), (52, 76, 0.9),
          (86, 66, 0.9), (30, 70, 1.0), (104, 60, 0.9)]
# la pluie de plumes de lumière : (angle autour d'elle, départ, hauteur de départ, tournoiement)
RAIN = [(200, 880, -18, 1.0), (330, 930, -30, -1.0), (20, 960, -22, 1.0), (140, 1000, -34, -1.0), (260, 1040, -16, 1.0),
        (80, 1090, -28, -1.0), (300, 1140, -20, 1.0), (170, 1180, -32, -1.0), (40, 1230, -26, 1.0), (230, 1280, -24, -1.0),
        (110, 1330, -30, 1.0), (350, 1380, -18, -1.0)]


def fx_special(tl):
    def f(fig, ctx):
        P = ctx['P']
        lift = P['lift']
        waist = ctx['waist']
        feet = (CEN[0], CEN[1])
        # ---- le vent se lève à ses pieds (elle se ramasse) ----
        k = env(tl, 0, 120, 300, 460)
        if k > 0:
            sp = (tl / 1000) * 360 * 1.4
            for j, (rx, ry, w, a0) in enumerate(((22, 4.2, 2.0, 0), (30, 5.8, 1.6, 150))):
                fig.fx_back.append(wind_ring(fig, (feet[0], feet[1] - 2 - 4 * j * k), rx * (0.7 + 0.3 * k), ry, w, k * 0.9, True))
                fig.fx_front.append(wind_ring(fig, (feet[0], feet[1] - 2 - 4 * j * k), rx * (0.7 + 0.3 * k), ry, w, k * 0.9, False))
            for j in range(3):
                a = math.radians(sp + 120 * j)
                q = (feet[0] + 20 * math.cos(a), feet[1] - 3 - 6 * k * (j % 2))
                fig.fx_front.append(gust(fig, q, add(q, (-3, -4)), add(q, (2, -9)), add(q, (6, -10)), 1.5, curl=2.4, s=1, op=k * 0.8))
        # ---- l'élan : rafales qui descendent sous les ailes quand elle s'élève ----
        for t0, t1 in ((300, 640), (690, 1000)):
            kd = env(tl, t0, t0 + 80, t1 - 120, t1)
            if kd > 0:
                u = (tl - t0) / (t1 - t0)
                for j, x in enumerate((30, 104)):
                    s_ = -1 if j == 0 else 1
                    q0 = (x, 70 - lift + 18 * u)
                    fig.fx_back.append(gust(fig, q0, add(q0, (0, 10)), add(q0, (-4 * s_, 22)), add(q0, (-8 * s_, 30 * (0.6 + 0.4 * u))),
                                            2.2, curl=3.4, s=s_, tail=0.4 * u, op=kd * 0.85))
                fig.fx_back.append(puff(fig, feet[0] - 26 - 6 * u, GR - 2, 2.4 + 1.6 * u, op=kd * 0.8, k=1))
                fig.fx_back.append(puff(fig, feet[0] + 26 + 6 * u, GR - 2, 2.4 + 1.6 * u, op=kd * 0.8, k=0))
        # ---- l'auréole s'illumine : une lueur douce autour d'elle ----
        gh = min(1.6, P['glow'])
        if gh > 0:
            fig.under.append((ctx['halo'][0], ctx['halo'][1], 22 + 6 * gh, 10 + 3 * gh, GOLDFX[1], 0.25 * gh, None))
        # ---- 1re note : éclair doux blanc et or au pavillon, la silhouette s'éclaire ----
        kf = env(tl, SP_BLOW - 20, SP_BLOW, SP_BLOW + 60, SP_BLOW + 260)
        if kf > 0:
            b = ctx['bell']
            fig.fx_front.append(glow(fig, b, 30 * kf, '#ffffff', 0.7 * kf))
            fig.fx_front.append(pop(fig, b, 4.0 * (0.6 + 0.5 * kf), facing=ctx['tang'], op=kf, gold=True))
        au = P.get('aura', 0.0)
        if au > 0.02:
            fig.aura = (GOLDFX[1], 1.3 * au, 0.85 * au)
        # ---- l'anneau de vent naît autour de sa taille et s'élargit tout autour d'elle ----
        if SP_BLOW - 10 <= tl <= 1300:
            u = smooth((tl - SP_BLOW) / 420)
            op = env(tl, SP_BLOW - 10, SP_BLOW + 30, 1000, 1300)
            rx = 12 + 92 * u
            ry = rx * 0.26
            c = (waist[0], waist[1] + 18 * u + 4)
            w = 3.4 - 1.4 * u
            fig.fx_back.append(wind_ring(fig, c, rx, ry, w, op, True))
            fig.fx_front.append(wind_ring(fig, c, rx, ry, w, op, False))
            # le second anneau, plus fin, en retard
            if tl > SP_BLOW + 80:
                u2 = smooth((tl - SP_BLOW - 80) / 420)
                rx2 = 10 + 70 * u2
                fig.fx_back.append(wind_ring(fig, (waist[0], waist[1] + 12 * u2 + 2), rx2, rx2 * 0.26, 2.0 - 0.8 * u2, op * 0.8, True))
                fig.fx_front.append(wind_ring(fig, (waist[0], waist[1] + 12 * u2 + 2), rx2, rx2 * 0.26, 2.0 - 0.8 * u2, op * 0.8, False))
            # il se défait en volutes, au bord
            if tl > 980:
                v = (tl - 980) / 320
                for j, a in enumerate((20, 160, 200, 340)):
                    q = (c[0] + rx * math.cos(math.radians(a)), c[1] + ry * math.sin(math.radians(a)))
                    s_ = 1 if math.cos(math.radians(a)) > 0 else -1
                    fig.fx_front.append(gust(fig, q, add(q, (4 * s_, -3)), add(q, (8 * s_, -7)), add(q, (10 * s_, -12 * v - 2)),
                                             1.6, curl=2.4 + 2 * v, s=-s_, tail=0.5 * v, op=(1 - v) * 0.9))
        # ---- les taches sombres : elles apparaissent à l'éclair, se détachent et s'évaporent ----
        if SP_BLOW - 60 <= tl <= 1320:
            body = ctx['BODY']
            for j, (x, y, r) in enumerate(SPECKS):
                p = mapp(body, (x, y))
                a_in = env(tl, SP_BLOW - 60 + 8 * j, SP_BLOW + 10 + 8 * j, 900, 1320)
                d = max(0.0, (tl - 880 - 20 * j) / 400)
                q = add(p, (6 * d * math.cos(j * 1.7), -16 * d - 4 * d * d))
                col = SPECK[0] if d < 0.2 else SPECK[1] if d < 0.55 else SPECK[2]
                rr = r * (1 + 0.6 * d)
                if a_in > 0.02:
                    blob = sm([add(q, (rr, 0)), add(q, (0.2 * rr, 0.9 * rr)), add(q, (-rr, 0.2 * rr)), add(q, (-0.3 * rr, -rr))], t=0.95)
                    fig.over.append('<path d="%s" fill="%s" opacity="%g"/>' % (blob.d(), col, a_in * (1 - 0.6 * d)))
        # ---- la pluie de plumes de lumière, en cercle autour d'elle ----
        for j, (a, t0, h0, tw) in enumerate(RAIN):
            if t0 <= tl <= t0 + 820:
                u = (tl - t0) / 620
                ex, ey = 70 * math.cos(math.radians(a)), 15 * math.sin(math.radians(a))
                fall = smooth(min(1, u))
                x = feet[0] + ex + 3 * math.sin(u * 7 + j) * (1 - fall)
                y = (h0 + (GR - 1 + ey - h0) * fall)
                op = env(tl, t0, t0 + 80, t0 + 600, t0 + 820)
                ang = 20 * tw * math.sin(u * 6 + j) - 10 + 30 * fall * tw
                layer = fig.fx_back if math.sin(math.radians(a)) < 0 else fig.fx_front
                layer.append(plume(fig, (x, y), ang, 0.95, op=op, light=True))
                if u >= 1:
                    layer.append(sparkle(fig, (x, y - 1), 1.6 * (1 - (u - 1) / 0.32), op, rot=10 * j))
        # ---- 2de note : l'auréole s'embrase, le grand halo doré pulse une fois, un anneau d'or au sol ----
        kn = env(tl, SP_NOTE2 - 40, SP_NOTE2, SP_NOTE2 + 200, SP_NOTE2 + 480)
        if kn > 0:
            c = (waist[0], waist[1] - 10)
            u = smooth((tl - SP_NOTE2 + 40) / 260)
            R = 30 + 34 * u
            fig.under.append((c[0], c[1], R, R, GOLDFX[1], 0.3 * kn, [(0, GOLDFX[0], 0.0), (0.72, GOLDFX[1], 0.18 * kn), (0.9, GOLDFX[0], 0.55 * kn), (1, GOLDFX[1], 0)]))
            ring_ = sm([(c[0] + R * math.cos(math.radians(i * 12)), c[1] + R * math.sin(math.radians(i * 12))) for i in range(30)], t=0.9)
            inner = sm([(c[0] + (R - 1.6) * math.cos(math.radians(i * 12)), c[1] + (R - 1.6) * math.sin(math.radians(i * 12))) for i in range(30)], t=0.9)
            from lib import Shape
            band = Shape(ring_.subs + inner.rev().subs, evenodd=True)
            fig.fx_back.append('<path d="%s" fill-rule="evenodd" fill="%s" opacity="%g"/>' % (band.d(), GOLDFX[1], 0.8 * kn))
            for j in range(10):
                a = j * 36 + 12 * u
                fig.fx_front.append(sparkle(fig, (c[0] + R * math.cos(math.radians(a)), c[1] + R * math.sin(math.radians(a))),
                                            1.4 + 0.8 * ((j * 7) % 3) / 2, kn, rot=a))
            gx = (feet[0], GR - 0.5)
            fig.fx_back.append(gold_ring(fig, gx, 26 + 30 * u, (26 + 30 * u) * 0.2, 2.4, kn, True))
            fig.fx_front.append(gold_ring(fig, gx, 26 + 30 * u, (26 + 30 * u) * 0.2, 2.4, kn, False))
        # les lueurs qui montent, après la seconde note
        if SP_NOTE2 + 100 <= tl <= SP_NOTE2 + 820:
            for j in range(9):
                t0 = SP_NOTE2 + 100 + 50 * j
                if t0 <= tl <= t0 + 560:
                    u = (tl - t0) / 560
                    a = math.radians(j * 40 + 15)
                    x = feet[0] + 44 * math.cos(a) * (1 - 0.3 * u)
                    y = GR - 4 + 10 * math.sin(a) - 46 * u
                    fig.fx_front.append(sparkle(fig, (x, y), 1.3 * (1 - 0.5 * u), env(u, 0, 0.15, 0.6, 1.0), rot=30 * j))
    return f


# ---- les éclats sur les ors pendant la pose (un à la fois)

def fx_glints(T):
    def f(fig, ctx):
        t = T % 2.0
        spots = [
            (0.1, lambda: ctx['bell']),                                    # le pavillon
            (0.6, lambda: mapp(ctx['HEAD'], (M.HALO_C[0] + 8, M.HALO_C[1] - 2.6))),   # l'auréole
            (1.0, lambda: mapp(ctx['UC'], (58.4, 52.0))),                  # l'épaulière
            (1.5, lambda: mapp(ctx['U'], (75.6, 71.0))),                   # la boucle de la ceinture
        ]
        for t0, pos in spots:
            k = env(t, t0, t0 + 0.1, t0 + 0.14, t0 + 0.3)
            if k > 0:
                fig.over.append(sparkle(fig, pos(), 1.9 * k, k, rot=8))
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


def shadow_layer(w, h, view, lift=0.0, floor_y=GR):
    """L'ombre au sol sous elle (elle rétrécit quand elle s'élève)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (68 - x0) * k
    s = max(0.55, 1 - lift / 30)
    ImageDraw.Draw(sh).ellipse([cx - 30 * k * s, fy - 3.0 * k * s, cx + 30 * k * s, fy + 3.0 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


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
    return M.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


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
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-myrr-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load('myrr'), 0), 'RGBA')
    ref = out[0][0] if name == 'pose' else out[-1][0]
    bg = Image.new('RGBA', ref.size, (232, 236, 242, 255))
    bg.alpha_composite(ref)
    ox, oy = find_offset(sprite, bg)
    return out, (ox, oy)


def game_size_part():
    """Partie 2 : à la taille du jeu, sur le vrai fond de combat d'un clan du vent, le pixel art à gauche et le
    vectoriel à droite, à la même échelle, la même suite : pose, attaque, pose, spéciale, pose."""
    fond = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'eldra.webp')).convert('RGBA')
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


def compose(pngs, lifts, w, h, view):
    bg = background(w, h, view)
    for p, lf in zip(pngs, lifts):
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view, lf))
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
        moments = [1.0, 1.5, a_s + 0.2, a_s + 0.33, a_s + 0.42, a_s + 0.5, a_s + 0.62, a_s + 0.8,
                   s_s + 0.2, s_s + 0.45, s_s + 0.69, s_s + 0.8, s_s + 1.0, s_s + 1.2, s_s + 1.33, s_s + 1.6]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, [r[1]['lift'] for r in res], 640, 360, VIEW)
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
    compose(pngs, [r[1]['lift'] for r in res], VW, VH, VIEW)
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
