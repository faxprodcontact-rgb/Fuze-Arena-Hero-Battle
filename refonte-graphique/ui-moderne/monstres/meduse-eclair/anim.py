# La méduse éclair vectorielle ANIMÉE : les mêmes animations que son pixel art
# (refonte-graphique/pixel/hd/anim/meduse-eclair/build.py) — elle flotte et pulse (repos), attaque de base « Bulle
# d'éclair », attaque spéciale « Orage des abysses » — dans le style lisse des héros vectoriels (comme Kesha, le chef de
# son clan : heros/kesha/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/meduse-eclair/anim.py              # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/meduse-eclair/anim.py --planche [t…]  # planche d'images clés
#
# Une méduse ne bouge pas comme un humain : l'ombrelle PULSE (elle se resserre et s'allonge, puis s'ouvre et
# s'aplatit) ; à chaque contraction elle monte, puis plane et redescend doucement. Ce qui pend suit avec retard : une
# onde descend les bras et les filaments (plus ample vers le bout), le bas traîne quand elle avance ou recule, ils
# s'étirent quand elle monte (les deux filaments posés au sol y restent). La dent pendue à l'anneau se balance. Le
# coeur s'allume quand elle charge un sort ; les filaments s'allument pendant l'attaque spéciale.
#   - « Bulle d'éclair » : elle s'ouvre et se tasse (elle prend de l'eau), le coeur s'allume, une bulle chargée naît
#     devant son bord et grossit (tenue) ; contraction d'un coup : elle recule et monte, la bulle file en légère courbe
#     vers l'ennemi (sillage d'eau, décharge courbe autour) et éclate (gerbe ronde, deux décharges en fouet, gouttes) ;
#   - « Orage des abysses » : elle s'élève en deux contractions, ses filaments s'allument et chargent une grosse sphère
#     d'eau électrique devant elle ; une poussée de toute l'ombrelle la lance ; elle enferme l'ennemi dans un grand
#     dôme de bulle posé au sol, parcouru de décharges courbes (temps suspendu), qui crève par le haut : gerbe
#     d'écume, deux vagues qui roulent au sol de chaque côté, pluie de gouttes et de bulles ; elle redescend, le coeur
#     éteint un instant.
# Les effets : les outils et les couleurs d'eau des héros d'eau vectoriels (Kesha, Ilian : dégradés, un contour bleu
# nuit, aucun flou) ; les décharges sont des courbes douces qui ondulent (jamais de zigzag), cyan à coeur blanc.
import importlib.util
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
_spec = importlib.util.spec_from_file_location('meduse_eclair', os.path.join(HERE, 'meduse-eclair.py'))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
from atelier import lock, sm, ribbon, ellipse, mapp, f as fm  # noqa: E402
from outils import taper, crpath  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'meduse-eclair')
TMP = os.environ.get('MEDUSE_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-10, -24, 256, 144)           # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
WINK = '#0c1846'                      # le contour de l'eau (bleu nuit presque noir, comme Kesha et Ilian)
WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']
ZAP = ('#ffffff', '#a8ffec', '#6e76ec')     # décharge : coeur blanc, halo cyan électrique, bord bleu-violet
SPARK = ('#fffcde', '#ffe26e')              # étincelle : coeur blanc chaud, jaune (le jaune de Kesha)
TX, TY = 206.0, 78.0                  # l'ennemi : où il se tient, la hauteur où le sort le touche (sa poitrine)

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


NUM = ['k', 'lift', 'x', 'xb', 'tilt', 'glow', 'fil', 'tooth']


def keyed(keys, t):
    ts = [k[0] for k in keys]
    return {n: monotone(ts, [k[1].get(n, 0.0) for k in keys], t) for n in NUM}


# ======================================================================== les actions (poses clés, en ms)
# Mêmes temps que le pixel art (ATTAQUE / SPECIALE de build.py), en plus fluide.
ATTACK = [
    (0, {}),
    (120, dict(k=1, lift=-1, glow=1, xb=0.4, tooth=3)),                  # elle s'ouvre, se tasse (prend l'eau)
    (260, dict(k=1, lift=-2, x=1, glow=1, xb=0.8, tooth=4)),
    (480, dict(k=1.1, lift=-2.2, x=1.2, glow=1.2, xb=0.9, tooth=2)),    # anticipation tenue, la bulle grossit
    (540, dict(k=-1, lift=2, x=-3, glow=0.4, xb=-1.5, tilt=-2, tooth=-6)),   # contraction d'un coup : la bulle part
    (600, dict(k=-1, lift=3, x=-3.2, xb=-2.4, tilt=-2, tooth=-8)),
    (660, dict(k=0, lift=3, x=-2.4, xb=-2, tooth=-3)),
    (720, dict(k=1, lift=2.2, x=-2, xb=-1, tooth=4)),                  # l'impact (tenu)
    (900, dict(k=0.8, lift=2, x=-1.2, xb=-0.4, tooth=2)),
    (1010, dict(k=0, lift=1, x=-0.8, tooth=-1)),
    (1140, dict(k=0, lift=0.3, x=-0.2)),
    (1330, {}),
]
A_LAUNCH, A_HIT = 540, 720

SPECIAL = [
    (0, {}),
    (160, dict(k=1, lift=-2, x=1, glow=1, xb=0.6, tooth=3)),           # elle se tasse (prend l'eau)
    (250, dict(k=-1, lift=2, glow=1, xb=-0.4, tooth=-4)),              # 1re contraction : elle monte
    (340, dict(k=0, lift=5, glow=1, tooth=-2)),
    (450, dict(k=1, lift=7, x=1, glow=2, fil=1, tooth=3)),             # elle s'ouvre, s'allume
    (530, dict(k=-1, lift=11, glow=2, fil=1, tooth=-4)),               # 2e contraction
    (640, dict(k=0, lift=14, glow=2, fil=1, tooth=-1)),
    (900, dict(k=1, lift=14, x=1, glow=2, fil=1, xb=0.6, tooth=2)),   # la sphère est prête (tenue)
    (970, dict(k=-1, lift=14, x=-5, tilt=6, glow=0.5, fil=0.6, xb=1.6, tooth=-7)),   # la poussée
    (1030, dict(k=-1, lift=14, x=-5, tilt=4, glow=0.2, fil=0.3, xb=-1, tooth=-8)),
    (1090, dict(k=0, lift=13, x=-4, tilt=1, xb=-2, tooth=-3)),
    (1150, dict(k=1, lift=11, x=-4, xb=-2, tooth=3)),                  # le dôme : temps suspendu
    (1400, dict(k=1, lift=10, x=-3, xb=-1.6, tooth=2)),
    (1520, dict(k=0, lift=8, x=-2, xb=-1, tooth=-1)),
    (1640, dict(k=0, lift=6, x=-2, glow=-1, tooth=-2)),                # elle redescend, coeur éteint
    (1760, dict(k=1, lift=3, x=-1, glow=-1, tooth=2)),
    (1880, dict(k=1, lift=1, glow=-1, tooth=1)),
    (2010, dict(k=0, lift=0, glow=0)),
    (2300, {}),
]
S_SPHERE, S_PUSH, S_TRAP, S_BURST = 420, 970, 1150, 1500


# ======================================================================== le repos (en boucle)

def idle_pose(T):
    """Elle pulse toutes les 1,5 s : contraction rapide (elle monte de 2 px, le coeur s'allume un peu), puis elle
    s'ouvre et plane, et redescend doucement."""
    u = (T % 1.5) / 1.5
    k = monotone([0, 0.14, 0.42, 0.75, 1.0], [0.3, -1.0, 1.0, 0.55, 0.3], u)
    lift = monotone([0, 0.12, 0.32, 0.55, 1.0], [0.0, 0.5, 2.0, 1.9, 0.0], u)
    glow = 0.35 * math.exp(-((u - 0.18) / 0.12) ** 2)
    xb = 0.7 * math.sin(2 * math.pi * u - 0.6)
    tooth = 6 * math.sin(2 * math.pi * T / 1.5 - 1.8)
    return dict(k=k, lift=lift, glow=glow, xb=xb, tooth=tooth, x=0.0, tilt=0.0, fil=0.0)


def pose_at(T, action=None, t0=0.0):
    """La pose complète au temps T (s) : le repos (pondéré) + l'action en cours."""
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl = idle_pose(T)
    src = act or {n: 0.0 for n in NUM}
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['ph'] = 2 * math.pi * T / 1.6
    P['wave'] = 1.0 + (0.4 if action else 0.0) * (1 - w)
    P['blink'] = 1.0 if (w > 0.95 and 2.1 <= (T % 4.2) < 2.2) else 0.0
    return P, tl


# ======================================================================== l'eau et les décharges


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, ry or r, stops)


def outlined(shapes_fills, ink=WINK, w=1.2, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (silhouettes épaisses, puis les couleurs) ; une 4e valeur
    = pas de silhouette pour cet élément (un reflet peint dedans)."""
    sil = ''.join('<path d="%s"%s fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s"%s fill="%s"%s/>' % (sh.d(), ' fill-rule="evenodd"' if sh.evenodd else '', fl,
                                                    '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
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


def bubble(fig, x, y, r, op=1.0):
    """Une petite bulle d'air : un anneau d'eau claire, l'intérieur pâle, un éclat en haut à droite."""
    if r < 0.25 or op <= 0.02:
        return ''
    gr = g_rad(fig, (x - 0.2 * r, y + 0.2 * r), r, [(0, WATER[1], 0.75), (0.7, WATER[2], 0.85), (1, WATER[3], 1)])
    return ('<g opacity="%g"><circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.95"/></g>') % (
        max(0, min(1, 2 * op)), fm(x), fm(y), fm(r), gr, WINK, fm(min(0.9, 0.3 + 0.35 * r)), fm(x + 0.38 * r), fm(y - 0.38 * r), fm(0.3 * r), fm(0.22 * r))


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
    """Un filet d'eau le long d'une courbe (le sillage d'une bulle) : fin derrière, plein devant, crête claire."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=20)
    sh = taper(c, w0, w1, tip='round')
    crest = taper([(x + 0.25, y - 0.35) for x, y in c[4:]], w0 * 0.2, w1 * 0.3, tip='round')
    gr = g_lin(fig, c[0], c[-1], [(0, WATER[3]), (0.6, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.85, 'n')], w=1.1, op=op)


def arc_pts(p0, p1, bend=0.25, wob=1.2, waves=1.0, phase=0.0, n=16):
    """Le chemin d'une décharge de p0 à p1 : une courbe (bend) qui ondule doucement (wob), jamais un zigzag."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    out = []
    for i in range(n + 1):
        t = i / n
        s = math.sin(math.pi * t)
        o = bend * L * s + wob * math.sin(2 * math.pi * waves * t + phase) * s
        out.append((p0[0] + dx * t + nx * o, p0[1] + dy * t + ny * o))
    return out


def zap(pts, w=0.8, op=1.0):
    """Une décharge : un ruban effilé aux deux bouts (bord bleu-violet, halo cyan, coeur blanc), sans contour noir :
    c'est de la lumière."""
    if op <= 0.02 or len(pts) < 3:
        return ''
    c = crpath(pts, n=22)
    n = len(c)

    def ws(k):
        return [0.05] + [k * w * (0.55 + 0.45 * math.sin(math.pi * i / (n - 1))) for i in range(1, n - 1)] + [0.05]
    out = ''.join('<path d="%s" fill="%s"%s/>' % (ribbon(c, ws(k)).d(), col, '' if o == 1 else ' opacity="%g"' % o)
                  for k, col, o in ((2.6, ZAP[2], 0.55), (1.7, ZAP[1], 0.95), (0.7, ZAP[0], 1)))
    return '<g opacity="%g">%s</g>' % (max(0, min(1, op)), out)


def spark(x, y, r=1.0, op=1.0):
    """Une étincelle ronde (pas d'étoile) : un halo cyan, le jaune de Kesha, un coeur blanc chaud."""
    if op <= 0.02:
        return ''
    return ('<g opacity="%g"><circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.45"/><circle cx="%s" cy="%s" r="%s" '
            'fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/></g>') % (
        max(0, min(1, op)), fm(x), fm(y), fm(r * 2.1), ZAP[1], fm(x), fm(y), fm(r), SPARK[1], fm(x), fm(y), fm(r * 0.5), SPARK[0])


def orb(fig, c, r, ph, op=1.0, shell=True):
    """La bulle d'eau chargée d'éclairs : une sphère d'eau (claire en haut à droite, un contour bleu nuit), deux
    décharges courbes qui tournent dedans, un coeur blanc, un reflet ; une décharge crépite sur son arrière."""
    if r < 0.4 or op <= 0.02:
        return '', ''
    x, y = c
    halo = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(y), fm(r * 2.0), fm(r * 2.0), g_rad(
        fig, c, r * 2.0, [(0, ZAP[1], 0.55 * op), (0.5, ZAP[1], 0.2 * op), (1, ZAP[1], 0)]))
    gr = fig.rad(x + 0.35 * r, y - 0.35 * r, r * 1.45, r * 1.45, [(0, WATER[0]), (0.25, WATER[1]), (0.6, WATER[2]), (0.9, WATER[3]), (1, WATER[4])])
    body = ellipse(x, y, r, r)
    inner = ''
    for j in range(2):
        a0 = ph * 1.3 + j * math.pi
        p0 = (x + 0.62 * r * math.cos(a0), y + 0.62 * r * math.sin(a0))
        p1 = (x + 0.55 * r * math.cos(a0 + 2.3), y + 0.55 * r * math.sin(a0 + 2.3))
        inner += zap(arc_pts(p0, p1, bend=0.32, wob=0.12 * r, waves=1.0, phase=ph * 2 + j), w=max(0.35, 0.09 * r))
    core = '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="#ffffff"/>' % (
        fm(x), fm(y), fm(0.3 * r), ZAP[1], fm(x), fm(y), fm(0.17 * r))
    hl = ribbon([(x + 0.12 * r, y - 0.72 * r), (x + 0.5 * r, y - 0.56 * r), (x + 0.72 * r, y - 0.16 * r)], [0.1, 0.16 * r, 0.1])
    front = outlined([(body, gr, 1)], w=1.2, op=op)
    front = front[:-4] + inner + core + '<path d="%s" fill="#ffffff" opacity="0.9"/>' % hl.d() + '</g>'
    if shell:
        pts = []
        for i in range(25):
            a = math.radians(110 + 140 * i / 24)
            rr = r + 1.3 + 0.7 * math.sin(ph * 3 + i * 0.5)
            pts.append((x + rr * math.cos(a), y - rr * math.sin(a)))
        front += zap(pts, w=0.45, op=op) + spark(pts[0][0], pts[0][1], 0.55, op) + spark(pts[-1][0], pts[-1][1], 0.55, op)
    return halo, front


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


def dome(fig, X, R, H, ph, op=1.0, top_open=0.0):
    """Le grand dôme de bulle posé au sol autour de l'ennemi : une demi-sphère d'eau translucide (on voit au travers),
    un contour bleu nuit, une lèvre d'eau au sol, un reflet en arc en haut à droite, des décharges courbes qui
    courent sur sa surface. top_open : il crève par le haut (0 → 1)."""
    if op <= 0.02:
        return '', ''
    G = GR + 0.3
    a_cut = math.radians(90 * (1 - top_open)) if top_open > 0 else None
    pts = []
    n = 36
    for i in range(n + 1):
        a = math.pi * i / n
        if a_cut is not None and abs(a - math.pi / 2) < math.pi / 2 - a_cut:
            continue
        pts.append((X - R * math.cos(a), G - H * math.sin(a)))
    gr = fig.rad(X + 0.3 * R, G - 0.6 * H, R * 1.1, H * 1.1, [(0, WATER[3], 0.3), (0.55, WATER[2], 0.42), (0.88, WATER[2], 0.75), (1, WATER[1], 0.95)])
    back = ''
    front = ''
    if top_open <= 0:
        d = 'M%s %s ' % (fm(X - R), fm(G)) + ' '.join('L%s %s' % (fm(x), fm(y)) for x, y in pts[1:]) + ' Z'
        back = '<g opacity="%g"><path d="%s" fill="%s" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/></g>' % (
            min(1, op * 1.5), d, gr, WINK)
        # le reflet : un arc en retrait du bord, en haut à droite
        hl = [(X + R * 0.82 * math.cos(math.radians(a)), G - H * 0.84 * math.sin(math.radians(a))) for a in range(30, 75, 5)]
        front += '<path d="%s" fill="#ffffff" opacity="%g"/>' % (ribbon(hl, [0.1, 0.8, 1.3, 1.6, 1.6, 1.4, 1.1, 0.7, 0.1]).d(), 0.85 * op)
        # les décharges qui courent sur la surface
        for j in range(3):
            a0 = 22 + 50 * j + 14 * math.sin(ph * 0.9 + j * 2.1)
            a1 = min(170, a0 + 44 + 8 * math.sin(ph * 1.3 + j))
            kk = 0.62 + 0.25 * ((j * 0.37 + ph * 0.05) % 1)
            arc = [(X + R * kk * math.cos(math.radians(a0 + (a1 - a0) * i / 12)) + 0.8 * math.sin(ph * 2 + i + j),
                    G - H * kk * math.sin(math.radians(a0 + (a1 - a0) * i / 12))) for i in range(13)]
            front += zap(arc, w=0.6, op=op) + spark(arc[0][0], arc[0][1], 0.55, op) + spark(arc[-1][0], arc[-1][1], 0.5, op)
    else:
        # il crève : la paroi se défait en un anneau d'écume qui retombe
        k = top_open
        for j in range(7):
            a = math.pi * (j + 0.5) / 7
            x = X - R * (1 + 0.25 * k) * math.cos(a)
            y = G - H * (1 - 0.8 * k) * math.sin(a)
            front += foam(fig, x, y, 2.2 * (1 - 0.5 * k), op=op, seed=j)
    # la lèvre d'eau au sol, tout le tour
    lip = sm([(X - R - 2, G + 0.2), (X - R + 1, G - 2.2), (X, G - 3.0), (X + R - 1, G - 2.2), (X + R + 2, G + 0.2),
              (X, G + 1.2)], sharp=(0, 4), t=0.9)
    front += outlined([(lip, g_lin(fig, (X + R, G - 3), (X - R, G), [(0, WATER[2]), (0.5, WATER[3]), (1, WATER[4])]), 1),
                       (ribbon([(X - R * 0.6, G - 1.6), (X, G - 2.5), (X + R * 0.7, G - 1.8)], [0.1, 0.8, 0.1]), '#ffffff', 0.8, 'n')],
                      w=1.2, op=op)
    return back, front


def wave(fig, X, h, L, side, op=1.0):
    """Une vague qui roule au sol : un dos long derrière, une crête qui penche vers l'avant (side = +1 : vers la
    droite), de l'écume sur la crête."""
    if h < 0.6 or op <= 0.02:
        return ''
    G = GR + 0.4
    s = side
    pts = [(X - s * L, G), (X - s * L * 0.55, G - h * 0.35), (X - s * L * 0.1, G - h * 0.85), (X + s * L * 0.25, G - h),
           (X + s * L * 0.52, G - h * 0.7), (X + s * L * 0.6, G - h * 0.3), (X + s * L * 0.72, G)]
    if s < 0:
        pts = pts[::-1]
    sh = sm(pts, sharp=(0, len(pts) - 1), t=0.9)
    gr = g_lin(fig, (X + L * 0.3, G - h), (X - L * 0.3, G), [(0, WATER[2]), (0.45, WATER[3]), (1, WATER[4])])
    crest = ribbon([(X - s * L * 0.35, G - h * 0.65), (X - s * L * 0.05, G - h * 0.92), (X + s * L * 0.25, G - h * 0.98), (X + s * L * 0.48, G - h * 0.74)],
                   [0.1, h * 0.12, h * 0.14, 0.1])
    out = outlined([(sh, gr, 1), (crest, '#ffffff', 0.9, 'n')], w=1.3, op=op)
    out += foam(fig, X + s * L * 0.3, G - h * 0.95, h * 0.18, op=op, seed=int(X) % 3)
    return out


# ---- l'attaque de base : la bulle d'éclair

SHOT = {}


def fx_attack(tl):
    def f(fig, ctx):
        M = ctx['M']
        ph = tl / 1000 * 9
        birth = mapp(M, (K.HW + 8.5, 6.5))
        if tl < A_LAUNCH:
            r = monotone([100, 260, 480, 540], [0.0, 3.0, 5.0, 5.4], tl)
            if r > 0.3:
                SHOT['p0'] = birth
                halo, front = orb(fig, birth, r, ph, op=min(1, r / 1.5), shell=r > 2)
                fig.fx_back.append(halo)
                fig.fx_front.append(front)
        elif tl < A_HIT:
            t = (tl - A_LAUNCH) / (A_HIT - A_LAUNCH)
            t = t ** 0.85
            p0 = SHOT.get('p0', birth)
            p1 = (TX - 7, TY)

            def path(s):
                return (p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s - 9 * math.sin(math.pi * s))
            x, y = path(t)
            s0 = max(0.0, t - 0.32)
            trail = [path(s0 + (t - s0) * i / 10) for i in range(11)]
            fig.fx_back.append(stream(fig, trail[2:], 0.5, 4.0, op=1))
            for j, s in enumerate((0.06, 0.13, 0.2)):
                if t - s > 0:
                    bx, by = path(t - s)
                    fig.fx_back.append(bubble(fig, bx - 1, by + (3.2 if j % 2 else -3.4), 1.3 if j == 0 else 1.0))
            halo, front = orb(fig, (x, y), 5.6, ph)
            fig.fx_back.append(halo)
            fig.fx_front.append(front)
        else:
            tau = (tl - A_HIT) / 1000.0
            X, Y = TX - 6, TY
            e = env(tau, 0, 0.03, 0.14, 0.4)
            # l'éclat : un rond de lumière, une gerbe ronde de nappes, deux décharges qui se recourbent en fouet
            if tau < 0.12:
                k = tau / 0.12
                fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(X), fm(Y), fm(4 + 7 * k), g_rad(
                    fig, (X, Y), 4 + 7 * k, [(0, '#ffffff', 0.9 * (1 - k)), (0.5, ZAP[1], 0.6 * (1 - k)), (1, ZAP[1], 0)])))
            for j, (ang, L, bd, w) in enumerate(((-150, 13, -40, 3.6), (-110, 15, -20, 4.0), (-60, 12, 30, 3.4),
                                                  (160, 11, 30, 3.2), (100, 9, 20, 3.0))):
                L_ = L * (0.4 + 0.6 * min(1, tau / 0.1))
                (fig.fx_back if j in (1, 4) else fig.fx_front).append(
                    sheet(fig, (X, Y), ang, L_ * (0.3 + 0.7 * e), bd, w * (0.4 + 0.6 * e), op=min(1, 3 * e), tail=max(0, tau - 0.14) * 2.4))
            fe = env(tau, 0, 0.02, 0.12, 0.34)
            fig.fx_front.append(foam(fig, X + 1, Y, 3.6 * fe + 1.0, op=fe, seed=2))
            ze = env(tau, 0, 0.01, 0.12, 0.26)
            if ze > 0:
                fig.fx_front.append(zap(arc_pts((X - 3, Y - 4), (X - 15, Y - 15), bend=0.3, wob=0.9, phase=ph), w=0.7, op=ze))
                fig.fx_front.append(zap(arc_pts((X - 3, Y + 5), (X - 17, Y + 9), bend=-0.28, wob=0.9, phase=ph + 2), w=0.7, op=ze))
                fig.fx_front.append(spark(X - 15, Y - 15, 0.8, ze))
                fig.fx_front.append(spark(X - 17, Y + 9, 0.8, ze))
            for j, (vx, vy) in enumerate(((-60, -90), (-95, -40), (-30, -120), (-85, 15), (20, -110), (55, -70), (-50, -20))):
                if tau < 0.7:
                    x, y = ballistic((X, Y), (vx, vy), 260, tau)
                    if y < GR:
                        fig.fx_front.append(drop(fig, x, y, vx, vy + 260 * tau, 0.95 if j % 2 else 0.75, op=min(1, (0.7 - tau) * 4)))
            for j, (dx, r0) in enumerate(((-4, 1.3), (3, 1.0), (-1, 0.8))):
                tb = tau - 0.08 * j
                if 0 < tb < 0.55:
                    fig.fx_front.append(bubble(fig, X + dx + 1.2 * math.sin(tb * 12 + j), Y - 4 - 26 * tb, r0, op=min(1, (0.55 - tb) * 4)))
    return f


# ---- l'attaque spéciale : l'orage des abysses

def fx_special(tl):
    def f(fig, ctx):
        M = ctx['M']
        ph = tl / 1000 * 9
        sph = mapp(M, (K.HW + 13, -3))
        if S_SPHERE <= tl < S_PUSH:
            r = monotone([S_SPHERE, 530, 640, 900, S_PUSH], [0.5, 3.5, 6.0, 8.6, 9.0], tl)
            SHOT['s0'] = sph
            halo, front = orb(fig, sph, r, ph, op=min(1, r / 2))
            fig.fx_back.append(halo)
            fig.fx_front.append(front)
            # les filaments allumés chargent la sphère : des décharges courbes partent de leurs bouts vers elle
            fl = ctx['strands']
            for j, (name, s) in enumerate((('f7', 0.85), ('f5', 0.9), ('a3', 0.9), ('b3', 0.8))):
                flick = 0.5 + 0.5 * math.sin(tl / 1000 * 31 + j * 2.4)
                if flick < 0.25:
                    continue
                p = K.point_at(fl[name], s)
                fig.fx_front.append(zap(arc_pts(p, (sph[0] - r * 0.6, sph[1] + r * 0.5), bend=0.18 * (1 if j % 2 else -1),
                                                wob=1.2, waves=1.2, phase=ph * 2 + j), w=0.55, op=flick))
                fig.fx_front.append(spark(p[0], p[1], 0.6, flick))
        elif S_PUSH <= tl < S_TRAP:
            t = (tl - S_PUSH) / (S_TRAP - S_PUSH)
            t = t ** 0.8
            p0 = SHOT.get('s0', sph)
            p1 = (TX - 2, TY - 2)

            def path(s):
                return (p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s - 8 * math.sin(math.pi * s))
            x, y = path(t)
            s0 = max(0.0, t - 0.35)
            trail = [path(s0 + (t - s0) * i / 10) for i in range(11)]
            fig.fx_back.append(stream(fig, trail[2:], 0.6, 7.0, op=1))
            for j, s in enumerate((0.05, 0.11, 0.17, 0.23)):
                if t - s > 0:
                    bx, by = path(t - s)
                    fig.fx_back.append(bubble(fig, bx - 1, by + (5 if j % 2 else -5.5), 1.5 if j < 2 else 1.1))
            halo, front = orb(fig, (x, y), 9.0, ph)
            fig.fx_back.append(halo)
            fig.fx_front.append(front)
            if tl < S_PUSH + 60:                        # la poussée : un anneau d'eau chassé par l'ombrelle
                k = (tl - S_PUSH) / 60
                c = mapp(M, (K.HW + 4, 2))
                fig.fx_front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%g"/>' % (
                    fm(c[0]), fm(c[1]), fm(3 + 6 * k), fm(9 + 8 * k), WATER[2], fm(1.6 * (1 - k) + 0.3), 0.9 * (1 - k)))
        if tl >= S_TRAP:
            tau = (tl - S_TRAP) / 1000.0
            G = GR
            R, H = 22.0, 33.0
            grow = min(1.0, tau / 0.1)
            if tl < S_BURST:
                # le dôme se referme autour de l'ennemi (il pousse du sol), tenu, parcouru de décharges
                e = 0.6 + 0.4 * grow
                back, front = dome(fig, TX, R * e, H * grow ** 0.7, ph, op=1)
                fig.fx_back.append(back)
                fig.fx_front.append(front)
                if tau < 0.1:                           # l'éclat de l'arrivée
                    k = tau / 0.1
                    fig.fx_front.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(TX), fm(TY), fm(6 + 12 * k), g_rad(
                        fig, (TX, TY), 6 + 12 * k, [(0, '#ffffff', 0.9 * (1 - k)), (0.5, ZAP[1], 0.5 * (1 - k)), (1, ZAP[1], 0)])))
                for j in range(4):                      # bulles qui montent dedans
                    tb = (tau * 1.3 + j * 0.27) % 1
                    fig.fx_front.append(bubble(fig, TX - 10 + 6.5 * j + 1.2 * math.sin(tb * 9 + j), G - 3 - (H - 7) * tb,
                                               1.1 + 0.35 * (j % 2), op=min(1, (1 - tb) * 3) * grow))
            else:
                tb = (tl - S_BURST) / 1000.0
                op_ = env(tb, 0, 0.01, 0.12, 0.3)
                back, front = dome(fig, TX, R, H, ph, op=max(op_, 0.01), top_open=min(1, tb / 0.22))
                fig.fx_back.append(back)
                fig.fx_front.append(front)
                # la gerbe d'écume qui jaillit par le haut
                e = env(tb, 0, 0.04, 0.22, 0.55)
                for j, (ang, L, bd, w) in enumerate(((-120, 18, -30, 4.2), (-100, 24, -12, 5.0), (-80, 23, 12, 5.0), (-60, 17, 30, 4.2))):
                    L_ = L * (0.4 + 0.6 * min(1, tb / 0.12))
                    fig.fx_front.append(sheet(fig, (TX + (j - 1.5) * 2.2, G - H + 3), ang, L_ * (0.3 + 0.7 * e), bd, w * (0.5 + 0.5 * e),
                                              op=min(1, 3 * e), tail=max(0, tb - 0.25) * 2))
                fe = env(tb, 0, 0.04, 0.2, 0.45)
                for j, (dx, dy, rr) in enumerate(((-4, 0, 3.4), (3, -2, 3.0), (0, -6, 2.6))):
                    fig.fx_front.append(foam(fig, TX + dx, G - H + dy - 10 * min(1, tb / 0.2), rr * fe + 0.6, op=fe, seed=j))
                # deux vagues qui roulent au sol, de chaque côté, sur tout le premier rang
                we = env(tb, 0.04, 0.14, 0.42, 0.7)
                for side in (-1, 1):
                    X = TX + side * (R * 0.7 + 30 * min(1, tb / 0.65) ** 0.8)
                    fig.fx_front.append(wave(fig, X, 8.5 * we * (1 - 0.35 * min(1, tb / 0.7)), 15, side, op=we))
                # la pluie de gouttes et de bulles
                for j in range(12):
                    vx = -70 + 140 * ((j * 0.618) % 1)
                    vy = -150 + 60 * ((j * 0.37) % 1)
                    tt = tb - 0.03 * (j % 4)
                    if 0 < tt < 0.95:
                        x, y = ballistic((TX + (j % 5 - 2) * 2, G - H), (vx, vy), 300, tt)
                        if y < GR - 0.5:
                            fig.fx_front.append(drop(fig, x, y, vx, vy + 300 * tt, 1.0 if j % 3 else 0.8, op=min(1, (0.95 - tt) * 4)))
                for j in range(5):
                    tt = tb - 0.1 - 0.06 * j
                    if 0 < tt < 0.8:
                        fig.fx_front.append(bubble(fig, TX - 14 + 7 * j + 2 * math.sin(tt * 8 + j), G - H * 0.5 - 30 * tt,
                                                   0.9 + 0.3 * (j % 2), op=min(1, (0.8 - tt) * 4)))
                # les dernières décharges qui s'éteignent au sol
                ze = env(tb, 0, 0.02, 0.12, 0.3)
                if ze > 0:
                    for side in (-1, 1):
                        fig.fx_front.append(zap(arc_pts((TX + side * 4, G - 3), (TX + side * 22, G - 1), bend=-0.22 * side,
                                                        wob=0.5, phase=ph + side), w=0.6, op=ze))
    return f


# ======================================================================== la scène, le rendu


def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle d'un bord à l'autre (même fond que Kael)."""
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


def shadow_layer(w, h, view, P, floor_y=GR):
    """L'ombre douce au sol sous la méduse : plus petite et plus pâle quand elle s'élève."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    s = max(0.55, 1 - max(0.0, P['lift']) / 30)
    cx = (56 + P['x'] - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 32 * k * s, fy - 2.4 * k * s, cx + 32 * k * s, fy + 2.4 * k * s], fill=(10, 4, 24, int(130 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.0 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 3.0), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.9), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.1),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.5)]
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
        fx = [fx_attack(tl)]
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
    subprocess.run(['node', os.path.join(HERE, '..', '..', 'heros', 'rendu-lot.cjs'), jp], check=True)
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
        moments = extra or [0.3, 0.75, a_s + 0.3, a_s + 0.5, a_s + 0.6, a_s + 0.68, a_s + 0.75, a_s + 0.9,
                            s_s + 0.45, s_s + 0.8, s_s + 0.98, s_s + 1.08, s_s + 1.25, s_s + 1.55, s_s + 1.7, s_s + 1.9]
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
        out = os.environ.get('MEDUSE_PLANCHE', os.path.join(TMP, 'planche.png'))
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
