# Kesha vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/kesha/build.py) —
# le prédateur à l'affût (respiration), attaque de base « Coup de scie », attaque spéciale « Grand blanc » — dans le
# style lisse de l'interface (comme Kael : heros/kael/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/kesha/anim.py              # → anim.mp4 + anim.gif (sortie/ui/vecto/kesha/)
#   python3 refonte-graphique/ui-moderne/heros/kesha/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#
# Méthode : chaque image redessine kesha.py dans une POSE (buste qui respire et se penche depuis les hanches, tête et
# gueule qui s'ouvre autour de sa charnière, branchies qui battent, queue qui se balance et fouette, pagne et dents
# pendues qui suivent, griffe qui se replie ; la lame-scie avance dans son axe, le bras lointain suit par cinématique
# inverse). Les poses clés reprennent celles du pixel art (mêmes temps : ramassé tenu, fente très courte, arrêt sur
# l'impact, arrachement sec, retour en glissant), reliées par des courbes douces sans dépassement, 24 images/s.
# Les effets d'eau (traînée, gerbes, gouttes, écume, couronne, sillage, geyser) sont ceux des héros d'eau vectoriels
# (mêmes outils et couleurs qu'Ilian) : dégradés, un seul contour bleu nuit, aucun flou.
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import kesha as K  # noqa: E402
from atelier import lock, sm, ribbon, ellipse, f as fm  # noqa: E402
from outils import taper, crpath  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'kesha')
TMP = os.environ.get('KESHA_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-26, -44, 290, 163.125)      # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WINK = '#0c1846'                     # le contour de l'eau (bleu nuit presque noir, comme Ilian)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']
ENTRY_X = 96.0                       # où il plonge dans le sol
GEY_X = 206.0                        # le milieu de la gerbe (sous l'ennemi)
XE = 116.0                           # sa glissade quand il jaillit : sa gueule arrive sur l'ennemi
HOME_X = 70.0                        # où il ressurgit, chez lui

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


PAIRS = {'head': ('headx', 'heady'), 'na': ('nax', 'nay'), 'arm': ('armx', 'army')}
SCAL = ['crouch', 'lean', 'tilt', 'gape', 'gill', 'q', 'qw', 'pan', 'curl', 'ang', 'shift', 'drop', 'pitch']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: 0.0 for n in NUM}
    d['ang'] = K.ANG0
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


# ======================================================================== les actions (poses clés, en ms)
# 2) « Coup de scie » (pixel : ATTAQUE). Il se ramasse (tenu) : mâchoires serrées, lame tirée en arrière contre le flanc,
# griffe armée, queue dressée. Il fond sur l'ennemi en fente (il glisse), la gueule s'ouvre en grand, la lame plonge
# dans son axe (traînée d'eau) et frappe : arrêt sur l'image, gerbe au bout de la lame. Il ARRACHE la scie d'un coup
# sec (les dents d'ivoire projettent l'eau, la gueule claque), puis revient en glissant à sa garde.
AX = (0.8, -0.6)
CROUCH = dict(crouch=2.2, lean=-2.4, head=(-1.2, 1.0), tilt=-3, arm=(-5, 3), gape=-1.6, q=2.6, qw=1.0, pan=1.2,
              na=(-2.2, -1.2), gill=1, curl=0.7)
ATTACK = [
    (0, {}),
    (90, dict(crouch=0.6, lean=-0.6, arm=(-1.2, 0.7), q=0.6, curl=0.2)),
    (300, CROUCH),
    (380, dict(CROUCH, crouch=2.4, lean=-2.7, arm=(-5.6, 3.3), q=2.9, qw=1.4)),
    (425, dict(shift=11, crouch=1.2, lean=2, head=(1, 0), tilt=1, arm=(4, -2.4), gape=3, q=-1.5, qw=-1.5, pan=-1,
               na=(1, 0), curl=0.4)),
    (465, dict(shift=23, crouch=1.0, lean=3.2, head=(2, 0), tilt=2, arm=(13.6, -8.2), gape=6, q=-2.6, qw=-2.4, pan=-2,
               na=(2, 1), curl=0.3)),
    (490, dict(shift=25, crouch=1.2, lean=3.4, head=(2.2, 0.2), tilt=2.4, arm=(14.2, -8.6), gape=6.2, q=-2.2, qw=-1.2,
               pan=-2, na=(2, 1), curl=0.3)),
    (640, dict(shift=25, crouch=1.3, lean=3.3, head=(2.1, 0.3), tilt=2.2, arm=(14.0, -8.4), gape=5.8, q=-1.6, qw=0.4,
               pan=-1.6, na=(2, 1), curl=0.3)),
    (700, dict(shift=22, crouch=1.2, lean=2, head=(1, 1), tilt=-1, arm=(3.6, 1.2), gape=-2, q=0.4, qw=1.6, pan=-1,
               na=(1, 0), gill=1, curl=0.6)),
    (800, dict(shift=12, crouch=1.0, lean=1, head=(0, 1), arm=(1, 1.6), gape=-1, q=-0.6, qw=0.6, pan=0.2, curl=0.4)),
    (910, dict(shift=4, crouch=0.9, lean=0.2, head=(0, 0.4), arm=(0, 0.8), q=-1.0, qw=-0.6, pan=1, curl=0.2)),
    (1030, dict(crouch=0.7, head=(0, 0.6), q=-0.4, pan=0.8)),
    (1180, {}),
]
ATTACK_HIT = 490

# 3) « Grand blanc » (pixel : SPECIALE). Il se ramasse en fixant le sol (tenu), bondit et plonge dans le sol comme dans
# l'eau (couronne d'eau). Seul l'aileron dépasse et FILE vers l'ennemi en fendant le sol (vague d'étrave, sillage).
# Sous l'ennemi l'aileron s'enfonce, le sol bouillonne (tenu)… puis il JAILLIT dans une énorme gerbe, gueule grande
# ouverte, et MORD (arrêt sur l'image, éclat d'écume). Il secoue sa proie, retombe dans la gerbe qui s'effondre en
# pluie ; il ressurgit chez lui dans un rejaillissement, retombe accroupi et revient en garde.
FIN_DROP = GR - 19.0 - 1.6           # l'aileron seul dépasse (sa pointe 19 px au-dessus du sol)
SPECIAL = [
    (0, {}),
    (170, dict(crouch=2.2, lean=1, head=(1, 2), tilt=4, gape=-2, arm=(-2, 2), q=2.8, qw=1, pan=1, na=(-1, 1), gill=1, curl=0.6)),
    (300, dict(crouch=2.6, lean=1.4, head=(1, 2.4), tilt=5, gape=-2.2, arm=(-2.4, 2.4), q=3.2, qw=1.6, pan=1.2, na=(-1, 1.2), gill=1, curl=0.7)),
    (370, dict(shift=8, drop=-10, crouch=-0.6, lean=3, pitch=-12, head=(2, 0), tilt=-2, gape=2, arm=(2, -1), q=-2.6, qw=-2, pan=-2, na=(1, -1))),
    (430, dict(shift=18, drop=34, lean=3, pitch=32, head=(2, 1), gape=1, arm=(2, -1), q=-1, qw=1.6, pan=-2)),
    (500, dict(shift=26, drop=84, lean=3, pitch=40, head=(2, 1), arm=(2, -1), q=1, qw=1)),
    (560, dict(shift=40, drop=FIN_DROP + 3, pitch=0)),
    (620, dict(shift=76, drop=FIN_DROP)),
    (690, dict(shift=114, drop=FIN_DROP)),
    (760, dict(shift=146, drop=FIN_DROP + 1)),
    (830, dict(shift=156, drop=FIN_DROP + 9)),
    (950, dict(shift=158, drop=FIN_DROP + 14)),
    (951, dict(shift=XE, drop=96, pitch=-24)),
    (1010, dict(shift=XE, drop=50, pitch=-14, lean=2, head=(1, -1), tilt=-4, gape=7, arm=(3, -2), q=3, qw=-1, pan=-2, na=(1, -2))),
    (1080, dict(shift=XE, drop=10, pitch=-6, lean=2, head=(1, -2), tilt=-6, gape=9, arm=(3, -2), q=2, qw=1.6, pan=-2, na=(1, -2))),
    (1130, dict(shift=XE + 3, drop=7, pitch=4, lean=3.4, head=(2.4, 0), tilt=3, gape=-3, arm=(3, -2), q=-2, qw=-1.6, pan=1, na=(2, 0), gill=1)),
    (1340, dict(shift=XE + 3, drop=7, pitch=4, lean=3.2, head=(2.2, 0.2), tilt=2.6, gape=-3, arm=(3, -2), q=-1.6, qw=1, pan=0.6, na=(2, 0), gill=1)),
    (1400, dict(shift=XE - 1, drop=11, pitch=-3, lean=1, head=(-0.6, 1.2), tilt=-5, gape=-3, arm=(3, -2), q=2.4, qw=-2, pan=0, na=(1, 0))),
    (1460, dict(shift=XE + 1, drop=14, pitch=4, lean=2, head=(1.4, 0.4), tilt=4, gape=-2.6, arm=(3, -2), q=-2, qw=2, pan=0.6)),
    (1560, dict(shift=XE - 4, drop=96, pitch=18, lean=1, head=(0, 1), gape=-1, arm=(3, -2), q=-2)),
    (1561, dict(shift=0, drop=96, pitch=-10, q=2)),
    (1640, dict(shift=0, drop=44, pitch=-8, head=(0, -1), gape=1, q=3, qw=-1, pan=-1)),
    (1720, dict(shift=0, drop=8, pitch=-2, head=(0, -1), gape=1, q=2, qw=1.4, pan=-1)),
    (1810, dict(crouch=2.2, lean=-1, head=(0, 1), q=-1, qw=-1, pan=1, curl=0.4)),
    (1930, dict(crouch=1, head=(0, 1), pan=0.4)),
    (2080, {}),
]
SP_BITE = 1130
SP_CUT = (400, 1760)


# ======================================================================== la respiration (en boucle, 3 s)

IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (2 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : sa queue de requin en croissant ondule lentement, comme dans l'eau (elle se balance, la pointe fouette
    en retard).
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(q=2.6 * math.sin(u - 0.4), qw=2.4 * math.sin(u - 1.6))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u)
    g = max(0.0, math.sin(2 * u - 0.6)) ** 2
    return dict(breath=br, crouch=0.4 * (0.5 - 0.5 * math.cos(u - 1.3)), heady=0.3 * math.sin(u - 0.6),
                tilt=0.8 * math.sin(u - 0.9), gape=0.7 + 0.7 * math.sin(u - 1.2), gill=0.8 * g,
                q=1.0 * math.sin(u - 0.4), qw=1.1 * math.sin(u - 1.6), pan=0.8 * math.sin(u + 0.5),
                nay=0.5 * math.sin(u - 0.9), nax=0.3 * math.sin(u - 1.4), curl=0.25 + 0.2 * math.sin(u - 0.3),
                army=0.45 * math.sin(u - 1.0), armx=0.2 * math.sin(u - 1.2))


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : respiration (pondérée) + action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 220), max(0.0, (tl - (dur - 320)) / 320))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    for n, v in signe(T).items():
        P[n] += w * v
    P['breath'] = w * idl['breath']
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['na'] = (P.pop('nax'), P.pop('nay'))
    P['arm'] = (P.pop('armx'), P.pop('army'))
    P['blink'] = 1.0 if (w > 0.95 and 1.28 <= (T % IDLE_T) < 1.36) else 0.0
    P['cut'] = action == 'special' and SP_CUT[0] <= tl <= SP_CUT[1]
    return P, tl


# ======================================================================== l'eau (mêmes outils et couleurs qu'Ilian)

def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops):
    return fig.rad(c[0], c[1], r, r, stops)


def outlined(shapes_fills, ink=WINK, w=1.3, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ;
    une 4e valeur dans un élément = pas de silhouette pour lui (un reflet peint dedans)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    # un effet qui s'efface rétrécit surtout : l'opacité ne descend qu'à la toute fin (pas de fantôme sombre)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, 2 * op)), sil, col)


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


def stream(fig, pts, w0, w1, op=1.0):
    """Un filet d'eau le long d'une courbe (traînée de la lame, eau arrachée) : fin derrière, plein devant, crête claire."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=20)
    sh = taper(c, w0, w1, tip='round')
    crest = taper([(x + 0.25, y - 0.35) for x, y in c[4:]], w0 * 0.2, w1 * 0.3, tip='round')
    gr = g_lin(fig, c[0], c[-1], [(0, WATER[3]), (0.6, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.85, 'n')], w=1.1, op=op)


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


def splash_crown(fig, X, k, big=1.0, seed=0):
    """La couronne d'eau là où il entre dans le sol (ou en ressort) : des nappes qui s'ouvrent en couronne, de
    l'écume, des gouttes (k : 0 → 1 le temps de l'éclaboussure)."""
    out_b, out_f = [], []
    if k <= 0 or k >= 1:
        return out_b, out_f
    e = math.sin(math.pi * min(1, k * 1.25)) if k < 0.8 else max(0, (1 - k) / 0.2) * math.sin(math.pi * 0.999)
    e = max(0.0, e)
    for j, (dx, ang, L, bd, w) in enumerate(((-6, -122, 15, -40, 3.6), (-2.5, -100, 21, -20, 4.2), (2.5, -80, 20, 22, 4.2),
                                              (6, -58, 15, 40, 3.6), (0, -90, 12, 0, 3.0))):
        L_ = L * big * (0.4 + 0.6 * min(1, k * 2.2)) * (1 - 0.35 * max(0, k - 0.5) * 2)
        (out_b if j in (0, 3, 4) else out_f).append(sheet(fig, (X + dx * big, GR + 0.2), ang, L_, bd, w * big, op=min(1, e * 1.6), tail=max(0, k - 0.45) * 1.2))
    out_f.append(mound(fig, X, 5 * big * e, 14 * big, op=min(1, e * 1.5)))
    for j, (vx, vy) in enumerate(((-55, -120), (40, -135), (-90, -80), (85, -95), (-20, -150), (15, -160), (110, -60))):
        tau = k * 0.7 - 0.03 * (j % 3)
        if 0 < tau < 0.7:
            x, y = ballistic((X, GR - 3), (vx * big, vy * big), 330, tau)
            if y < GR:
                out_f.append(drop(fig, x, y, vx, vy + 330 * tau, 1.1 if j % 2 else 0.85))
    for j in range(3):
        out_f.append(foam(fig, X - 7 * big + 7 * big * j, GR - 1.2, 1.8 * big * e, op=min(1, e * 1.5), seed=j + seed))
    return out_b, out_f


# ---- l'attaque de base : traînée de la lame, gerbe à la pointe, eau arrachée par les dents

HIT = {}


def fx_attack(tl, path):
    """path : les positions récentes de la pointe (pour la traînée)."""
    def f(fig, ctx):
        tip = ctx['tip']
        if 400 <= tl <= 520 and len(path) >= 2:
            k = env(tl, 400, 430, 490, 530)
            pts = path + [tip]
            fig.fx_back.append(stream(fig, pts, 0.6, 4.4 * k + 0.5, op=min(1, 3 * k)))
        tau = (tl - ATTACK_HIT) / 1000.0
        if tau >= 0:
            if 'c' not in HIT:
                HIT['c'] = tip
            X, Y = HIT['c']
            e = env(tau, 0, 0.03, 0.16, 0.42)
            for j, (ang, L, bd, w) in enumerate(((-48, 20, -50, 4.6), (12, 16, -40, 4.0), (-112, 12, 40, 3.2), (-80, 14, 20, 3.4))):
                L_ = L * (0.45 + 0.55 * min(1, tau / 0.12))
                (fig.fx_back if j < 2 else fig.fx_front).append(sheet(fig, (X - 1, Y), ang, L_ * (0.3 + 0.7 * e), bd, w * (0.4 + 0.6 * e), op=min(1, 3 * e), tail=max(0, tau - 0.15) * 2.2))
            pe = env(tau, 0, 0.02, 0.1, 0.3)
            if pe > 0:
                fig.fx_front.append(foam(fig, X + 2.5, Y - 0.5, 4.6 * pe + 1.2, op=pe, seed=1))
            for j, (vx, vy) in enumerate(((60, -95), (95, -40), (30, -125), (85, 15), (-15, -110), (115, -70), (50, -20))):
                if tau < 0.75:
                    x, y = ballistic((X + 2, Y), (vx, vy), 260, tau)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 260 * tau, 1.0 if j % 2 else 0.75, op=min(1, (0.75 - tau) * 4)))
            # l'arrachement : un filet d'eau suit les dents, puis une volée de gouttes part des dents
            r0 = 640
            if tl >= r0:
                tr = (tl - r0) / 1000.0
                if 'teeth' not in HIT:
                    HIT['teeth'] = [t_ for t_ in ctx['teeth']]
                ek = env(tr, 0, 0.03, 0.07, 0.2)
                if ek > 0:
                    T1 = ctx['teeth'][1]
                    pts = [(X, Y + 3), (X - 3, Y + 7), ((X + T1[0]) / 2, (Y + T1[1]) / 2 + 6), (T1[0] + 1, T1[1] + 2)]
                    fig.fx_back.append(stream(fig, pts, 0.6, 3.6 * ek + 0.4, op=min(1, 3 * ek)))
                RIPV = [[(-34, -96), (22, -128)], [(-70, -62), (4, -150), (40, -84)], [(-12, -118), (-52, -40)], [(30, -60), (-26, -140)]]
                for j, Tt in enumerate(HIT['teeth']):
                    for m, (vx, vy) in enumerate(RIPV[j % 4]):
                        tt = tr - 0.02 * ((j + m) % 3)
                        if 0 < tt < 0.6:
                            x, y = ballistic(Tt, (vx, vy), 300, tt)
                            if y < GR:
                                fig.fx_front.append(drop(fig, x, y, vx, vy + 300 * tt, 0.8 + 0.15 * ((j + m) % 2), op=min(1, (0.6 - tt) * 5)))
    return f


# ---- l'attaque spéciale

def fx_special(tl):
    def f(fig, ctx):
        t = tl
        # 1) la plongée : la couronne d'eau là où il entre
        if 400 <= t <= 1000:
            b, fr = splash_crown(fig, ENTRY_X, (t - 400) / 560.0, 1.0)
            fig.fx_back += b
            fig.fx_front += fr
        # 2) l'aileron file : vague d'étrave devant, sillage d'eau sombre et nappes derrière
        if 520 <= t <= 1000:
            fx_ = ctx['fin'][0]
            ew = env(t, 520, 580, 830, 1000)
            run = env(t, 520, 560, 760, 860)
            x0 = ENTRY_X + 4
            if fx_ > x0 + 2:
                wk = [(x0 + (fx_ - x0) * i / 8, GR - 0.6 - 0.4 * math.sin(i * 1.3 + t / 60.0)) for i in range(9)]
                band = taper(wk, 0.4, 3.2 * ew + 0.4, tip='round')
                gb = g_lin(fig, (x0, GR), (fx_, GR), [(0, WATER[4], 0.3 * ew), (1, WATER[3], ew)])
                fig.fx_back.append('<path d="%s" fill="%s"/>' % (band.d(), gb))
                for j in range(4):
                    xx = fx_ - 10 - 16 * j - (t / 12.0) % 16
                    if xx > x0:
                        fig.fx_front.append(foam(fig, xx, GR - 0.8, 1.3 * ew * (1 - 0.15 * j), op=ew * (1 - 0.2 * j), seed=j))
            fig.fx_front.append(mound(fig, fx_ + 6, 4.5 * ew + 2.5 * run, 9 + 3 * run, op=ew))
            fig.fx_back.append(sheet(fig, (fx_ + 8, GR), -50, 10 * run + 2, 40, 3.2, op=ew * run))
            fig.fx_back.append(sheet(fig, (fx_ - 4, GR), -140, 8 * run + 2, -30, 2.8, op=ew * run))
            for j in range(5):
                tt = ((t - 520) / 1000.0 + j * 0.07) % 0.35
                x, y = ballistic((fx_ + 4, GR - 2), (40 + 15 * j, -70 - 10 * j), 320, tt)
                if y < GR and run > 0.2:
                    fig.fx_front.append(drop(fig, x, y, 40, -70 + 320 * tt, 0.8, op=run))
        # 3) sous l'ennemi : le sol bouillonne (tenu), puis la grande gerbe jaillit, tient, et s'effondre en pluie
        if 800 <= t <= 1900:
            X = GEY_X
            bub = env(t, 800, 860, 940, 1000)
            if bub > 0:
                fig.fx_back.append(mound(fig, X, 5 * bub + 1.2 * math.sin(t / 25.0), 18, op=bub))
                for j in range(4):
                    ph = (t / 70.0 + j * 0.7) % 1
                    fig.fx_front.append(foam(fig, X - 12 + 8 * j, GR - 2 - 4 * ph, 1.4 * (1 - ph) + 0.4, op=bub * (1 - ph), seed=j))
            if t >= 950:
                tg = (t - 950) / 1000.0
                # elle monte d'un coup, tient, puis s'effondre : elle maigrit et se défait en pluie (le sommet ne
                # redescend pas à travers lui)
                up = env(tg, 0, 0.12, 0.5, 0.68)
                rise = env(tg, 0, 0.12, 0.5, 0.7)
                top = GR - 112 * up
                wb = (30 + 8 * up) * (0.75 + 0.25 * rise)
                wt = (18 + 8 * up) * (0.75 + 0.25 * rise)
                if rise > 0:
                    fig.fx_back.append(column(fig, X, top, wb, wt, 3 * math.sin(tg * 6), tg, op=min(1, rise * 1.6)))
                    fig.fx_front.append(mound(fig, X, 12 * rise, 30, op=min(1, rise * 2.5)))
                    for j, (dx, ang, L, bd) in enumerate(((-16, -150, 18, -40), (16, -30, 18, 40), (-10, -125, 14, -30), (10, -55, 14, 30))):
                        fig.fx_front.append(sheet(fig, (X + dx, GR), ang, L * rise, bd, 4.4, op=min(1, rise * 2)))
                # la pluie : la gerbe s'effondre, des gouttes partent de ses bords et retombent (en désordre)
                RAIN = [(-0.9, 0.62, -55, 0.38), (0.8, 0.48, 60, 0.4), (-0.5, 0.85, -30, 0.44), (0.3, 0.92, 25, 0.42),
                        (1.0, 0.7, 75, 0.47), (-1.0, 0.3, -70, 0.5), (0.6, 0.25, 45, 0.53), (-0.2, 0.55, -15, 0.49),
                        (0.15, 0.75, 10, 0.56), (-0.7, 0.45, -45, 0.58), (0.9, 0.9, 35, 0.6), (-0.35, 0.98, -20, 0.62)]
                for j, (sx, hy, vx, st) in enumerate(RAIN):
                    tt = tg - st - 0.1
                    if 0 < tt < 0.6:
                        p0 = (X + sx * 13, GR - 104 * hy)
                        x, y = ballistic(p0, (vx, -25 - 10 * (j % 3)), 360, tt)
                        if y < GR:
                            fig.fx_front.append(drop(fig, x, y, vx, -25 + 360 * tt, 1.3 if j % 3 == 0 else 0.95, op=min(1, (0.6 - tt) * 6)))
                pud = env(tg, 0.4, 0.55, 0.75, 0.95)
                if pud > 0:
                    fig.fx_front.append(mound(fig, X, 3.5 * pud, 26, op=pud, foamy=0.7))
        # 4) il MORD : l'éclat d'écume sur la gueule, des gouttes
        tb = (t - SP_BITE) / 1000.0
        if 0 <= tb < 0.6:
            M = ctx['mouth']
            pe = env(tb, 0, 0.02, 0.12, 0.3)
            if pe > 0:
                fig.fx_front.append(foam(fig, M[0] + 4, M[1] - 1, 5.5 * pe + 1, op=pe, seed=2))
                fig.fx_front.append(foam(fig, M[0] + 8, M[1] + 3, 3.2 * pe + 0.6, op=pe, seed=1))
            for j, (vx, vy) in enumerate(((70, -90), (100, -30), (40, -120), (-10, -100), (90, 20), (130, -60))):
                x, y = ballistic((M[0] + 5, M[1]), (vx, vy), 280, tb)
                if y < GR:
                    fig.fx_front.append(drop(fig, x, y, vx, vy + 280 * tb, 1.0 if j % 2 else 0.8, op=min(1, (0.6 - tb) * 4)))
        # 5) il ressurgit chez lui : un rejaillissement, puis l'eau ruisselle
        if 1540 <= t <= 2080:
            b, fr = splash_crown(fig, HOME_X, (t - 1540) / 520.0, 0.85, seed=1)
            fig.fx_back += b
            fig.fx_front += fr
        if 1700 <= t <= 2080:
            k = (t - 1700) / 380.0
            for j, (px, py) in enumerate(((60, 62), (96, 56), (48, 88), (90, 80), (70, 40), (36, 70))):
                tt = (k * 0.9 + 0.17 * j) % 0.5
                x, y = ballistic((px, py + 10 * ((j * 0.37) % 1)), (0, 10), 300, tt)
                if y < GR - 1:
                    fig.fx_front.append(drop(fig, x, y, 0, 10 + 300 * tt, 0.7, op=(1 - k)))
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (même fond que
    Kael)."""
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
    return im


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous le héros : elle suit sa glissade, pâlit quand il bondit, disparaît quand il est sous
    le sol."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    dr = P['drop']
    if dr > 6:
        return sh
    lift = max(0.0, -dr)
    s = max(0.4, 1 - lift / 30) * (1 - max(0.0, dr) / 6)
    cx = (64 + P['shift'] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 40 * k * s, fy - 2.8 * k * s, cx + 40 * k * s, fy + 2.8 * k * s], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
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
    P, tl = pose_at(T, act, t0)
    fx = []
    if act == 'attack':
        if tl < 300:
            HIT.clear()
        path = []
        for dt in (0.09, 0.06, 0.03):
            if T - dt >= t0:
                Pp, _ = pose_at(T - dt, act, t0)
                path.append(K.build(pose=Pp).ctx['tip'])
        fx = [fx_attack(tl, path)]
    elif act == 'special':
        fx = [fx_special(tl)]
    return K.build(ow=ow, pose=P, fx=fx, frame=view).svg(), P


def render(frames_svg, w, h, prefix):
    """Rend les SVG en PNG (un seul navigateur)."""
    import json
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
        extra = [float(x) for x in sys.argv[sys.argv.index('--planche') + 1:]]
        moments = extra or [1.0, a_s + 0.3, a_s + 0.44, a_s + 0.5, a_s + 0.6, a_s + 0.7, a_s + 0.85,
                            s_s + 0.3, s_s + 0.37, s_s + 0.45, s_s + 0.6, s_s + 0.75, s_s + 0.9, s_s + 1.03,
                            s_s + 1.09, s_s + 1.2, s_s + 1.45, s_s + 1.6, s_s + 1.7, s_s + 1.85]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
            im = bg.copy()
            im.alpha_composite(shadow_layer(640, 360, VIEW, P))
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('KESHA_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    for i, (p, (_, P)) in enumerate(zip(pngs, fr)):
        im = bg.copy()
        im.alpha_composite(shadow_layer(VW, VH, VIEW, P))
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
    shutil.rmtree(TMP)


if __name__ == '__main__':
    main()
