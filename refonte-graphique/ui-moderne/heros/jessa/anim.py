# Jessa vectorielle ANIMÉE : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/tireur-pirate/build.py)
# — pose (la tireuse calme et son ara), attaque de base « Coup de hanche », attaque spéciale « Lame de fond » — dans le
# style lisse de l'interface, à 24 images par seconde (même méthode que Kael et que son capitaine Barzul : ../barzul/anim.py).
#
#   python3 refonte-graphique/ui-moderne/heros/jessa/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/jessa/
#   python3 refonte-graphique/ui-moderne/heros/jessa/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (jessa.py) est fait de morceaux ; chaque image le redessine dans une POSE. Le mousquet est un seul
# objet qui tourne autour de la main proche (la poignée) ; les deux mains restent sur le bois et les bras suivent par
# cinématique inverse depuis les épaules (le coude tourne sur un arc, rien ne se décroche ; les jabots cachent les
# poignets). Au repos l'arme ne bouge pas, le corps respire derrière ; les cheveux et les pans de l'écharpe suivent avec
# retard ; l'ara hoche la tête comme un vrai ara, sa queue se balance. Poses clés et durées reprises du pixel art.
# 2) « Coup de hanche » : elle abaisse le long mousquet à plat contre la hanche, vise, le chien s'abat (étincelle), le
#    coup part (éclair, balle, fumée blanche qui s'enroule), le recul relève le canon jusqu'à la garde, poussière aux
#    bottes ; l'ara sursaute, ouvre les ailes et crie.
# 3) « Lame de fond » : elle épaule et vise longuement, la joue contre la crosse ; l'eau de mer s'enroule autour de la
#    bouche du canon et s'y engouffre, l'ara déploie ses ailes et crie ; le coup part : une grosse balle d'eau enroulée
#    d'écume file à l'horizontale (anneaux d'eau dans son sillage) et éclate sur l'ennemi en une gerbe qui retombe en
#    pluie ; le recul la repousse, le canon se cabre, puis elle redescend l'arme en garde.
# Effets (formes rondes et courbes, dégradés, un contour, aucun flou ; l'eau et la fumée : mêmes outils et mêmes
# couleurs que Barzul).
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
import jessa as B  # noqa: E402
from atelier import sm, ribbon, ellipse, sides, bez, resample, lock, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, unit, ang_of, taper, crpath  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'jessa')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-jessa'
TMP = os.environ.get('JESSA_TMP', os.path.join(DBG, '_images'))
FPS = 24
VIEW = (6, -8, 236.0, 132.75)        # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = B.GRD
FOE_X = 186.0                        # l'ennemi (milieu)

WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']   # l'eau (celle de Kesha, d'Ilian, de Barzul)
WINK = '#0c1846'                     # le contour de l'eau
SMOKE = ['#ffffff', '#f4f2f8', '#dedcea', '#b8b6d0', '#8e8cae']               # la fumée de poudre (jamais de noir)
SINK = '#3a3660'
FIRE = ['#fffce4', '#ffe46e', '#ffa03c', '#e0583a']
FINK = '#6a1a14'
IRON = ['#d0d4ea', '#73769a', '#3e3a58', '#241e36']
STEELFX = ['#f4f8ff', '#c4d0ea', '#8494bc']
DUST = ['#fbf2e0', '#eee2c8', '#cdb894', '#a08a70', '#7a6656']

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
    cx = (67 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 21 * k, fy - 2.8 * k, cx + 21 * k, fy + 2.8 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))



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



def compose(pngs, w, h, view):
    bg = background(w, h, view)
    for p in pngs:
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view))
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)




# ======================================================================== les poses (réglages de jessa.py ; b : souffle en plus)
BASE = dict(lean=0.0, dn=0.0, headx=0.0, heady=0.0, tilt=0.0, hs=0.0, cl=0.0, sq=0.0, smile=0.0,
            gx=B.G0[0], gy=B.G0[1], ga=B.GA0, fu=37.6, nwa=240.0, fwa=122.0, fired=0.0,
            phx=0.0, phy=0.0, pr=0.0, pt=0.0, pw=0.0, pc=0.0, pb=0.0, b=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key == 'head':
            d['headx'], d['heady'] = v
        elif key == 'g':
            d['gx'], d['gy'] = v
        elif key == 'ph':
            d['phx'], d['phy'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# 2) « Coup de hanche » (1100 ms, comme le pixel art) : elle abaisse le mousquet à plat contre la hanche (la main lointaine
# glisse sur le fût et le prend par-dessus), se tasse, plisse l'œil ; le chien s'abat (étincelle), le coup part ; le
# recul relève le canon jusqu'à la garde, la pousse en arrière, soulève la poussière aux bottes ; l'ara sursaute, ouvre
# les ailes et crie, puis se calme ; elle a son demi-sourire.
HIP = dict(g=(61.0, 82.6), ga=-1.5, fu=35.5, fwa=200.0, nwa=238.0)
ATTACK = [
    (0, {}),
    (90, dict(g=(60.6, 83.6), ga=-14.0, fu=36.6, fwa=165.0, nwa=239.0, dn=0.5, head=(0.3, 0.6), hs=0.6, cl=0.5, pt=0.6)),
    (200, dict(HIP, dn=0.8, head=(0.5, 0.8), tilt=1.5, sq=1, hs=-0.4, cl=-0.3, pt=0.8, pr=6)),
    (360, dict(HIP, dn=0.8, head=(0.5, 0.8), tilt=1.5, sq=1, pr=6, pt=0.2)),
    (390, dict(HIP, dn=0.8, head=(0.5, 0.8), tilt=1.5, sq=1, pr=6, fired=1)),
    (420, dict(HIP, dn=0.8, head=(0.5, 0.8), tilt=1.5, sq=1, pr=4, fired=1)),
    (470, dict(g=(59.6, 82.4), ga=-11.0, fu=35.8, fwa=190.0, nwa=238.0, fired=1, lean=-0.9, dn=0.5, head=(-0.6, 0.2), tilt=-1.5,
               sq=0.4, hs=1.2, cl=1.0, pw=0.75, pc=1, pb=1, ph=(-0.6, -0.8), pr=-10, pt=-1.2)),
    (560, dict(g=(59.8, 83.0), ga=-20.0, fu=36.6, fwa=160.0, fired=1, lean=-0.6, head=(-0.3, 0.0), pw=0.5, pc=0.8, pb=0.6, pr=-4,
               pt=-0.6, hs=0.6, cl=0.6)),
    (680, dict(ga=-27.0, fu=37.4, fwa=128.0, fired=1, lean=-0.1, pw=0.12, pc=0.2, pb=0.1, pt=0.6, hs=-0.4, cl=-0.4)),
    (800, dict(fired=1, head=(0.0, -0.3), smile=1, pt=-0.4, pr=4)),
    (960, dict(fired=0.0, smile=1, pr=0)),
    (1100, {}),
]
ATT_SPARK = 380       # le chien s'abat : étincelle
ATT_SHOT = 420        # le coup part

# 3) « Lame de fond » (2040 ms) : elle épaule (la crosse contre l'épaule, la joue sur le bois) et vise longuement ; l'eau
# s'enroule autour de la bouche du canon et s'y engouffre, l'ara déploie ses ailes et crie ; le coup part : grosse balle
# d'eau enroulée d'écume, anneaux d'eau dans son sillage ; elle éclate sur l'ennemi en une gerbe qui retombe en pluie ;
# le recul la repousse, le canon se cabre ; elle reste en joue un instant (demi-sourire), puis redescend l'arme en garde.
RAISE = dict(g=(62.4, 72.4), ga=-12.0, fu=37.6, nwa=195.0, fwa=150.0)
AIM = dict(g=(66.0, 62.8), ga=0.0, fu=38.0, nwa=139.0, fwa=178.0, head=(0.5, 1.6), tilt=3.5, sq=1, lean=0.2)
SPECIAL = [
    (0, {}),
    (90, dict(RAISE, dn=0.6, hs=0.6, cl=0.5, pt=0.6)),
    (230, dict(AIM, hs=-0.5, cl=-0.4, pt=0.6)),
    (360, dict(AIM, pr=8, ph=(0.4, 0.0), pw=0.15)),
    (490, dict(AIM, b=0.8, pw=0.7, pb=0.6, pc=0.4, pt=-0.6)),
    (600, dict(AIM, b=1.0, pw=1, pb=1, pc=1, pt=-1.0, pr=-6)),
    (730, dict(AIM, b=1.0, pw=1, pb=1, pc=1, pt=-0.8, pr=-2)),
    (790, dict(AIM, fired=1, b=0.6, pw=1, pb=1, pc=1)),
    (850, dict(AIM, g=(62.6, 62.0), ga=-11.0, fired=1, lean=-1.4, head=(-0.4, 1.0), tilt=1.0, sq=0.4, hs=1.4, cl=1.2, pw=0.8, pc=1,
               pb=0.8, pt=-1.4, pr=-12)),
    (1000, dict(AIM, g=(64.0, 62.4), ga=-6.0, fired=1, lean=-0.8, hs=0.8, cl=0.8, pw=0.5, pc=0.5, pb=0.4, pt=-0.6)),
    (1150, dict(AIM, fired=1, sq=0.6, smile=0.6, pw=0.2, pc=0, pt=0.4)),
    (1550, dict(AIM, fired=1, smile=1, sq=0.4, head=(0.4, 1.4), tilt=3.0)),
    (1700, dict(RAISE, fired=0.5, smile=1, pt=-0.6, hs=-0.4)),
    (1850, dict(smile=0.6, pt=0.4, hs=0.4, cl=0.3)),
    (2040, {}),
]
GATHER = (330, 790)     # l'eau s'enroule autour de la bouche du canon
SPEC_SHOT = 790         # le coup part
SHOT_V = 0.36           # la vitesse de la balle d'eau (pixels du dessin par ms)
IMPACT_X = FOE_X - 2.0


# ======================================================================== la pose (le repos : elle respire, l'ara hoche)
IDLE_T = 3.0     # la boucle du repos (s) : respiration lente et signe du héros (1,6 s avant le 27/11)


def signe(T):
    """LE SIGNE DU REPOS (demande du 27/11 : « chaque héros a quelque chose à lui, une petite animation lente mais
    visible ») : son ara rouge entrouvre lentement les ailes puis les replie, et sa longue queue se balance.
    Une pose partielle pour build() ; jouée au combat (pose_at) et dans les menus (heros/repos.py)."""
    u = 2 * math.pi * T / IDLE_T
    return dict(pw=0.4 * (0.5 - 0.5 * math.cos(u)), pt=-1.6 * math.sin(u - 1.2))


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE_T
    br = 0.5 - 0.5 * math.cos(u - 0.3)
    s2 = math.sin(2 * u + 0.4)
    bob = math.copysign(abs(s2) ** 0.6, s2)            # l'ara hoche la tête (vif, puis il tient)
    d = dict(lean=0.2 * math.sin(u), headx=0.12 * math.sin(u - 0.6), heady=-0.3 * (0.5 - 0.5 * math.cos(u - 0.9)),
             tilt=0.4 * math.sin(u - 1.0), hs=-0.8 * math.sin(u - 1.3), cl=-0.7 * math.sin(u - 1.1),
             pt=-0.9 * math.sin(u - 1.6), phx=0.3 * bob, phy=0.45 * bob, pr=5.0 * math.sin(u + 0.8))
    return d, br


def pose_at(T, action=None, t0=0.0):
    w = 1.0
    act = None
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 160), max(0.0, (tl - (dur - 260)) / 260))
        w = w * w * (3 - 2 * w)
    idl, br = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    for n, v in signe(T).items():
        P[n] += w * v
    br = br * w + P['b']
    out = dict(breath=min(1.3, br), lean=P['lean'], dn=P['dn'], head=(P['headx'], P['heady']), tilt=P['tilt'], hs=P['hs'],
               cl=P['cl'], sq=max(0, min(1, P['sq'])), smile=max(0, min(1, P['smile'])), g=(P['gx'], P['gy']), ga=P['ga'],
               fu=P['fu'], nwa=P['nwa'], fwa=P['fwa'], fired=max(0, min(1, P['fired'])), ph=(P['phx'], P['phy']), pr=P['pr'],
               pt=P['pt'], pw=max(0, min(1, P['pw'])), pc=max(0, min(1, P['pc'])), pb=max(0, P['pb']))
    out['blink'] = 1.0 if (w > 0.95 and 2.30 <= (T % IDLE_T) < 2.39) else 0.0
    return out


# ======================================================================== 2) l'attaque : le coup de hanche

SHOT = {}


def shot_at(action):
    """Là où le coup est parti : la bouche du canon et sa direction à l'instant du coup."""
    if action not in SHOT:
        t = ATT_SHOT if action == 'attack' else SPEC_SHOT
        P = pose_at(0.0, action, -t / 1000.0)
        ctx = B.build(pose=P).ctx
        SHOT[action] = (ctx['muzzle'], ctx['muzzle_dir'])
    return SHOT[action]


SMOKE_PUFFS = [(5.0, -1.0, 3.2, 0), (10.0, -2.4, 3.8, 15), (16.0, -3.6, 3.4, 30), (21.0, -5.6, 2.8, 45), (2.0, -3.4, 2.4, 25)]
SMOKE_CURLS = [((22.0, -7.0), (1, -0.6), 2.6, 1), ((0.0, -5.4), (-0.6, -1), 2.2, -1)]


def gun_smoke(fig, M0, t, t0, t1, out, scale=1.0):
    """La fumée blanche du coup : des bouffées poussées vers l'avant qui ralentissent, gonflent, montent et se défont."""
    k = (t - t0) / (t1 - t0)
    for j, (dx, dy, r, dl) in enumerate(SMOKE_PUFFS):
        kk = max(0.0, min(1.0, (t - t0 - dl) / (t1 - t0 - dl)))
        if kk <= 0:
            continue
        go = 1 - (1 - min(1, kk * 2.6)) ** 3
        c = (M0[0] + dx * go * scale + 2.5 * kk, M0[1] + dy * go * scale - kk * 4.5)
        rr = r * scale * (0.35 + 0.65 * go) * (1 + 0.35 * kk) * (1 - smooth((kk - 0.62) / 0.38) * 0.75)
        out.append(smoke(fig, c[0], c[1], rr, op=1 - smooth((kk - 0.55) / 0.45), k=j))
    for j, ((dx, dy), d, r0, s) in enumerate(SMOKE_CURLS):
        e = env(k, 0.18, 0.35, 0.6, 0.9)
        if e > 0:
            p = (M0[0] + dx * scale + 2 * k, M0[1] + dy * scale - 4 * k)
            out.append(curl(fig, p, d, r0 * (0.6 + 0.4 * e), 200 + 120 * e, s, 1.3 * e, op=e))


def dust_kick(fig, t, t0, out):
    """La poussière soulevée aux bottes par le recul (deux petites bouffées couleur de sable qui roulent en arrière)."""
    k = (t - t0) / 360.0
    if not 0 < k < 1:
        return
    for j, (x, r) in enumerate(((49.0, 2.4), (70.0, 1.9))):
        e = env(k, 0, 0.15, 0.45, 1)
        c = (x - 5 * k - 1.5 * j, GR - 1.4 - 2.2 * k)
        out.append(dusty(fig, c, r * (0.6 + 0.6 * k), e, j))


def dusty(fig, c, r, op, k):
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.85, 0.25, 0.7), (-0.86, 0.3, 0.68), (0.25, -0.55, 0.62)]
    balls = [(c[0] + r * dx, c[1] + r * dy, r * rr) for dx, dy, rr in J]
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), DUST[4], DUST[4])
                  for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def fx_attack(tl):
    def f(fig, ctx):
        t = tl
        front = []
        # l'étincelle de la batterie, quand le chien s'abat
        if ATT_SPARK - 10 <= t <= ATT_SPARK + 70:
            e = env(t, ATT_SPARK - 10, ATT_SPARK + 5, ATT_SPARK + 25, ATT_SPARK + 70)
            p = ctx['pan']
            front.append(spark(fig, (p[0] + 0.4, p[1] - 0.8), 3.0 * e + 0.6, op=e, rot=12))
            front.append(spark(fig, (p[0] + 2.2, p[1] - 2.8), 1.5 * e, op=e, rot=-20))
        M0, D0 = shot_at('attack')
        # l'éclair du coup à la bouche du canon
        if ATT_SHOT - 5 <= t <= ATT_SHOT + 110:
            e = env(t, ATT_SHOT - 5, ATT_SHOT + 10, ATT_SHOT + 35, ATT_SHOT + 110)
            front.append(flash(fig, add(M0, D0, 3.0 + 2 * e), 4.2 * e + 0.6, facing=ang_of(D0), op=e))
        # la balle file et sort du cadre (une courte traînée pâle)
        if ATT_SHOT <= t <= ATT_SHOT + 180:
            k = (t - ATT_SHOT) / 1000.0
            x = M0[0] + 6 + 900 * k
            y = M0[1] + 900 * k * D0[1] / max(0.2, D0[0])
            tail = [(x - 12 - 26 * min(1, k * 8), y + 0.3), (x - 6, y + 0.15), (x, y)]
            front.append('<path d="%s" fill="%s" opacity="0.75"/>' % (taper(tail, 0.2, 1.3, tip='round').d(), STEELFX[1]))
            front.append(outlined([(ellipse(x, y, 1.0, 0.95), IRON[1], 1), (ellipse(x + 0.3, y - 0.3, 0.35, 0.3), IRON[0], 1, 'n')],
                                  ink=IRON[3], w=0.9))
        if ATT_SHOT + 20 <= t <= 1100:
            gun_smoke(fig, M0, t, ATT_SHOT + 20, 1100, front)
        dust_kick(fig, t, ATT_SHOT + 30, front)
        # le filet de fumée qui monte encore du canon
        if 720 <= t <= 1100:
            k = (t - 720) / 380.0
            m = ctx['muzzle']
            e = env(k, 0, 0.2, 0.6, 1)
            pts = [(m[0] + 0.4, m[1] - 1.0), (m[0] + 1.6 + 1.1 * math.sin(k * 6), m[1] - 4 - 4 * k),
                   (m[0] + 0.5 + 1.8 * math.sin(k * 6 + 1.5), m[1] - 8 - 6 * k), (m[0] + 2.2 + 2.2 * math.sin(k * 5 + 3), m[1] - 11 - 8 * k)]
            c = crpath(pts, 14)
            sh = taper(c, 0.4, 1.2 * e + 0.2, tip='round')
            front.append(outlined([(sh, g_lin(fig, c[0], c[-1], [(0, SMOKE[2]), (1, SMOKE[0])]), 1)], ink=SINK, w=0.8, op=e))
        fig.fx_front += front
    return f


# ======================================================================== 3) la spéciale : « Lame de fond »

def ring(fig, c, rx, ry, w, op, tilt=0.0):
    """Un anneau d'eau dressé (vu de biais : une ellipse étroite), clair en haut à droite, un contour."""
    if op <= 0.02 or ry < 0.4:
        return ''
    outer = ellipse(c[0], c[1], rx + w / 2, ry + w / 2, tilt)
    inner = ellipse(c[0] + 0.1, c[1], max(0.1, rx - w / 2), max(0.1, ry - w / 2), tilt)
    sh = outer.__class__(outer.subs + inner.subs, evenodd=True)
    gr = g_lin(fig, (c[0] + rx, c[1] - ry), (c[0] - rx, c[1] + ry), [(0, '#ffffff'), (0.35, WATER[2]), (1, WATER[4])])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


def fx_gather(fig, ctx, t, back, front):
    """L'eau de mer s'enroule autour de la bouche du canon et s'y engouffre : trois filets en spirale qui se resserrent,
    un anneau d'eau qui tourne, des gouttes aspirées."""
    a, b = GATHER
    k = (t - a) / (b - a)
    if not 0 < k < 1.06:
        return
    M = ctx['muzzle']
    d = ctx['muzzle_dir']
    e = env(k, 0, 0.18, 0.8, 1.06)
    C = add(M, d, 2.0)
    for j in range(3):
        a0 = j * 120 + t * 0.75
        R0 = 13 * (1 - 0.75 * k) + 2
        pts = []
        for i in range(12):
            s_ = i / 11
            ang = math.radians(a0 + 230 * s_)
            r = R0 * (1 - 0.8 * s_)
            pts.append((C[0] + 0.55 * r * math.cos(ang) + 3.0 * (1 - s_), C[1] + r * math.sin(ang)))
        (back if j == 1 else front).append(stream(fig, pts, 0.3, 1.5 * e + 0.3, op=e))
    rr = 5.6 * (1 - 0.45 * k)
    front.append(ring(fig, add(C, d, 1.0), rr * 0.32, rr, 0.9, e * 0.9))
    for j in range(5):
        ph = (t * 0.004 + j * 0.21) % 1.0
        ang = math.radians(j * 72 + 30)
        r = 16 * (1 - ph)
        p = (C[0] + 0.7 * r * math.cos(ang) + 2, C[1] + r * math.sin(ang))
        v = sub(C, p)
        front.append(drop(fig, p[0], p[1], v[0], v[1], 0.8 + 0.4 * (1 - ph), op=e * min(1, ph * 4)))


def water_ball(fig, c, r, t, op=1.0):
    """La grosse balle d'eau : une boule bleue, un reflet, enroulée d'un filet d'écume qui tourne."""
    out = outlined([(ellipse(c[0], c[1], r, r * 0.92), g_rad(fig, (c[0] + r * 0.35, c[1] - r * 0.35), r * 1.5,
                                                               [(0, '#ffffff'), (0.25, WATER[2]), (0.65, WATER[3]), (1, WATER[4])]), 1),
                    (ellipse(c[0] + r * 0.38, c[1] - r * 0.4, r * 0.32, r * 0.22, -30), '#ffffff', 0.9, 'n')], w=1.3, op=op)
    pts = []
    for i in range(18):
        s_ = i / 17
        ang = t * 0.03 + 5.5 * s_
        pts.append((c[0] - r * 2.2 * (1 - s_) + r * 0.95 * math.cos(ang) * s_, c[1] + r * 1.05 * math.sin(ang) * (0.4 + 0.6 * s_)))
    out += outlined([(taper(crpath(pts, 18), 0.2, r * 0.36, tip='round'), g_lin(fig, pts[0], pts[-1], [(0, WATER[1]), (1, '#ffffff')]), 1)],
                    w=0.9, op=op)
    return out


def fx_special(tl):
    def f(fig, ctx):
        t = tl
        back, front = [], []
        fx_gather(fig, ctx, t, back, front)
        M0, D0 = shot_at('special')
        # le coup part : un éclair de poudre et une gerbe d'eau à la bouche du canon
        if SPEC_SHOT - 5 <= t <= SPEC_SHOT + 130:
            e = env(t, SPEC_SHOT - 5, SPEC_SHOT + 10, SPEC_SHOT + 40, SPEC_SHOT + 130)
            front.append(flash(fig, add(M0, D0, 3.0 + 2 * e), 4.6 * e + 0.6, facing=ang_of(D0), op=e))
            for j, (da, L) in enumerate(((-28, 9), (0, 12), (28, 9))):
                front.append(sheet(fig, add(M0, D0, 1.0), ang_of(D0) + da, L * e, 14 * (1 if j == 0 else -1) if j != 1 else 0, 2.2,
                                   op=e, tail=0.2))
        # la balle d'eau file à l'horizontale ; anneaux d'eau dans son sillage, un filet d'eau derrière elle
        hit = SPEC_SHOT + (IMPACT_X - M0[0] - 4) / SHOT_V
        if SPEC_SHOT <= t <= hit:
            x = M0[0] + 4 + SHOT_V * (t - SPEC_SHOT)
            y = M0[1]
            k0 = max(M0[0] + 4, x - 34)
            front.append(stream(fig, [(k0 + (x - k0) * i / 8, y + 0.6 * math.sin(i + t * 0.05)) for i in range(9)], 0.3, 3.2))
            for j in range(4):
                rx_ = M0[0] + 14 + 22 * j
                if rx_ < x - 2:
                    age = (x - rx_) / 60.0
                    front.append(ring(fig, (rx_, y), 1.2 + 1.2 * age, 3.6 + 4.5 * age, 0.8, max(0, 1 - age * 1.4)))
            front.append(water_ball(fig, (x, y), 3.6, t))
        if SPEC_SHOT + 20 <= t <= 1500:
            gun_smoke(fig, M0, t, SPEC_SHOT + 20, 1500, front, scale=0.85)
        dust_kick(fig, t, SPEC_SHOT + 40, front)
        # la gerbe sur l'ennemi : une colonne d'eau qui jaillit et s'effondre, une couronne, des gouttes en pluie
        ks = (t - hit) / 900.0
        if 0 < ks < 1:
            up = env(ks, 0, 0.12, 0.35, 0.7)
            if up > 0:
                hgt = 42 * up
                wb = 18 * (0.7 + 0.3 * up)
                back.append(column(fig, IMPACT_X, GR - hgt, wb, wb * 0.6, 1.5 * math.sin(ks * 7), ks, op=min(1, up * 1.8)))
            b_, fr = splash_crown(fig, IMPACT_X, ks, 1.9, seed=1)
            back += b_
            front += fr
            # l'éclat au point d'impact (la balle se brise en écume)
            ei = env(ks, 0, 0.03, 0.1, 0.25)
            if ei > 0:
                for j in range(4):
                    front.append(foam(fig, IMPACT_X - 4 + 4 * math.cos(j * 1.6) * (1 + 4 * ks), M0[1] + 3 * math.sin(j * 1.6) * (1 + 4 * ks) + 20 * ks,
                                      2.4 * ei + 0.6, op=ei, seed=j))
            # la pluie qui retombe tout autour
            for j in range(9):
                kk = ks * 1.4 - 0.35 - 0.05 * (j % 4)
                if 0 < kk < 0.75:
                    x = IMPACT_X - 26 + 6.5 * j + 3 * math.sin(j * 1.7)
                    y = GR - 64 + 85 * kk * kk + 10 * (j % 3)
                    if y < GR - 1:
                        front.append(drop(fig, x, y, 0.0, 60.0, 0.9 if j % 2 else 0.7, op=min(1, (0.75 - kk) * 5)))
        # l'écume s'étale au sol puis disparaît
        ef = env(t, hit + 400, hit + 560, 1850, 2040)
        if ef > 0:
            for j, (dx, r) in enumerate(((-24, 1.8), (-10, 2.4), (4, 2.2), (18, 2.4), (30, 1.7))):
                front.append(foam(fig, IMPACT_X + dx + 3 * (t - hit - 400) / 800 * (1 if dx > 0 else -1), GR - 1.0, r * ef, op=ef, seed=j))
            front.append(mound(fig, IMPACT_X, 2.8 * ef, 32, op=ef, foamy=0.7))
        fig.fx_back += back
        fig.fx_front += front
    return f


# ======================================================================== la vidéo

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


def pixel_frames(name):
    """Les images d'une animation pixel art (GIF de contrôle, fond clair retiré), à l'échelle 1, et la place du
    dessin dans ces images."""
    import numpy as np
    hdd = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd')
    sys.path.insert(0, hdd)
    import hd
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-tireur-pirate-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load(os.path.join(hdd, 'monstres', 'tireur-pirate.txt')), 0), 'RGBA')
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
    feet = (110, 214)
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
        moments = [0.4, 1.2, a_s + 0.2, a_s + 0.38, a_s + 0.43, a_s + 0.48, a_s + 0.56, a_s + 0.7, s_s + 0.1, s_s + 0.25,
                   s_s + 0.5, s_s + 0.7, s_s + 0.8, s_s + 0.86, s_s + 0.95, s_s + 1.1, s_s + 1.25, s_s + 1.45, s_s + 1.7, s_s + 1.9]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, 640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = Image.open(p)
            ImageDraw.Draw(im).text((8, 6), '%.2f' % moments[i], fill=(255, 255, 255))
            sheet_.paste(im, ((i % cols) * 640, (i // cols) * 360))
        os.makedirs(DBG, exist_ok=True)
        dst = os.path.join(DBG, 'planche.png')
        sheet_.save(dst)
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
