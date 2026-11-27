# Les effets REÇUS par l'équipe (sort d'équipe), en VECTORIEL (27/11/2026, remplaçants de ceux du pixel art) :
# soin, régénération, purification, bouclier, défense, attaque, énergie, pour les 4 éléments (feu, vent, eau, terre).
#
#   python3 refonte-graphique/ui-moderne/effets/recus.py [--voir <dossier>] [soin bouclier …]
#
# Écrit public/art/vecto/fx/<effet>-<élément>.webp (une planche par effet et par élément) et src/game/vecto-fx.ts
# (GÉNÉRÉ, lu par hd-fight.ts ; le seul rendu du jeu depuis la v0.65.0). Avec --voir : une
# planche de contrôle par effet (chaque image, ses deux calques posés sur une silhouette de héros, les 4 éléments).
#
# Comment le jeu les pose (hd-fight.ts : playReception) : chaque image a deux calques, « dos » (sous le héros) et
# « devant » (sur lui), posés aux pieds du héros qui reçoit, à sa taille (1 pixel du dessin = sa taille de pixel), jamais
# retournés (la lumière reste en haut à droite) ; « eclat » : la lueur que le jeu ajoute sur lui à certaines images.
# Repère : pieds en (0, 0), y vers le bas ; l'enveloppe commune des héros : tronc x -11…12, y -66…-20 ; tête y -114…-58.
#
# Style (celui des héros vectoriels) : des LUMIÈRES lisses (dégradés, sans contour), éclairées en haut à droite ; un seul
# contour pour les objets solides (les plaques de la défense) ; courbes (rubans, volutes, gouttes) ; jamais de rayons
# droits répétés, ni rayures, ni hachures, ni lettres ; aucun flou SVG (tout est rendu ici en images).
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RENDU = os.path.join(HERE, '..', 'heros', 'rendu-lot.cjs')
OUT_ART = os.path.join(ROOT, 'public', 'art', 'vecto', 'fx')
TS = os.path.join(ROOT, 'src', 'game', 'vecto-fx.ts')
UP = 1.0                          # pixels de planche par pixel du dessin (comme les héros vectoriels au combat)
VIEW = (-80.0, -150.0, 160.0, 162.0)
ALPHA_MIN = 4
PAD = 2

ELEMS = ('feu', 'vent', 'eau', 'terre')
# chaque élément : du cœur blanc au bord le plus sombre (les tons des héros vectoriels de l'élément)
PAL = {
    'feu': ['#fffbe8', '#fff0b0', '#ffd45c', '#ff9a3a', '#e2402e', '#a8142c'],
    'vent': ['#ffffff', '#e6fcff', '#b4eef0', '#74d8c2', '#36b394', '#1b7470'],
    'eau': ['#ffffff', '#d6f6ff', '#86dcf6', '#36aee4', '#1a6cb8', '#0f3c7e'],
    'terre': ['#fffbe8', '#fff0b0', '#ffd45c', '#e0962e', '#a8601e', '#6a3a1e'],
}
INK = {'feu': '#5a0a1e', 'vent': '#123c4a', 'eau': '#0c1846', 'terre': '#4a2a1c'}
WARM = ['#fffbe8', '#fff0b0', '#ffd45c', '#ff9a3a', '#e2402e', '#a8142c']
SMUT = ['#3e284a', '#6a4e7a', '#b8acc4']          # les taches sombres que la purification chasse (jamais du noir)


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def env(t, a, b, c, d):
    """0 avant a, monte jusqu'à b, tient jusqu'à c, redescend jusqu'à d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        return smooth((t - a) / (b - a))
    if t <= c:
        return 1.0
    return smooth(1 - (t - c) / (d - c))


class Frame:
    """Une image : deux calques (dos, devant) et leurs dégradés."""

    def __init__(self):
        self.defs, self.back, self.front, self.n = [], [], [], 0

    def _id(self):
        self.n += 1
        return 'q%d' % self.n

    @staticmethod
    def _stops(stops):
        out = []
        for s in stops:
            o, c, a = (s + (1.0,))[:3]
            out.append('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (f(o), c, f(max(0, min(1, a)))))
        return ''.join(out)

    def lin(self, p0, p1, stops):
        i = self._id()
        self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                         % (i, f(p0[0]), f(p0[1]), f(p1[0]), f(p1[1]), self._stops(stops)))
        return 'url(#%s)' % i

    def rad(self, c, r, stops, ry=None, focus=None):
        i = self._id()
        ry = ry or r
        fx = '' if not focus else ' fx="%s" fy="%s"' % (f(focus[0]), f(focus[1]))
        self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s"%s '
                         'gradientTransform="translate(%s %s) scale(1 %s) translate(%s %s)">%s</radialGradient>'
                         % (i, f(c[0]), f(c[1]), f(r), fx, f(c[0]), f(c[1]), f(ry / r), f(-c[0]), f(-c[1]), self._stops(stops)))
        return 'url(#%s)' % i

    def svg(self, layer):
        body = ''.join(self.back if layer == 'dos' else self.front)
        x, y, w, h = VIEW
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s"><defs>%s</defs>%s</svg>'
                % (f(x), f(y), f(w), f(h), ''.join(self.defs), body))


# ======================================================================== formes

def path_d(pts, close=True):
    if len(pts) < 2:
        return ''
    d = 'M%s %s' % (f(pts[0][0]), f(pts[0][1]))
    # courbe lisse (Catmull-Rom → Bézier) par les points
    n = len(pts)
    for i in range(n - (0 if close else 1)):
        p0, p1 = pts[(i - 1) % n] if (close or i > 0) else pts[0], pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += 'C%s %s %s %s %s %s' % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1]))
    return d + ('Z' if close else '')


def ribbon_pts(pts, ws):
    """Le contour d'un ruban de largeur variable le long d'une ligne (bouts effilés si la largeur y est nulle)."""
    left, right = [], []
    n = len(pts)
    for i in range(n):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = ws[i] / 2
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    return left + right[::-1]


def ribbon(fr, pts, ws, fill, op=1.0):
    if len(pts) < 3 or op <= 0.01:
        return ''
    return '<path d="%s" fill="%s" opacity="%s"/>' % (path_d(ribbon_pts(pts, ws)), fill, f(op))


def glow(fr, c, r, color, op, ry=None):
    if r <= 0.3 or op <= 0.01:
        return ''
    ry = ry or r
    g = fr.rad(c, r, [(0, color, op), (0.45, color, op * 0.45), (1, color, 0)], ry=ry)
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(c[0]), f(c[1]), f(r), f(ry), g)


def flame(fr, base, h, w, lean, ph, tones, op=1.0):
    """Une langue de flamme douce (une lumière : sans contour) : large en bas, effilée en haut, qui ondule."""
    if h < 1 or op <= 0.01:
        return ''
    n = 14
    pts, ws = [], []
    for i in range(n + 1):
        u = i / n
        x = base[0] + lean * u * u + 1.4 * math.sin(ph + u * 4.2) * u
        pts.append((x, base[1] - h * u))
        ws.append(w * (math.sin(math.pi * min(1.0, u / 0.32) * 0.5) ** 0.7) * (1 - u) ** 0.75 + 0.05)
    g = fr.lin((base[0] + w, base[1] - h), (base[0] - w, base[1]), [(0, tones[1]), (0.5, tones[2]), (1, tones[3])])
    core = [(x, y) for x, y in pts[:int(n * 0.7)]]
    return ('<g opacity="%s"><path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.85"/></g>'
            % (f(op), path_d(ribbon_pts(pts, ws)), g, path_d(ribbon_pts(core, [x * 0.42 for x in ws[:len(core)]])), tones[0]))


def mote(fr, el, x, y, s=1.0, op=1.0, rot=0.0):
    """Un grain de l'élément : braise (feu), petite plume (vent), goutte (eau), pétale d'or (terre)."""
    if op <= 0.02 or s <= 0.05:
        return ''
    P = PAL[el]
    out = glow(fr, (x, y), 4.2 * s, P[2], 0.45 * op)
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    T = lambda u, v: (x + s * (u * ca - v * sa), y + s * (u * sa + v * ca))   # noqa: E731
    if el == 'feu':
        g = fr.rad((x - 0.3 * s, y - 0.3 * s), 1.4 * s, [(0, P[0]), (0.6, P[1]), (1, P[3])])
        return out + '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>' % (f(x), f(y), f(1.3 * s), g, f(op))
    if el == 'vent':
        pts = [T(-2.6, 0.4), T(-0.6, -1.1), T(2.4, -0.6), T(0.4, 0.9)]
    elif el == 'eau':
        pts = [T(0, -2.6), T(1.3, -0.2), T(1.0, 1.2), T(0, 1.7), T(-1.0, 1.2), T(-1.3, -0.2)]
    else:
        pts = [T(0, -2.0), T(1.5, 0), T(0, 2.0), T(-1.5, 0)]
    g = fr.lin(T(1.5, -2), T(-1.5, 2), [(0, P[0]), (0.55, P[2]), (1, P[3])])
    return out + '<path d="%s" fill="%s" opacity="%s"/>' % (path_d(pts), g, f(op))


def burst(fr, c, r, color, op=1.0, rot=12.0):
    """Un éclat : étoile à quatre branches inégales aux flancs courbes, blanche au cœur (une lumière)."""
    if r < 0.5 or op <= 0.02:
        return ''
    pts = []
    for i, arm in enumerate((1.0, 0.6, 0.85, 0.5)):
        a = math.radians(rot + 90 * i)
        pts.append((c[0] + r * arm * math.cos(a), c[1] + r * arm * math.sin(a)))
        b = math.radians(rot + 90 * i + 45)
        pts.append((c[0] + r * 0.22 * math.cos(b), c[1] + r * 0.22 * math.sin(b)))
    g = fr.rad(c, r, [(0, '#ffffff'), (0.45, color), (1, color, 0.6)])
    return glow(fr, c, r * 1.6, color, 0.5 * op) + '<path d="%s" fill="%s" opacity="%s"/>' % (path_d(pts), g, f(op))


def pool(fr, rx, ry, el, op, cy=-0.5):
    """Une flaque de lumière posée au sol (sous les pieds, un ovale aplati, bords fondus)."""
    if op <= 0.01 or rx <= 0.5:
        return ''
    P = PAL[el]
    g = fr.rad((0, cy), rx, [(0, P[0], 0.9 * op), (0.35, P[1], 0.7 * op), (0.75, P[2], 0.35 * op), (1, P[3], 0)], ry=ry)
    return '<ellipse cx="0" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(cy), f(rx), f(ry), g)


def helix_runs(head, length, y0, y1, R, ph, turns, w, n=40):
    """Un ruban qui monte en spirale autour du corps : les morceaux derrière (dos) et devant, avec leurs largeurs."""
    runs = {'dos': [], 'devant': []}
    cur, side = [], None
    for i in range(n + 1):
        u = max(0.0, head - length) + min(head, length) * i / n
        if u > 1:
            break
        th = ph + 2 * math.pi * turns * u
        x, y = R * (1 - 0.25 * u) * math.cos(th), y0 + (y1 - y0) * u
        s = 'devant' if math.sin(th) > 0 else 'dos'
        q = i / n
        wd = w * math.sin(math.pi * q) ** 0.7
        if s != side and cur:
            runs[side].append(cur)
            cur = [cur[-1]]
        side = s
        cur.append(((x, y), wd))
    if len(cur) > 1:
        runs[side].append(cur)
    return runs


# ======================================================================== les effets (t de 0 à 1 sur la durée)

def fx_soin(fr, el, t, ms):
    """Une flaque de lumière s'ouvre au sol, une colonne de lueur monte derrière lui et s'en va par le haut, deux rubans
    montent en spirale autour de lui (derrière puis devant), des grains de l'élément montent en se balançant."""
    P = PAL[el]
    fr.back.append(pool(fr, 34 * (0.5 + 0.5 * smooth(t / 0.25)), 7.5, el, env(t, 0, 0.12, 0.55, 0.95)))
    c = env(t, 0.05, 0.3, 0.55, 0.95)
    if c > 0:
        top = -20 - 110 * smooth(t / 0.55)
        bot = -110 * smooth((t - 0.45) / 0.5)
        if bot - top > 4:
            g = fr.lin((0, top), (0, bot), [(0, P[1], 0), (0.3, P[1], 0.55 * c), (1, P[2], 0.35 * c)])
            fr.back.append('<path d="%s" fill="%s"/>' % (path_d([(-22, bot), (-17, (top + bot) / 2), (-9, top), (9, top), (17, (top + bot) / 2), (22, bot)]), g))
    for j, ph in enumerate((0.0, math.pi)):
        head = smooth((t - 0.04 * j) / 0.75) * 1.25
        op = env(t, 0.0, 0.1, 0.7, 1.0)
        runs = helix_runs(head, 0.55, -2, -118, 30, ph, 1.3, 4.2)
        for side, lst in runs.items():
            for run in lst:
                pts = [p for p, _ in run]
                ws = [w for _, w in run]
                tg = fr.lin((20, -110), (-20, 0), [(0, P[0]), (0.5, P[2]), (1, P[3])])
                (fr.front if side == 'devant' else fr.back).append(ribbon(fr, pts, ws, tg, op * (1 if side == 'devant' else 0.8)))
                (fr.front if side == 'devant' else fr.back).append(ribbon(fr, pts, [x * 0.35 for x in ws], P[0], op * 0.9))
    for j in range(9):
        t0 = 0.08 + 0.06 * j
        k = (t - t0) / 0.45
        if 0 < k < 1:
            x = (-26 + 6.5 * j) + 3 * math.sin(k * 6 + j)
            y = -10 - 16 * (j % 3) - 70 * k
            (fr.front if j % 2 else fr.back).append(mote(fr, el, x, y, 1.0 + 0.25 * (j % 3 == 0), env(k, 0, 0.15, 0.7, 1), rot=40 * j + 120 * k))
    e = env(t, 0.45, 0.55, 0.62, 0.85)
    if e > 0:
        fr.front.append(glow(fr, (0, -60), 30, P[1], 0.35 * e, ry=46))


def fx_regen(fr, el, t, ms):
    """La version légère du soin : une petite flaque qui respire au sol, quelques grains qui montent, une douce lueur."""
    P = PAL[el]
    br = 0.5 - 0.5 * math.cos(2 * math.pi * t)
    op = env(t, 0, 0.12, 0.8, 1.0)
    fr.back.append(pool(fr, 22 + 5 * br, 5.5, el, 0.8 * op))
    fr.back.append(glow(fr, (0, -50), 28 + 4 * br, P[2], 0.3 * op, ry=44))
    for j in range(7):
        k = (t * 1.0 + j / 7.0) % 1.0
        x = (-22 + 7.3 * j) + 2.5 * math.sin(k * 7 + j * 1.3)
        y = -6 - 84 * k
        (fr.front if j % 2 else fr.back).append(mote(fr, el, x, y, 1.45, env(k, 0, 0.2, 0.65, 1) * op, rot=60 * j + 200 * k))


def fx_purif(fr, el, t, ms):
    """Des taches sombres (violet-gris) apparaissent sur lui, s'en détachent et montent en petites volutes qui pâlissent
    et s'évaporent en un grain de lumière de l'élément ; il s'éclaire, propre."""
    P = PAL[el]
    spots = [(-5, -58, 0.0, -1, 1.8), (7, -44, 0.08, 1, 1.7), (-7, -30, 0.1, -1, 1.6), (5, -24, 0.18, 1, 1.45),
             (2, -72, 0.16, 1, 1.5), (9, -62, 0.24, -1, 1.35)]
    for j, (x, y, t0, s, sz) in enumerate(spots):
        k = (t - t0) / 0.6
        if not 0 < k < 1:
            continue
        if k < 0.25:
            a = smooth(k / 0.12)
            g = fr.rad((x + 0.6, y - 0.6), 3.4 * sz, [(0, SMUT[0], 0.95), (0.6, SMUT[1], 0.8), (1, SMUT[2], 0)])
            fr.front.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%s"/>' % (f(x), f(y), f(3.4 * sz), f(2.8 * sz), g, f(a)))
        else:
            u = (k - 0.25) / 0.75
            pts = []
            for i in range(14):
                q = i / 13
                r = (1 - 0.6 * q) * (3 + 3 * u) * sz
                a = s * (q * 4.2 + u * 3)
                pts.append((x + s * 6 * u * q + r * math.cos(a) * q, y - 22 * u * (0.4 + q) + r * math.sin(a) * q))
            col = SMUT[1] if u < 0.55 else SMUT[2]
            ws = [2.6 * sz * math.sin(math.pi * min(1, (i / 13) / 0.4) * 0.5) * (1 - i / 13) + 0.2 for i in range(14)]
            fr.front.append(ribbon(fr, pts, ws, col, (1 - smooth((u - 0.4) / 0.5)) * 0.9))
            if u > 0.45:
                fr.front.append(mote(fr, el, pts[-1][0], pts[-1][1] - 4, 1.4, env(u, 0.45, 0.6, 0.8, 1.0), rot=50 * j))
    e = env(t, 0.55, 0.68, 0.75, 0.95)
    if e > 0:
        fr.back.append(glow(fr, (0, -58), 30, P[1], 0.5 * e, ry=50))
        fr.front.append(glow(fr, (2, -62), 22, P[0], 0.3 * e, ry=36))


BUB = (0.0, -60.0, 46.0, 66.0)        # la bulle : centre, demi-largeur, demi-hauteur (posée au sol, coupée par lui)


def bubble_pt(a):
    cx, cy, rx, ry = BUB
    return (cx + rx * math.cos(math.radians(a)), cy - ry * math.sin(math.radians(a)))


def fx_bouclier(fr, el, t, ms):
    """Une bulle translucide se dessine autour de lui : son bord lumineux monte des deux côtés depuis le sol et se
    referme en haut (petit éclat), l'intérieur à peine teinté ; un reflet court sur le bord en haut à droite, puis la
    bulle se pose : le bord s'affine et pâlit."""
    P = PAL[el]
    cx, cy, rx, ry = BUB
    a0 = -math.degrees(math.asin(min(1, (0 - cy) / ry)))       # l'angle où le bord touche le sol (à droite)
    grow = smooth(t / 0.38)
    op = env(t, 0, 0.05, 0.7, 1.0)
    w = 3.2 * (1 - 0.45 * smooth((t - 0.4) / 0.4))
    if grow > 0.98:
        fill = fr.rad((cx + rx * 0.35, cy - ry * 0.4), rx * 1.2, [(0, P[0], 0.22 * op), (0.6, P[2], 0.12 * op), (1, P[3], 0.28 * op)], ry=ry * 1.2)
        dome = [bubble_pt(a) for a in range(int(a0), int(180 - a0) + 1, 6)]
        fr.back.append('<path d="%s" fill="%s"/>' % (path_d(dome + [(-rx * 0.9, 0), (rx * 0.9, 0)]), fill))
        fr.front.append('<path d="%s" fill="%s" opacity="0.3"/>' % (path_d(dome + [(-rx * 0.9, 0), (rx * 0.9, 0)]), fill))
    # le bord : deux arcs qui montent des deux côtés (dos : un liseré plus pâle derrière lui ; devant : le bord vif)
    top = a0 + (90 - a0) * grow
    for side in (1, -1):
        angs = [a0 + (top - a0) * i / 24 for i in range(25)]
        pts = [bubble_pt(a if side > 0 else 180 - a) for a in angs]
        ws = [w * (0.4 + 0.6 * math.sin(math.pi * min(1, i / 24 * 1.0 + 0.05))) for i in range(25)]
        g = fr.lin((rx, cy - ry), (-rx, 0), [(0, P[0]), (0.5, P[2]), (1, P[3])])
        fr.front.append(ribbon(fr, pts, ws, g, op))
        fr.back.append(ribbon(fr, pts, [x * 2.2 for x in ws], P[2], op * 0.3))
    if 0.3 < t < 0.6:
        k = env(t, 0.32, 0.38, 0.42, 0.58)
        fr.front.append(burst(fr, bubble_pt(90), 7, P[1], k))
    # le reflet qui court sur le bord en haut à droite
    k = (t - 0.4) / 0.35
    if 0 < k < 1:
        a = 150 - 110 * smooth(k)
        pts = [bubble_pt(a - 14 + 28 * i / 12) for i in range(13)]
        pts = [(x - (x - cx) * 0.1, y - (y - cy) * 0.1) for x, y in pts]
        fr.front.append(ribbon(fr, pts, [1.8 * math.sin(math.pi * i / 12) for i in range(13)], '#ffffff', 0.9 * env(k, 0, 0.2, 0.7, 1)))
    fr.front.append(pool(fr, 30, 5, el, 0.35 * op))


def plate_pts(el, c, s, rot):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    T = lambda u, v: (c[0] + s * (u * ca - v * sa), c[1] + s * (u * sa + v * ca))   # noqa: E731
    if el == 'feu':      # une écaille d'or en fusion : arrondie en haut, pointe en bas
        return [T(0, -5.6), T(4.4, -3.6), T(4.0, 1.4), T(0, 6.2), T(-4.0, 1.4), T(-4.4, -3.6)]
    if el == 'vent':     # une plume-plaque penchée
        return [T(-1.0, -6.4), T(3.6, -2.6), T(3.0, 3.0), T(0.6, 6.2), T(-3.2, 2.4), T(-3.6, -2.4)]
    if el == 'eau':      # un cristal de glace : pointu en haut et en bas
        return [T(0, -7.0), T(3.8, -1.2), T(3.0, 2.6), T(0, 7.0), T(-3.0, 2.6), T(-3.8, -1.2)]
    return [T(-3.4, -5.2), T(3.4, -5.6), T(5.4, -0.4), T(3.6, 5.0), T(-3.6, 5.2), T(-5.4, 0.2)]   # terre : pierre taillée


def plate(fr, el, c, s, rot, op=1.0, flash=0.0):
    """Une plaque de lumière solide (un objet : un seul contour), éclairée en haut à droite, une arête claire."""
    if op <= 0.02:
        return ''
    P = PAL[el]
    pts = plate_pts(el, c, s, rot)
    g = fr.lin((c[0] + 4 * s, c[1] - 6 * s), (c[0] - 4 * s, c[1] + 6 * s),
               [(0, P[0]), (0.45, P[1] if flash < 0.5 else '#ffffff'), (1, P[3])])
    ridge = [pts[0], (c[0] + 0.6 * s, c[1]), pts[3]] if el != 'terre' else [pts[1], (c[0] + 0.8 * s, c[1] - 0.4 * s), pts[3]]
    return ('<g opacity="%s"><path d="%s" fill="%s" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>'
            '<path d="%s" fill="none" stroke="#ffffff" stroke-width="0.8" stroke-linecap="round" opacity="0.8"/></g>'
            % (f(op), path_d(pts), g, INK[el], path_d(ridge, close=False)))


# (x, y de la place sur le corps, devant ?, angle d'arrivée en degrés, retard)
PLATES = [(0, -36, True, 270, 0.0), (-13, -38, True, 210, 0.06), (13, -38, True, 330, 0.03),
          (-21, -44, False, 160, 0.09), (21, -45, False, 20, 0.04), (-10, -64, True, 130, 0.07), (11, -65, True, 50, 0.02)]


def fx_defense(fr, el, t, ms):
    """Des plaques de l'élément arrivent de tout autour en arcs et se plaquent sur lui (une ceinture à la taille, deux
    aux épaules), avec un petit à-coup ; un éclat les parcourt, un anneau s'ouvre au sol ; puis elles pâlissent et
    s'éteignent en grains."""
    P = PAL[el]
    for j, (x, y, front, ang, d) in enumerate(PLATES):
        k = smooth((t - d) / 0.3)
        if t < d:
            continue
        a = math.radians(ang)
        dist = 60 * (1 - k)
        c = (x + dist * math.cos(a) + 14 * math.sin(math.pi * k) * math.sin(a), y - dist * math.sin(a) * 0.8 - 10 * math.sin(math.pi * k))
        bump = 1 + 0.18 * env(t, d + 0.29, d + 0.32, d + 0.34, d + 0.42)
        op = min(1, (t - d) / 0.06) * (1 - smooth((t - 0.72) / 0.18))
        fl = env(t, 0.36 + 0.02 * j, 0.4 + 0.02 * j, 0.44 + 0.02 * j, 0.5 + 0.02 * j)
        rot = (ang - 270) * 0.25 * (1 - k)
        (fr.front if front else fr.back).append(plate(fr, el, c, 1.3 * bump, rot, op, fl))
        if fl > 0.2:
            (fr.front if front else fr.back).append(glow(fr, c, 7, P[1], 0.5 * fl))
        if t > 0.75:
            u = (t - 0.75) / 0.25
            fr.front.append(mote(fr, el, c[0] + 3 * math.sin(j), c[1] - 14 * u, 0.9, env(u, 0, 0.2, 0.6, 1), rot=30 * j))
    k = (t - 0.38) / 0.4
    if 0 < k < 1:
        rx = 16 + 22 * smooth(k)
        op = 1 - smooth(k)
        for layer, a0, a1 in ((fr.back, 180, 360), (fr.front, 0, 180)):
            pts = [(rx * math.cos(math.radians(a0 + (a1 - a0) * i / 20)), -0.5 + rx * 0.22 * math.sin(math.radians(a0 + (a1 - a0) * i / 20))) for i in range(21)]
            layer.append(ribbon(fr, pts, [2.4 * math.sin(math.pi * i / 20) ** 0.5 + 0.2 for i in range(21)], P[2], 0.9 * op))


ATK_TONGUES = [(-24, -2, 30, 9.0, -5, 0.0, False), (25, -2, 27, 8.5, 5, 1.7, False), (-20, -26, 24, 7.5, -6, 2.9, False),
               (21, -32, 27, 8.0, 5, 0.9, False), (-14, -56, 20, 6.5, -5, 2.2, False), (17, -60, 22, 7.0, 4, 3.6, False),
               (-11, -1, 12, 6.0, -3, 1.1, True), (12, -1, 11, 5.5, 3, 2.5, True)]


def fx_attaque(fr, el, t, ms):
    """Une aura chaude monte autour de lui : des langues de flamme douces naissent au sol et le long de son corps,
    ondulent vers le haut puis se détachent ; des braises montent ; un ruban de son élément tourne autour de lui."""
    P = PAL[el]
    ph = t * 14
    for j, (x, y, h, w, lean, p0, front) in enumerate(ATK_TONGUES):
        g = env(t, 0.02 * j, 0.25 + 0.02 * j, 0.55, 0.85)
        lift = 26 * smooth((t - 0.6) / 0.35)
        hh = 1.35 * h * g * (0.85 + 0.15 * math.sin(ph + p0 * 2))
        (fr.front if front else fr.back).append(flame(fr, (x, y - lift), hh, 1.25 * w, lean, ph + p0, WARM, op=min(1, g * 2.5) * (1 - smooth((t - 0.75) / 0.25))))
    for j in range(7):
        k = (t - 0.15 - 0.07 * j) / 0.5
        if 0 < k < 1:
            x = -22 + 7 * j + 3 * math.sin(k * 6 + j)
            fr.front.append(mote(fr, 'feu', x, -20 - 18 * (j % 3) - 60 * k, 0.9, env(k, 0, 0.15, 0.6, 1)))
    # le ruban de l'élément qui tourne une fois autour de lui
    head = smooth((t - 0.1) / 0.6) * 1.4
    op = env(t, 0.1, 0.2, 0.65, 0.9)
    if True:
        runs = helix_runs(head, 0.5, -10, -100, 28, 0.6, 1.1, 3.4)
        for side, lst in runs.items():
            for run in lst:
                pts = [p for p, _ in run]
                ws = [w for _, w in run]
                g = fr.lin((20, -100), (-20, 0), [(0, P[0]), (0.5, P[2]), (1, P[4])])
                (fr.front if side == 'devant' else fr.back).append(ribbon(fr, pts, ws, g, op))
    e = env(t, 0.35, 0.45, 0.55, 0.75)
    if e > 0:
        fr.back.append(glow(fr, (0, -56), 34, WARM[3], 0.35 * e, ry=52))


ORBS = [((-62, -128), (-56, -96), (-28, -70), 0.0, 0.32), ((44, -142), (58, -110), (30, -84), 0.08, 0.42),
        ((76, -72), (60, -44), (26, -42), 0.18, 0.53)]


def bez2(p0, p1, p2, p3, u):
    a, b, c, d = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def fx_energie(fr, el, t, ms):
    """Trois orbes lumineux arrivent d'en haut et du côté, chacun sur sa courbe, avec une traînée effilée, et entrent dans
    la poitrine l'un après l'autre (petit éclat à chaque fois) ; au troisième, un éclat plus grand, il s'éclaire."""
    P = PAL[el]
    chest = (1.0, -52.0)
    for j, (p0, p1, p2, t0, t1) in enumerate(ORBS):
        if t0 <= t < t1:
            u = smooth((t - t0) / (t1 - t0)) * 0.7 + 0.3 * (t - t0) / (t1 - t0)
            c = bez2(p0, p1, p2, chest, u)
            pts = [bez2(p0, p1, p2, chest, max(0.0, u - 0.3 + 0.3 * i / 14)) for i in range(15)]
            ws = [0.1 + 4.2 * (i / 14) ** 1.5 for i in range(15)]
            g = fr.lin(pts[0], pts[-1], [(0, P[3], 0), (0.6, P[2], 0.8), (1, P[1], 1)])
            fr.front.append(ribbon(fr, pts, ws, g, 0.95))
            fr.front.append(glow(fr, c, 9, P[2], 0.55))
            fr.front.append('<circle cx="%s" cy="%s" r="3.2" fill="%s"/>' % (f(c[0]), f(c[1]), fr.rad((c[0] + 0.8, c[1] - 0.8), 3.4, [(0, '#ffffff'), (0.6, P[1]), (1, P[2])])))
        k = (t - t1) / 0.16
        if 0 <= k < 1:
            big = j == 2
            fr.front.append(burst(fr, chest, (8 if not big else 13) * (0.6 + 0.4 * math.sin(math.pi * k)), P[1], 1 - smooth(k), rot=12 + 25 * j))
    e = env(t, 0.5, 0.58, 0.66, 0.9)
    if e > 0:
        fr.back.append(glow(fr, (0, -56), 30, P[1], 0.45 * e, ry=48))


# nom : (fonction, durées des images (ms), éclat {image: %}, couleur de l'éclat : None = le ton pâle de l'élément)
EFFECTS = {
    'soin': (fx_soin, [70, 70, 80, 80, 80, 90, 130, 110, 90, 80, 80, 90], {4: 6, 5: 12, 6: 20, 7: 12, 8: 5}, None),
    'regeneration': (fx_regen, [100] * 10, {}, None),
    'purification': (fx_purif, [70, 80, 90, 80, 80, 80, 90, 120, 100, 90, 90], {6: 12, 7: 24, 8: 10}, None),
    'bouclier': (fx_bouclier, [60, 60, 70, 80, 130, 90, 90, 90, 90, 90, 90, 100], {4: 20, 5: 10}, None),
    'defense': (fx_defense, [60, 60, 70, 70, 120, 80, 90, 90, 90, 80, 80, 90], {4: 26, 5: 14, 6: 6}, None),
    'attaque': (fx_attaque, [60, 70, 70, 80, 90, 120, 90, 80, 80, 80, 80, 90], {4: 12, 5: 22, 6: 12, 7: 5}, '#ff783c'),
    'energie': (fx_energie, [70, 70, 70, 80, 80, 90, 120, 90, 90, 100], {3: 8, 4: 9, 5: 10, 6: 22, 7: 12, 8: 4}, None),
}


# ======================================================================== rendu, planches, table

def render_all(jobs):
    """jobs : liste de (svg, png) ; un seul navigateur pour tout."""
    tmp = tempfile.mkdtemp(prefix='vecto-recus-')
    w, h = int(round(VIEW[2] * UP)), int(round(VIEW[3] * UP))
    frames = []
    for i, (svg, png) in enumerate(jobs):
        p = os.path.join(tmp, 'f%05d.svg' % i)
        open(p, 'w').write(svg)
        frames.append([p, png])
    jp = os.path.join(tmp, 'job.json')
    json.dump({'w': w, 'h': h, 'frames': frames}, open(jp, 'w'))
    subprocess.run(['node', RENDU, jp], check=True)


def crop(path):
    a = np.asarray(Image.open(path).convert('RGBA'))
    ys, xs = np.nonzero(a[:, :, 3] >= ALPHA_MIN)
    if not len(xs):
        return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = a[y0:y1, x0:x1].copy()
    sub[sub[:, :, 3] < ALPHA_MIN] = 0
    return Image.fromarray(sub), VIEW[0] + x0 / UP, VIEW[1] + y0 / UP


def pack(cells):
    order = sorted(range(len(cells)), key=lambda i: -cells[i][0].height)

    def go(maxw):
        x = y = rowh = width = 0
        pos = {}
        for i in order:
            im = cells[i][0]
            if x + im.width + PAD > maxw:
                x, y, rowh = 0, y + rowh + PAD, 0
            pos[i] = (x, y)
            x += im.width + PAD
            width = max(width, x)
            rowh = max(rowh, im.height)
        return width * (y + rowh), pos, width, y + rowh
    widest = max(c[0].width for c in cells) + PAD
    return min((go(w) for w in range(max(256, widest), 2049, 64)), key=lambda r: r[0])[1:]


def eclat_color(name, el):
    return EFFECTS[name][3] or PAL[el][1]


def main():
    args = sys.argv[1:]
    voir = None
    if '--voir' in args:
        i = args.index('--voir')
        voir = args[i + 1]
        del args[i:i + 2]
    names = args or list(EFFECTS)
    tmp = tempfile.mkdtemp(prefix='vecto-recus-png-')
    jobs, plan = [], []
    for name in names:
        fn, ms, ecl, _ = EFFECTS[name]
        total = sum(ms)
        for el in ELEMS:
            imgs = []
            t = 0.0
            for i, m in enumerate(ms):
                fr = Frame()
                fn(fr, el, t / total, ms)
                pair = []
                for layer in ('dos', 'devant'):
                    png = os.path.join(tmp, '%s-%s-%02d-%s.png' % (name, el, i, layer))
                    jobs.append((fr.svg(layer), png))
                    pair.append(png)
                imgs.append(pair)
                t += m
            plan.append((name, el, imgs))
    print('rendu de %d images…' % len(jobs), flush=True)
    render_all(jobs)
    os.makedirs(OUT_ART, exist_ok=True)
    table = {}
    if os.path.isfile(TS):
        s = open(TS).read()
        table = json.loads(s[s.index('{'):s.rindex('}') + 1])['fx']
    for name, el, imgs in plan:
        fn, ms, ecl, _ = EFFECTS[name]
        cells, seen, dos, devant = [], {}, [], []
        for pair in imgs:
            for lst, png in zip((dos, devant), pair):
                c = crop(png)
                if c is None:
                    lst.append(-1)
                    continue
                key = (c[0].tobytes(), round(c[1], 2), round(c[2], 2))
                if key not in seen:
                    seen[key] = len(cells)
                    cells.append(c)
                lst.append(seen[key])
        pos, width, height = pack(cells)
        sheet = Image.new('RGBA', (width, height))
        for i, (im, ax, ay) in enumerate(cells):
            sheet.paste(im, pos[i])
        key = '%s-%s' % (name, el)
        sheet.save(os.path.join(OUT_ART, key + '.webp'), 'WEBP', quality=90, alpha_quality=95, method=6)
        frames = [[pos[i][0], pos[i][1], im.width, im.height, round(ax, 2), round(ay, 2)] for i, (im, ax, ay) in enumerate(cells)]
        table[key] = dict(ms=ms, dos=dos, devant=devant, frames=frames, size=[width, height], boucle=False,
                          eclat=[eclat_color(name, el), {str(k): v for k, v in ecl.items()}], up=UP)
        print('%s : %d images, planche %d × %d : %.2f Mo de mémoire graphique' % (key, len(cells), width, height, width * height * 4 / 1e6))
        if voir:
            control(voir, key, imgs, ms, el)
    body = json.dumps(dict(up=UP, fx=dict(sorted(table.items()))), separators=(',', ':'), ensure_ascii=False)
    head = ('// Généré par refonte-graphique/ui-moderne/effets/recus.py : ne pas modifier à la main.\n'
            '// Les effets REÇUS des sorts d\'équipe, en VECTORIEL (lus par hd-fight.ts : playReception). Une\n'
            '// planche art/vecto/fx/<effet>-<élément>.webp, frames [x, y, l, h] en pixels de la planche (rendue\n'
            '// ×up), (ax, ay) en pixels du dessin par rapport aux pieds du héros qui reçoit ; dos / devant : -1 = rien.\n')
    open(TS, 'w').write(head + 'export const VECTO_FX = ' + body + ' as const;\n')
    print('écrit', os.path.relpath(TS, ROOT))


def control(out_dir, key, imgs, ms, el):
    """Chaque image sur une silhouette de héros (gris), le dos dessous, le devant dessus, ×2."""
    os.makedirs(out_dir, exist_ok=True)
    S = 2
    W, H = int(VIEW[2] * S), int(VIEW[3] * S)
    fx_, fy_ = int(-VIEW[0] * S), int(-VIEW[1] * S)
    sil = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(sil)
    d.ellipse([fx_ - 13 * S, fy_ - 112 * S, fx_ + 13 * S, fy_ - 84 * S], fill=(120, 110, 150, 255))
    d.rounded_rectangle([fx_ - 16 * S, fy_ - 86 * S, fx_ + 16 * S, fy_ - 2 * S], radius=10 * S, fill=(120, 110, 150, 255))
    out = Image.new('RGB', (W * len(imgs), H), (60, 50, 84))
    for i, (dos, devant) in enumerate(imgs):
        c = Image.new('RGBA', (W, H), (60, 50, 84, 255))
        ImageDraw.Draw(c).line([(0, fy_), (W, fy_)], fill=(80, 200, 120, 255))
        c.alpha_composite(Image.open(dos).convert('RGBA').resize((W, H), Image.LANCZOS))
        c.alpha_composite(sil)
        c.alpha_composite(Image.open(devant).convert('RGBA').resize((W, H), Image.LANCZOS))
        ImageDraw.Draw(c).text((4, 4), '%d  %d ms' % (i, ms[i]), fill=(255, 255, 255, 255))
        out.paste(c.convert('RGB'), (i * W, 0))
    out.save(os.path.join(out_dir, 'recu-%s.png' % key))


if __name__ == '__main__':
    main()
