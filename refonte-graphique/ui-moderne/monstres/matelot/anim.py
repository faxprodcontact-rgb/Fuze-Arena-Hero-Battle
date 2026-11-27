# Le matelot vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/matelot/build.py)
# — pose (l'escrimeur qui sautille), attaque de base « Coup d'abordage », attaque spéciale « Vague d'abordage » — dans
# le style lisse de l'interface, à 24 images par seconde (même méthode que Kael et que son équipage, Barzul et Jessa :
# ../../heros/jessa/anim.py ; la vague et le croissant d'eau sont ceux d'Ilian, ../../heros/ilian/anim.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/matelot/anim.py            # → anim.mp4 + anim.gif dans pixel/sortie/ui/vecto/matelot/
#   python3 refonte-graphique/ui-moderne/monstres/matelot/anim.py --planche  # seulement une planche d'images clés (contrôle)
#
# Méthode : le dessin (matelot.py) est fait de morceaux ; chaque image le redessine dans une POSE. Le sabre est un seul
# objet (lame, coquille, poing) qui tourne autour de la poignée ; le bras suit le poing par cinématique inverse depuis
# l'épaule (le coude tourne sur un arc, rien ne se décroche). Les jambes aussi : les pieds restent posés (ou se
# replient en l'air) et les genoux plient dans le bon sens. Poses clés et durées reprises du pixel art.
# 1) Pose : il sautille sur place comme un escrimeur (les genoux plient et remontent), le souffle soulève le buste ; la
#    tête et le sabre suivent avec un peu de retard, les pans du bandana et du chiffon avec plus de retard ; le bras au
#    couteau se balance ; il cligne des yeux.
# 2) « Coup d'abordage » : il ramène le sabre au-dessus de l'épaule en pliant les genoux (la lame passe derrière la
#    tête), fond sur l'ennemi d'un bond rasant, taille de haut en bas : la lame laisse un croissant d'eau qui se défait
#    en gouttes ; puis il rebondit en arrière et retombe à sa place, en garde (poussière aux pieds).
# 3) « Vague d'abordage » : il se ramasse, sabre levé ; l'eau sourd à ses pieds et une vague se lève derrière lui, le
#    soulève ; il bondit de sa crête, retombe sur l'ennemi en taillant : la vague s'écrase avec lui en une grande gerbe
#    d'eau et d'écume, qui retombe en pluie ; il rebondit en arrière à sa place.
# Effets (formes rondes et courbes, dégradés, un contour, aucun flou ; l'eau : mêmes couleurs que Barzul, Jessa, Ilian).
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import matelot as B  # noqa: E402
sys.path.insert(0, B.HEROS)
from atelier import sm, ribbon, ellipse, sides, lock, f as fm  # noqa: E402
from outils import add, sub, lerp, norm, crpath, taper  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'matelot')
DBG = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/vecto-matelot'
TMP = os.environ.get('MATELOT_TMP', os.path.join(DBG, '_images'))
FPS = 24
VIEW = (14, -14, 240.0, 135.0)       # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = B.GRD
FOE_X = 200.0                        # l'ennemi (milieu), comme le pixel art (136 px devant lui)

WATER = ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e']   # l'eau (celle de Kesha, d'Ilian, de Barzul)
WINK = '#0c1846'                     # le contour de l'eau
DUST = ['#fbf2e0', '#eee2c8', '#cdb894', '#a08a70', '#7a6656']
STEELFX = ['#ffffff', '#e6eefc', '#b6c4e2']


# ======================================================================== outils (repris de Jessa et d'Ilian)

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
    """Une bosse d'eau posée au sol (l'eau qui sourd, la base de la gerbe) : dos courbe, écume sur le dessus."""
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


def wave(fig, xb, h, L, lip, r, op=1.0, foamy=1.0):
    """La vague (celle d'Ilian) : le dos qui monte du sol, la crête qui s'enroule vers l'avant (lip) en volute (r), le
    creux ; écume blanche sur la crête. Un seul contour."""
    if h < 1.5 or op <= 0.02:
        return ''
    G = GR + 0.4
    top = (xb + lip * 0.3, G - h)
    pts = [(xb - L * 0.62, G), (xb - L * 0.34, G - h * 0.22), (xb - L * 0.14, G - h * 0.62), (top[0] - r * 0.6, G - h * 0.97), top,
           (xb + lip * 0.75, G - h + r * 0.5), (xb + lip, G - h + r * 1.5), (xb + lip - r * 0.7, G - h + r * 2.3),
           (xb + lip - r * 1.5, G - h + r * 1.6), (xb + lip * 0.5, G - h + r * 1.6), (xb + L * 0.1, G - h * 0.45),
           (xb + L * 0.36, G - h * 0.08), (xb + L * 0.5, G)]
    sh = sm(pts, sharp=(0, 6, 12), t=0.9)
    gr = g_lin(fig, (xb + lip * 0.5, G - h), (xb - L * 0.3, G), [(0, WATER[2]), (0.3, WATER[3]), (0.7, WATER[4]), (1, WATER[5])])
    hollow = sm([(xb + lip - r * 1.4, G - h + r * 1.7), (xb + lip * 0.5, G - h + r * 1.7), (xb + L * 0.08, G - h * 0.45),
                 (xb + L * 0.05, G - h * 0.2), (xb - L * 0.05, G - h * 0.5), (xb + lip * 0.2, G - h + r * 1.1)])
    crest = sm([(xb - L * 0.2, G - h * 0.72), (top[0] - r * 0.7, G - h * 0.99), top, (xb + lip * 0.78, G - h + r * 0.55),
                (xb + lip, G - h + r * 1.5), (xb + lip * 0.86, G - h + r * 1.2), (xb + lip * 0.5, G - h + r * 0.55),
                (top[0] - r * 0.5, G - h + r * 0.6), (xb - L * 0.15, G - h * 0.6)])
    glint = ribbon([(xb - L * 0.42, G - h * 0.12), (xb - L * 0.26, G - h * 0.4), (xb - L * 0.1, G - h * 0.68)], [0.2, max(0.6, h * 0.025), 0.2])
    items = [(sh, gr, 1),
             (hollow, WATER[5], 0.45, 'n'),
             (crest, g_lin(fig, top, (xb - L * 0.2, G - h * 0.6), [(0, '#ffffff'), (1, WATER[1])]), min(1, foamy), 'n'),
             (glint, WATER[1], 0.7, 'n')]
    return outlined(items, w=1.5, op=op)


def column(fig, X, top, wb, wt, sway, t, op=1.0):
    """La grande gerbe (celle de Kesha) : une colonne d'eau qui monte du sol, ses bords ondulent, couronne d'écume."""
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
    cx = X + sway
    out = outlined(items, w=1.5, op=op)
    for j, (dx, dy, rr) in enumerate(((-0.62, 2.6, 0.22), (0.66, 2.2, 0.22), (-0.42, -0.6, 0.3), (0.4, -0.8, 0.32),
                                      (-0.16, -2.6, 0.38), (0.18, -3.4, 0.4), (0.0, -5.6, 0.34))):
        out += foam(fig, cx + dx * wt, top + dy * (wt / 14.0), rr * wt * (1 + 0.07 * math.sin(t * 11 + j * 1.7)), op=op, seed=j)
    return out


def ballistic(p, v, g, t):
    return (p[0] + v[0] * t, p[1] + v[1] * t + 0.5 * g * t * t)


def arc_band(C, R, a0, a1, w, taper_=0.8, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** taper_)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def crescent(fig, C, R, a0, a1, w, op=1.0, head=0.6):
    """Le croissant d'eau laissé par la lame : plein vers `head`, effilé aux deux bouts, crête d'écume, un contour."""
    if op <= 0.02 or w < 0.3 or abs(a1 - a0) < 3:
        return ''
    n = 28
    pts, ws = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        k = (t / head) if t < head else ((1 - t) / (1 - head))
        pts.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        ws.append(max(0.1, w * k ** 0.75))
    sh = ribbon(pts, ws)
    a_, b_ = int(n * 0.2), int(n * 0.88)
    crest = ribbon([(C[0] + (R + w * 0.18) * math.cos(math.atan2(p[1] - C[1], p[0] - C[0])),
                     C[1] + (R + w * 0.18) * math.sin(math.atan2(p[1] - C[1], p[0] - C[0]))) for p in pts[a_:b_]],
                   [x * 0.32 for x in ws[a_:b_]])
    gr = g_lin(fig, pts[0], pts[-1], [(0, WATER[3]), (head, WATER[2]), (1, WATER[1])])
    return outlined([(sh, gr, 1), (crest, '#ffffff', 0.9, 'n')], w=1.2, op=op)


def dusty(fig, c, r, op, k=0):
    """Une bouffée de poussière couleur de sable (quelques boules sous un contour doux)."""
    if r < 0.3 or op <= 0.02:
        return ''
    J = [(0, 0, 1), (0.85, 0.25, 0.7), (-0.86, 0.3, 0.68), (0.25, -0.55, 0.62)]
    balls = [(c[0] + r * dx, c[1] + r * dy, r * rr) for dx, dy, rr in J[:3 + k % 2]]
    gr = g_lin(fig, (c[0] + r, c[1] - r), (c[0] - r, c[1] + r), [(0, DUST[0]), (0.5, DUST[1]), (1, DUST[2])])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (fm(x), fm(y), fm(rr), DUST[4], DUST[4])
                  for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def dust_at(fig, x, t, t0, dur=380, out=None, back=False, scale=1.0):
    """La poussière qui roule quand un pied décolle ou se pose (deux petites bouffées)."""
    k = (t - t0) / dur
    if not 0 < k < 1:
        return
    for j, (dx, r) in enumerate(((-2.0, 2.2), (3.0, 1.7))):
        e = env(k, 0, 0.15, 0.45, 1)
        c = (x + dx + (-5 if back else 3) * k * (1 if j == 0 else 0.6), GR - 1.3 - 2.0 * k)
        out.append(dusty(fig, c, scale * r * (0.6 + 0.6 * k), e, j))


# ======================================================================== les poses (réglages de matelot.py)
BASE = dict(breath=0.0, crouch=0.0, lean=0.0, headx=0.0, heady=0.0, tilt=0.0, pl=0.0, sq=0.0, grin=0.0,
            tx=0.0, lift=0.0, fnx=0.0, fny=0.0, ffx=0.0, ffy=0.0, fistx=0.0, fisty=0.0, sa=B.SA0, na=0.0, behind=0.0, b=0.0)
NUM = list(BASE)


def flat(k):
    d = dict(BASE)
    for key, v in k.items():
        if key in ('head', 'fist', 'fn', 'ff'):
            d[key + 'x' if key != 'head' else 'headx'], d[key + 'y' if key != 'head' else 'heady'] = v
        else:
            d[key] = v
    return d


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [flat(k[1]) for k in keys]
    out = {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}
    # le sabre derrière la tête : une bascule nette (pas d'entre-deux), comme dans le pixel art
    i = max(j for j in range(len(ts)) if ts[j] <= t) if t >= ts[0] else 0
    out['behind'] = fl[i]['behind']
    return out


# Les décalages du poing (fist) sont ceux du pixel art (pixels du dessin), un peu agrandis là où le bras vectoriel
# doit monter plus haut ; sa = l'angle de la lame (−58° au repos ; −128° : derrière l'épaule ; +36° : taille finie).
WIND1 = dict(crouch=1.2, lean=-2.5, fist=(-6.0, -12.0), sa=-104.0, head=(0.0, 0.0), pl=1.0, na=6.0, sq=0.4, grin=0.3)
WIND2 = dict(crouch=3.2, lean=-5.0, fist=(-10.0, -19.0), sa=-136.0, behind=1.0, head=(-0.6, 0.6), pl=2.0, na=10.0, sq=1.0, grin=0.6)

# 2) « Coup d'abordage » (1000 ms, comme le pixel art).
ATTACK = [
    (0, {}),
    (90, WIND1),
    (260, WIND2), (300, dict(WIND2, crouch=3.4)),
    (350, dict(tx=20, lift=5, crouch=-1.5, lean=5, fist=(4.0, -12.0), sa=-66, fn=(5.0, -3.0), ff=(1.0, -1.5), pl=-2.0, na=-10, sq=1.0, grin=1.0)),
    (395, dict(tx=34, lift=1, crouch=1, lean=7, fist=(12.0, -2.0), sa=14, fn=(2.0, -1.0), pl=-2.0, na=-12, sq=1.0, grin=1.0)),
    (430, dict(tx=36, crouch=3, lean=7, fist=(12.0, 3.0), sa=34, head=(0.4, 0.8), pl=-2.0, na=-12, sq=1.0, grin=1.0)),
    (580, dict(tx=36, crouch=3, lean=7, fist=(12.0, 3.0), sa=36, head=(0.4, 0.8), pl=-1.0, na=-8, sq=0.8, grin=1.0)),
    (650, dict(tx=18, lift=6, crouch=-1, lean=-2, fist=(4.0, -4.0), sa=-24, fn=(2.0, -2.0), ff=(-1.0, -2.0), pl=2.0, na=0, grin=0.6)),
    (730, dict(tx=3, crouch=3, lean=-1, fist=(1.0, 0.0), sa=-44, head=(0.0, 0.6), pl=2.0, na=5, grin=0.4)),
    (820, dict(crouch=1, pl=1.0, na=4, grin=0.2)),
    (1000, {}),
]
ATT_SWING = (300, 430)        # la lame passe de derrière l'épaule à la taille finie
ATT_CUT = 395                 # le croissant d'eau se forme

# 3) « Vague d'abordage » (1600 ms, comme le pixel art).
SPECIAL = [
    (0, {}),
    (100, dict(WIND1, crouch=2.0)),
    (270, dict(WIND2, crouch=4.4)), (290, dict(WIND2, crouch=4.6)),
    (360, dict(tx=10, lift=12, crouch=-1.5, lean=2, fist=(-11.0, -20.0), sa=-140, behind=1.0, fn=(3.0, -2.0), ff=(-1.0, -1.0), pl=-1.0, na=-8, sq=1.0, grin=1.0)),
    (440, dict(tx=28, lift=30, crouch=3, lean=2, fist=(-8.0, -22.0), sa=-150, behind=1.0, fn=(5.0, -2.5), ff=(-1.5, -2.0), pl=-2.0, na=-12, sq=1.0, grin=1.0)),
    (550, dict(tx=44, lift=36, crouch=4, lean=3, fist=(-7.0, -23.0), sa=-160, behind=1.0, head=(0.0, -0.8), fn=(6.0, -3.0), ff=(-2.0, -2.5), pl=-2.0, na=-14, sq=1.0, grin=1.0)),
    (600, dict(tx=58, lift=14, crouch=0, lean=7, fist=(12.0, -3.0), sa=6, fn=(4.0, -2.0), ff=(0.0, -1.0), pl=2.0, na=-14, sq=1.0, grin=1.0)),
    (640, dict(tx=62, crouch=4, lean=7, fist=(12.0, 4.0), sa=36, head=(0.4, 0.9), pl=1.0, na=-14, sq=1.0, grin=1.0)),
    (880, dict(tx=62, crouch=4, lean=7, fist=(12.0, 4.0), sa=38, head=(0.4, 0.9), pl=-1.0, na=-12, sq=0.8, grin=1.0)),
    (1060, dict(tx=62, crouch=3, lean=5, fist=(11.0, 3.0), sa=34, pl=-1.0, na=-10, sq=0.6, grin=1.0)),
    (1150, dict(tx=62, crouch=3, lean=4, fist=(10.0, 2.0), sa=30, pl=0.0, na=-6, grin=1.0)),
    (1210, dict(tx=36, lift=10, crouch=-1, lean=-2, fist=(4.0, -4.0), sa=-22, fn=(2.0, -2.0), ff=(-1.0, -2.0), pl=2.0, na=0, grin=0.8)),
    (1280, dict(tx=12, lift=4, lean=-1, fist=(2.0, -2.0), sa=-36, pl=2.0, na=4, grin=0.6)),
    (1370, dict(crouch=3, lean=-1, fist=(1.0, 0.0), sa=-46, head=(0.0, 0.6), pl=1.0, na=4, grin=0.4)),
    (1470, dict(crouch=1, pl=0.0, na=2, grin=0.2)),
    (1600, {}),
]
SPE_SWING = (560, 640)
SPE_CRASH = 620               # la vague s'écrase sur l'ennemi avec lui

IDLE_T = 0.8                  # il sautille (une boucle de la pose du pixel art : 750 ms)


def idle_offsets(T):
    """Le sautillement de l'escrimeur : les genoux plient deux fois plus qu'ils ne se tendent, le souffle, la tête
    et le sabre en retard, les pans en plus grand retard, le bras au couteau qui se balance."""
    u = 2 * math.pi * T / IDLE_T
    bounce = 0.5 - 0.5 * math.cos(u)                         # 0 → 1 → 0 : il plie puis remonte
    br = 0.5 - 0.5 * math.cos(u * 0.5 - 0.6)                 # le souffle (deux sautillements par souffle)
    d = dict(crouch=1.6 * bounce ** 1.3, lean=0.6 * math.sin(u - 0.5), headx=0.1 * math.sin(u - 1.0),
             heady=0.55 * (0.5 - 0.5 * math.cos(u - 0.7)), tilt=0.5 * math.sin(u - 1.2),
             fistx=0.3 * math.sin(u - 1.1), fisty=0.9 * (0.5 - 0.5 * math.cos(u - 0.9)), sa=2.2 * math.sin(u - 1.3),
             pl=0.9 * math.sin(u - 1.8), na=3.5 * math.sin(u - 1.5))
    return d, br


def pose_at(T, action=None, t0=0.0):
    w = 1.0
    act = None
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
    br = br * w + P['b']
    out = dict(breath=min(1.3, br), crouch=P['crouch'], lean=P['lean'], head=(P['headx'], P['heady']), tilt=P['tilt'], pl=P['pl'],
               sq=max(0, min(1, P['sq'])), grin=max(0, min(1, P['grin'])), tx=P['tx'], lift=max(0.0, P['lift']),
               fn=(P['fnx'], P['fny']), ff=(P['ffx'], P['ffy']), fist=(P['fistx'], P['fisty']), sa=P['sa'], na=P['na'],
               behind=src['behind'])
    out['blink'] = 1.0 if (w > 0.95 and 1.95 <= (T % 3.3) < 2.04) else 0.0
    return out


# ======================================================================== les effets

def blade_tip(ctx, u=31.0, v=-3.0):
    return ctx['L'](u, v)


def fx_attack(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        F = ctx['fist']
        # la traînée de la lame qui fend l'air (de derrière l'épaule à la taille finie) : un croissant d'eau pâle
        a0, a1 = ATT_SWING
        if a0 + 20 < tl < a1 + 70:
            P = ctx['P']
            ang = P['sa'] - 4.0                                  # l'angle de la lame (vers la pointe)
            k = smooth((tl - a0) / (a1 - a0))
            start = -150 + 100 * k
            op = env(tl, a0 + 20, a0 + 50, a1, a1 + 70)
            back.append(crescent(fig, F, 30.5, start, ang, 5.2, op=op, head=0.85))
        # le croissant d'eau laissé par la taille : il reste un instant en l'air, s'étire et se défait en gouttes
        if ATT_CUT <= tl < ATT_CUT + 420:
            k = (tl - ATT_CUT) / 420.0
            C = (B.F0[0] + 36 + 12, B.F0[1] + 3)
            op = env(k, 0, 0.06, 0.4, 0.85)
            front.append(crescent(fig, C, 30.0 + 4 * k, -64 + 10 * k, 46 - 8 * k, 6.0 * (1 - 0.6 * k), op=op, head=0.7))
            for j, (da, sp) in enumerate(((-40, 60), (-14, 75), (8, 70), (30, 62), (44, 50))):
                tau = (k - 0.25 - 0.04 * j) * 0.42
                if 0 < tau < 0.42:
                    a = math.radians(da)
                    p0 = (C[0] + 31 * math.cos(a), C[1] + 31 * math.sin(a))
                    v = (sp * math.cos(a + 1.2) * 0.6 + 30, sp * math.sin(a + 1.2) * 0.6 - 40)
                    x, y = ballistic(p0, v, 260, tau)
                    if y < GR:
                        front.append(drop(fig, x, y, v[0], v[1] + 260 * tau, 0.95 if j % 2 else 0.8))
            # l'éclaboussure sur l'ennemi
            if k < 0.6:
                e = env(k, 0, 0.08, 0.25, 0.6)
                X = FOE_X - 8
                for j, (dx, dy, rr) in enumerate(((0, -24, 2.4), (3, -18, 1.8), (-2, -30, 1.6))):
                    front.append(foam(fig, X + dx + 6 * k, GR + dy - 4 * k, rr * (0.6 + k), op=e, seed=j))
        # la poussière : au bond (pied arrière), puis au retour
        dust_at(fig, 48.0, tl, 300, out=back, back=True)
        dust_at(fig, 84.0, tl, 310, out=back, back=True, scale=0.8)
        dust_at(fig, 50.0 + 3, tl, 720, out=front)
        dust_at(fig, 88.0 + 3, tl, 730, out=front, scale=0.8)
    return f


def fx_special(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        P = ctx['P']
        tx = P['tx']
        # 1) l'eau sourd à ses pieds (flaque qui bouillonne), puis la vague se lève derrière lui et le porte
        if tl < 300:
            e = smooth(tl / 280)
            front.append(mound(fig, 66, 3.6 * e, 22 * e + 4, op=e))
            for j in range(3):
                front.append(foam(fig, 52 + 14 * j, GR - 0.8, 1.4 * e, op=e, seed=j))
        if 180 <= tl < SPE_CRASH + 40:
            # la vague : sa base suit le matelot, elle monte, sa crête s'enroule et commence à se briser
            k = (tl - 180) / (SPE_CRASH + 40 - 180)
            h = monotone([180, 290, 360, 440, 550, 620, 660], [4, 14, 24, 40, 46, 30, 10], tl)
            xb = monotone([180, 360, 550, 620, 660], [46, 50 + 10, 58 + 44, FOE_X - 30, FOE_X - 14], tl)
            lip = monotone([180, 440, 600, 660], [6, 18, 26, 34], tl)
            r = 3 + 0.12 * h
            op = env(tl, 180, 230, SPE_CRASH - 30, SPE_CRASH + 20)
            back.append(wave(fig, xb, h, 18 + 0.9 * h, lip, r, op=op))
            # l'écume qui vole de la crête
            if tl > 400:
                for j in range(3):
                    tau = ((tl - 400) / 1000.0 + 0.08 * j) % 0.24
                    p = (xb + lip * 0.3 - 3 + 2 * j, GR - h - 1)
                    x, y = ballistic(p, (40 + 10 * j, -50), 300, tau)
                    front.append(drop(fig, x, y, 40, -50 + 300 * tau, 0.8, op=op))
        # 2) la traînée de la lame quand il retombe en taillant
        a0, a1 = SPE_SWING
        if a0 < tl < a1 + 80:
            F = ctx['fist']
            k = smooth((tl - a0) / (a1 - a0))
            op = env(tl, a0, a0 + 20, a1, a1 + 80)
            back.append(crescent(fig, F, 31.0, -160 + 120 * k, P['sa'] - 4, 6.4, op=op, head=0.85))
        # 3) la vague s'écrase sur l'ennemi avec lui : grande gerbe, nappes, écume, pluie de gouttes
        if SPE_CRASH <= tl < SPE_CRASH + 900:
            k = (tl - SPE_CRASH) / 900.0
            X = FOE_X - 4
            e = env(k, 0, 0.08, 0.45, 0.8)
            top = GR - 44 * smooth(min(1, k * 4)) * (1 - smooth((k - 0.35) / 0.4))     # elle retombe (pas de fantôme)
            back.append(column(fig, X, top, 22 * (1 - 0.3 * k), 12 + 4 * k, 2.0, tl / 1000.0, op=min(1, 3 * e)))
            for j, (dx, ang, L, bd, w) in enumerate(((-9, -128, 18, -40, 4.4), (-4, -104, 26, -22, 5.0), (4, -76, 25, 22, 5.0),
                                                     (9, -52, 18, 40, 4.4))):
                L_ = 1.5 * L * (0.4 + 0.6 * min(1, k * 3)) * (1 - 0.4 * max(0, k - 0.45) * 2)
                (back if j in (0, 3) else front).append(sheet(fig, (X + dx, GR + 0.2), ang, L_, bd, w, op=min(1, e * 1.6),
                                                              tail=max(0, k - 0.4) * 1.3))
            front.append(mound(fig, X, 6 * e, 26, op=min(1, e * 1.5)))
            for j in range(4):
                front.append(foam(fig, X - 12 + 8 * j, GR - 1.2, 2.2 * e, op=min(1, e * 1.5), seed=j))
            # la pluie de gouttes qui retombe
            for j, (vx, vy) in enumerate(((-60, -150), (45, -165), (-95, -110), (90, -120), (-25, -185), (20, -190), (120, -80), (-130, -70))):
                tau = k * 0.95 - 0.04 * (j % 4)
                if 0 < tau < 0.95:
                    x, y = ballistic((X, GR - 8), (vx, vy), 330, tau)
                    if y < GR:
                        front.append(drop(fig, x, y, vx, vy + 330 * tau, 1.15 if j % 2 else 0.9))
            # le grand croissant d'eau de la taille
            kc = min(1.0, k / 0.5)
            C = (B.F0[0] + 62 + 12, B.F0[1] + 4)
            front.append(crescent(fig, C, 31.0 + 5 * kc, -70 + 12 * kc, 48 - 10 * kc, 7.6 * (1 - 0.6 * kc),
                                  op=env(kc, 0, 0.05, 0.4, 0.95), head=0.7))
        # la poussière : à l'envol, puis au retour
        dust_at(fig, 48.0, tl, 290, out=back, back=True, scale=1.1)
        dust_at(fig, 52.0, tl, 1360, out=front)
        dust_at(fig, 90.0, tl, 1370, out=front, scale=0.8)
    return f


# ======================================================================== le rendu

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


def shadow_layer(w, h, view, cx_draw, lift=0.0, floor_y=GR):
    """L'ombre au sol sous lui (elle pâlit et rétrécit quand il saute)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (cx_draw - x0) * k
    s = max(0.45, 1 - lift / 50.0)
    ImageDraw.Draw(sh).ellipse([cx - 27 * s * k, fy - 2.8 * k, cx + 27 * s * k, fy + 2.8 * k], fill=(10, 4, 24, int(150 * s)))
    return sh.filter(ImageFilter.GaussianBlur(2.2 * k))


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


def compose(pngs, poses, w, h, view):
    bg = background(w, h, view)
    for p, P in zip(pngs, poses):
        im = bg.copy()
        im.alpha_composite(shadow_layer(w, h, view, 68 + P['tx'], P['lift']))
        im.alpha_composite(Image.open(p))
        im.convert('RGB').save(p)


def timeline():
    seq = [('idle', 3 * IDLE_T), ('attack', ATTACK[-1][0] / 1000), ('idle', 2 * IDLE_T), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 2 * IDLE_T), ('special', SPECIAL[-1][0] / 1000), ('idle', 2 * IDLE_T)]
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
    dessin dans ces images."""
    import numpy as np
    hdd = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'hd')
    sys.path.insert(0, hdd)
    import hd
    g = Image.open(os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'anim-matelot-%s.gif' % name))
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert('RGBA')
        im = im.resize((im.width // 4, im.height // 4), Image.NEAREST)
        a = np.array(im)
        key = (a[:, :, 0] == 232) & (a[:, :, 1] == 236) & (abs(a[:, :, 2].astype(int) - 241) <= 1)
        a[key, 3] = 0
        out.append((Image.fromarray(a), g.info.get('duration', 100)))
    sprite = Image.fromarray(hd.frame(hd.load(os.path.join(hdd, 'monstres', 'matelot.txt')), 0), 'RGBA')
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
    feet = (100, 214)
    crop = fond.crop((cx0, cy0, cx0 + CW, cy0 + CH))
    PW, PH = 632, 359
    seq = [('idle', 1.6), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('special', SPECIAL[-1][0] / 1000), ('idle', 0.8)]
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
        moments = [0.1, 0.3, 0.5, a_s + 0.09, a_s + 0.28, a_s + 0.35, a_s + 0.4, a_s + 0.45, a_s + 0.6, a_s + 0.66, a_s + 0.75,
                   s_s + 0.28, s_s + 0.36, s_s + 0.45, s_s + 0.55, s_s + 0.6, s_s + 0.65, s_s + 0.8, s_s + 1.0, s_s + 1.25]
        args = [a for a in sys.argv[1:] if a != '--planche']
        if args:
            moments = [float(x) for x in args]
        res = [frame_svg(T, segs) for T in moments]
        pngs = render([r[0] for r in res], 640, 360, 'p')
        compose(pngs, [r[1] for r in res], 640, 360, VIEW)
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
    compose(pngs, [r[1] for r in res], VW, VH, VIEW)
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
