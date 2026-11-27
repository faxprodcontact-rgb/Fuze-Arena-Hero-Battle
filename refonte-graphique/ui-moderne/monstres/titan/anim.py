# Le titan vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/titan/build.py) —
# la respiration de la montagne, l'attaque de base « Poing de la montagne », l'attaque spéciale « Réveil de la
# montagne » — dans le style lisse de l'interface (comme Kael : heros/kael/anim.py, et Garvin pour la roche).
#
#   python3 refonte-graphique/ui-moderne/monstres/titan/anim.py               # → anim.mp4 + anim.gif (sortie/ui/vecto/titan/)
#   python3 refonte-graphique/ui-moderne/monstres/titan/anim.py --planche [t…]  # une planche d'images clés (contrôle)
#   (images de travail : dans $TITAN_TMP, sinon un dossier temporaire du système ; jamais dans le dépôt)
#
# Méthode : chaque image redessine titan.py dans une POSE (le haut du corps se cabre ou s'écrase en basculant autour
# des hanches, la tête suit en retard, les jambes plient, pieds à plat ; chaque bras suit son poing par cinématique
# inverse et plie au vrai coude, le poing tourne avec l'avant-bras). C'est une montagne : tout est lourd et lent —
# longues préparations, coups courts, arrêts sur l'image, retours lents ; ses cristaux, ses yeux et ses signes luisent
# avec le souffle et flambent pendant la charge. Poses clés et durées reprises du pixel art, reliées par des courbes
# douces sans dépassement, 24 images/s.
# Les effets (poussière, cailloux, éclats de roche et de grenat projetés en cloche, traînée du poing, éclair d'impact,
# fissure au sol, pics de roche et cristaux qui jaillissent sous les héros, étincelles de grenat en volutes, blocs
# soulevés) : dégradés, un seul contour par objet, aucun flou ; jamais de rayons droits répétés.
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
import titan as K  # noqa: E402
from atelier import sm, ribbon, ellipse, f as fm  # noqa: E402

ROOT = K.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'titan')
TMP = os.environ.get('TITAN_TMP') or os.path.join(tempfile.gettempdir(), 'titan-anim')
FPS = 24
VIEW = (-6.0, -16.0, 480.0, 270.0)   # la scène de la vidéo, en pixels du dessin (16/9)
VW, VH = 1280, 720
GR = K.GRD
INK = '#1f1238'
DINK = '#4e3a48'                     # le contour de la poussière
ENEMY_X = 392.0                      # le héros visé (au sol, à droite)
TARGETS = [356.0, 392.0, 430.0]      # la spéciale frappe sous chaque héros
FIST_F = (240.0, GR)                 # le bout du poing lointain posé (là où il frappe)
FIST_N = (68.0, GR)
GAR = K.GAR
ROCK = K.ROCK

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


PAIRS = {'head': ('headx', 'heady'), 'ff': ('ffx', 'ffy'), 'fn': ('fnx', 'fny')}
SCAL = ['bx', 'by', 'pitch', 'tilt', 'gape', 'glow', 'frot', 'nrot', 'sway', 'inhale']
NUM = SCAL + [k for v in PAIRS.values() for k in v]


def flat(k):
    d = {n: 0.0 for n in NUM}
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
# 2) « Poing de la montagne » (pixel : ATTAQUE, 1,7 s). Longue préparation : le poids passe en arrière, l'avant du
# corps se cabre, la tête se relève en grondant, le poing lointain quitte le sol et monte à hauteur du col (des
# cailloux en tombent) ; il tient. Puis tout s'abat (traînée de poussière) : le poing frappe le sol un peu plus loin,
# le corps s'écrase dessus, la tête plonge. Impact tenu, le sol tremble ; sous la cible, la terre se soulève en pics.
# Retour lent : le poing glisse à sa place.
ATTACK = [
    (0, {}),
    (150, dict(bx=-1.0, pitch=-1.5, ff=(1.0, -6.0), glow=0.3, frot=-4)),
    (300, dict(bx=-2.5, by=-1.0, pitch=-4.0, head=(-1.0, -2.0), tilt=-3.0, ff=(4.0, -20.0), glow=0.8, gape=0.3, frot=-14)),
    (470, dict(bx=-4.0, by=-2.0, pitch=-6.5, head=(-2.0, -3.4), tilt=-5.0, ff=(9.0, -33.0), glow=1.5, gape=0.6, frot=-24, sway=-1.5)),
    (770, dict(bx=-4.6, by=-2.6, pitch=-7.4, head=(-2.2, -4.0), tilt=-6.0, ff=(11.0, -37.0), glow=2.0, gape=0.8, frot=-28, sway=1.0)),
    (800, dict(bx=0.0, by=-1.0, pitch=-2.5, head=(0.0, -1.0), tilt=-1.0, ff=(11.0, -14.0), glow=2.2, gape=0.6, frot=-10, sway=-1.0)),
    (830, dict(bx=4.0, by=3.0, pitch=1.6, head=(2.0, 3.0), tilt=4.0, ff=(9.0, 0.0), glow=3.0, gape=1.1, frot=0, sway=3.0)),
    (960, dict(bx=4.0, by=3.0, pitch=1.6, head=(2.0, 4.0), tilt=4.0, ff=(9.0, 0.0), glow=2.5, gape=1.0, sway=-2.0)),
    (1190, dict(bx=3.0, by=2.0, pitch=1.0, head=(1.0, 3.0), tilt=3.0, ff=(9.0, 0.0), glow=1.6, gape=0.6, sway=0.8)),
    (1340, dict(bx=2.0, by=1.0, pitch=0.5, head=(1.0, 2.0), tilt=1.5, ff=(6.0, -2.5), glow=0.9, gape=0.3)),
    (1500, dict(bx=1.0, ff=(2.5, -1.0), glow=0.3)),
    (1700, {}),
]
ATTACK_HIT = 830

# 3) « Réveil de la montagne » (pixel : SPECIALE, 2,37 s ; dégâts à TOUS les héros). Il se ramasse, puis se dresse :
# le corps monte sur ses jambes, l'avant se cabre, la tête se renverse en rugissant, les DEUX poings quittent le sol ;
# ses cristaux flambent (étincelles de grenat qui montent en volutes, blocs qui se soulèvent autour de lui). Il s'abat :
# les deux poings frappent le sol ensemble (éclair, secousse, poussière). Une vague de pics de roche et de cristaux court
# vers les héros et jaillit sous CHACUN d'eux, les blocs volent, puis tout s'effrite ; il se redresse, les cristaux
# s'éteignent.
SPECIAL = [
    (0, {}),
    (150, dict(bx=1.0, by=3.0, pitch=1.4, head=(1.0, 2.0), tilt=2.0, glow=1.0)),
    (320, dict(bx=-1.0, by=-5.0, pitch=-3.0, head=(-1.0, -3.0), tilt=-4.0, fn=(0.0, -8.0), ff=(2.0, -16.0), glow=2.0, gape=0.5,
               frot=-10, nrot=6)),
    (490, dict(bx=-3.0, by=-11.0, pitch=-6.5, head=(-3.0, -6.0), tilt=-8.0, fn=(-2.0, -22.0), ff=(6.0, -32.0), glow=3.0, gape=1.0,
               frot=-22, nrot=12, sway=-2.0)),
    (800, dict(bx=-4.0, by=-14.0, pitch=-8.5, head=(-4.0, -8.0), tilt=-10.0, fn=(-2.0, -30.0), ff=(10.0, -42.0), glow=4.0, gape=1.4,
               frot=-28, nrot=16, sway=1.5)),
    (890, dict(bx=-4.2, by=-14.4, pitch=-8.8, head=(-4.0, -8.4), tilt=-10.4, fn=(-2.0, -31.0), ff=(10.0, -43.0), glow=4.0, gape=1.4,
               frot=-28, nrot=16, sway=-1.0)),
    (920, dict(bx=1.0, by=-3.0, pitch=-2.0, head=(0.0, -1.0), tilt=-2.0, fn=(0.0, -10.0), ff=(9.0, -14.0), glow=4.0, gape=0.9,
               frot=-8, nrot=5, sway=-2.0)),
    (950, dict(bx=3.0, by=5.0, pitch=1.6, head=(2.0, 5.0), tilt=5.0, fn=(0.0, 0.0), ff=(7.0, 0.0), glow=4.0, gape=1.3, sway=3.5)),
    (1210, dict(bx=3.0, by=5.0, pitch=1.6, head=(2.0, 5.0), tilt=4.0, ff=(7.0, 0.0), glow=3.4, gape=1.1, sway=-2.0)),
    (1510, dict(bx=2.0, by=3.0, pitch=1.0, head=(1.0, 3.0), tilt=2.0, ff=(7.0, 0.0), glow=2.4, gape=0.6, sway=0.8)),
    (1920, dict(bx=1.0, by=1.0, pitch=0.5, head=(0.0, 1.0), ff=(4.0, -1.5), glow=1.2, gape=0.2)),
    (2200, dict(ff=(1.0, 0.0), glow=0.4)),
    (2370, {}),
]
SP_SLAM = 950

# ======================================================================== la respiration (en boucle)
IDLE = 2.37                          # un souffle (s) : le rythme lent du pixel art


def idle_offsets(T):
    u = 2 * math.pi * T / IDLE
    br = 0.5 - 0.5 * math.cos(u)
    return dict(inhale=br, heady=0.5 * math.sin(u - 1.3), headx=0.2 * math.sin(u - 1.6), tilt=0.6 * math.sin(u - 1.4),
                glow=0.45 * (0.5 - 0.5 * math.cos(u - 0.6)), gape=0.12 + 0.1 * math.sin(u - 1.5),
                sway=0.9 * math.sin(u - 2.0), by=0.0)


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
        w = min(1.0, max(0.0, 1 - tl / 200), max(0.0, (tl - (dur - 300)) / 300))
        w = w * w * (3 - 2 * w)
    idl = idle_offsets(T)
    src = act or flat({})
    P = {n: src[n] + w * idl.get(n, 0.0) for n in NUM}
    P['breath'] = P.pop('inhale')
    P['head'] = (P.pop('headx'), P.pop('heady'))
    P['ff'] = (P.pop('ffx'), P.pop('ffy'))
    P['fn'] = (P.pop('fnx'), P.pop('fny'))
    P['glow'] = max(0.0, P['glow'])
    P['gape'] = max(0.0, P['gape'])
    ph = T % (2 * IDLE)
    P['blink'] = 1.0 if (w > 0.95 and 1.62 <= ph < 1.74) else 0.0
    return P, tl


# ======================================================================== les effets (un seul contour, aucun flou)

def outlined(shapes_fills, ink=INK, w=1.0, op=1.0):
    """Un objet d'effet : ses formes réunies sous UN contour (toutes les silhouettes épaisses, puis les couleurs) ;
    une 4e valeur dans un élément = pas de silhouette pour lui (un reflet peint dedans)."""
    if op <= 0.01:
        return ''
    sil = ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        sh.d(), ink, ink, fm(w)) for sh, fl, o, *rest in shapes_fills if not rest)
    col = ''.join('<path d="%s" fill="%s"%s/>' % (sh.d(), fl, '' if o == 1 else ' opacity="%g"' % o) for sh, fl, o, *rest in shapes_fills)
    return '<g opacity="%g">%s%s</g>' % (max(0, min(1, op)), sil, col)


def g_lin(fig, p0, p1, stops):
    return fig.lin(p0[0], p0[1], p1[0], p1[1], stops)


def g_rad(fig, c, r, stops, ry=None):
    return fig.rad(c[0], c[1], r, ry or r, stops)


def dust(fig, cx, cy, r, op=1.0, seed=0):
    """Un nuage de poussière de terre, posé au sol : quelques boules de tailles inégales sous un contour."""
    if r < 0.4 or op <= 0.02:
        return ''
    a = 0.15 * math.sin(seed * 1.7)
    balls = [(cx, cy - 0.45 * r, r), (cx + (0.95 + a) * r, cy - 0.05 * r, 0.68 * r), (cx - (0.9 - a) * r, cy + 0.05 * r, 0.6 * r),
             (cx + 0.3 * r, cy - 1.05 * r, 0.5 * r)]
    gr = g_lin(fig, (cx + r, cy - 1.4 * r), (cx - r, cy + r * 0.5), [(0, '#f6ead0'), (0.5, '#d2b894'), (1, '#94786c')])
    sil = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.0"/>' % (fm(x), fm(y), fm(rr), DINK, DINK) for x, y, rr in balls)
    col = ''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(y), fm(rr), gr) for x, y, rr in balls)
    return '<g opacity="%g">%s%s</g>' % (op, sil, col)


ROCKP = [(-1, -0.6), (0.2, -1.1), (1.1, -0.35), (0.85, 0.85), (-0.55, 1.0)]


def chunk(fig, x, y, s=2.0, rot=0.0, op=1.0):
    """Un éclat de roche (sa roche, éclairée en haut à droite)."""
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in ROCKP]
    sh = sm(pts, sharp=(0, 1, 2, 3, 4), t=0.4)
    gr = g_lin(fig, (x + s, y - s), (x - s, y + s), [(0, '#c4ba98'), (0.5, ROCK.base), (1, ROCK.deep)])
    return outlined([(sh, gr, 1)], w=1.0, op=op)


def shard(fig, x, y, s=2.4, rot=0.0, op=1.0):
    """Un éclat de grenat : un petit cristal pointu aux deux bouts (face claire, face sombre)."""
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(px, py):
        return (x + s * (px * c - py * si), y + s * (px * si + py * c))
    sh = sm([P(0, -1.3), P(0.5, -0.2), P(0.1, 1.1), P(-0.45, 0.1)], sharp=(0, 1, 2, 3), t=0.3)
    dk = sm([P(0, -1.3), P(0.02, 0.0), P(0.1, 1.1), P(-0.45, 0.1)], sharp=(0, 1, 2, 3), t=0.3)
    return outlined([(sh, GAR.light, 1), (dk, GAR.shadow, 0.85, 'n'), (ellipse(*P(0.18, -0.4), s * 0.12, s * 0.2), '#ffffff', 0.8, 'n')], w=0.9, op=op)


def spark(fig, x, y, r=1.0, op=1.0):
    """Une étincelle de grenat : un cœur rosé dans une lueur (dégradé radial, sans flou)."""
    if op <= 0.02:
        return ''
    glow = g_rad(fig, (x, y), r * 3.4, [(0, '#ff6a86', 0.55 * op), (1, '#ff4a6a', 0)])
    core = g_rad(fig, (x - r * 0.2, y - r * 0.2), r, [(0, '#ffffff', op), (0.5, '#ffc0cc', op), (1, '#ff5a78', op)])
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/><circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(r * 3.4), glow, fm(x), fm(y), fm(r), core)


def flash(fig, x, y, r, op):
    """L'éclair d'impact : une lueur blanc doré (dégradé radial) aplatie au sol."""
    if op <= 0.02:
        return ''
    gr = g_rad(fig, (x, y), r, [(0, '#fff6d6', 0.9 * op), (0.45, '#ffe0a8', 0.55 * op), (1, '#ffb070', 0)], ry=r * 0.55)
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(x), fm(y), fm(r), fm(r * 0.55), gr)


def crack(fig, x0, x1, grow, seed=0, op=1.0):
    """Une fissure qui court au sol (de x0 vers x1) : une fente sombre en zigzag doux, son bord éclairé."""
    if grow <= 0.02 or op <= 0.02:
        return ''
    xe = x0 + (x1 - x0) * min(1.0, grow)
    n = max(2, int(abs(xe - x0) / 7))
    pts = [(x0 + (xe - x0) * i / n, GR + 0.8 + (0.9 if (i + seed) % 2 else -0.3) * (0.4 + 0.6 * ((i * 0.618 + seed * 0.3) % 1)))
           for i in range(n + 1)]
    ws = [0.2] + [1.5 * (1 - i / (n + 1)) + 0.3 for i in range(1, n)] + [0.15]
    sh = ribbon(pts, ws)
    hl = ribbon([(x, y + 0.9) for x, y in pts], [w * 0.4 for w in ws])
    return '<g opacity="%g"><path d="%s" fill="#2a1c34"/><path d="%s" fill="#c8b490" opacity="0.6"/></g>' % (op, sh.d(), hl.d())


def spike(fig, x, h, w, lean=0.0, sink=0.0, kind='roche', op=1.0, seed=0):
    """Un pic qui jaillit du sol : roche (facettes, pointe un peu émoussée) ou cristal de grenat ; `sink` le fait
    rentrer dans le sol en s'effritant (il descend et se raccourcit)."""
    if h < 0.8 or op <= 0.02 or sink >= 1:
        return ''
    hh = h * (1 - sink)
    base = GR + 1.5
    tip = (x + lean, base - hh)
    if kind == 'grenat':
        body, left, tipl, tipr, glint = K.crystal((x, base), math.degrees(math.atan2(lean, hh)), hh + 2, w)
        x0, y0, x1, y1 = body.bbox()
        gr = g_lin(fig, (x1, y0), (x0, y1), [(0, GAR.light), (0.55, GAR.base), (1, GAR.shadow)])
        return outlined([(body, gr, 1), (left, GAR.shadow, 0.8, 'n'), (tipr, K.lite_(GAR.light, 0.35), 0.9, 'n'),
                         (glint, '#ffffff', 0.7, 'n')], w=1.0, op=op)
    j = 0.12 * math.sin(seed * 2.1)
    pts = [(x - w / 2, base), (x - w * (0.36 + j), base - hh * 0.45), (tip[0] - w * 0.1, tip[1] + 1.0), (tip[0] + w * 0.12, tip[1] + 0.4),
           (x + w * (0.3 - j), base - hh * 0.55), (x + w / 2, base)]
    sh = sm(pts, sharp=(0, 2, 3, 5), t=0.6)
    lit = sm([(tip[0] + w * 0.04, tip[1] + 1.0), (tip[0] + w * 0.12, tip[1] + 0.4), (x + w * (0.3 - j), base - hh * 0.55), (x + w / 2, base),
              (x + w * 0.08, base), (x + w * 0.02, base - hh * 0.5)], sharp=(0, 1, 3, 4), t=0.5)
    gr = g_lin(fig, (x + w / 2, tip[1]), (x - w / 2, base), [(0, '#b4aa8c'), (0.5, ROCK.base), (1, ROCK.deep)])
    return outlined([(sh, gr, 1), (lit, '#cfc4a0', 0.55, 'n')], w=1.0, op=op)


def arc_band(C, R, a0, a1, w, n=28):
    """Un croissant le long d'un arc (de a0, fin, à a1, plein) autour de C ; angles en degrés (y vers le bas)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        ww = w * (t ** 0.8)
        outer.append((C[0] + R * math.cos(a), C[1] + R * math.sin(a)))
        inner.append((C[0] + (R - ww) * math.cos(a), C[1] + (R - ww) * math.sin(a)))
    return sm(outer + inner[::-1], sharp=(0, n, n + 1), t=0.5)


def smear(fig, C, R, a0, a1, w, op=1.0):
    """La traînée du poing qui s'abat : un croissant de poussière (dégradé), sans contour dur."""
    if op <= 0.02:
        return ''
    pa = (C[0] + R * math.cos(math.radians(a0)), C[1] + R * math.sin(math.radians(a0)))
    pb = (C[0] + R * math.cos(math.radians(a1)), C[1] + R * math.sin(math.radians(a1)))
    body = arc_band(C, R + w * 0.5, a0, a1, w)
    g1 = g_lin(fig, pa, pb, [(0, '#d2b894', 0.0), (0.5, '#e2cca8', 0.6), (1, '#f6ead0', 0.95)])
    return '<g opacity="%g"><path d="%s" fill="%s"/></g>' % (op, body.d(), g1)


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


def thrown(fig, origin, bits, t, out):
    """Les éclats projetés en cloche (roche 'r', grenat 'g') ; t en secondes depuis le choc ; ils roulent une fois posés."""
    for i, (vx, vy, kind, size, spin) in enumerate(bits):
        x = origin[0] + vx * t
        y = origin[1] - vy * t + 0.5 * 260 * t * t
        landed = y >= GR - size * 0.6
        if landed:
            # temps de l'atterrissage
            disc = vy * vy - 520 * (origin[1] - (GR - size * 0.6))
            tl = (vy + math.sqrt(max(0.0, disc))) / 260
            x = origin[0] + vx * tl + vx * 0.15 * min(1.0, (t - tl) * 3)
            y = GR - size * 0.6
            rot = i * 47 + spin * tl
            op = max(0.0, 1 - (t - tl) / 0.5)
        else:
            rot = i * 47 + spin * t
            op = 1.0
        if kind == 'r':
            out.append(chunk(fig, x, y, size, rot, op))
        else:
            out.append(shard(fig, x, y, size, rot, op))


HIT_BITS = [(-30, 70, 'r', 2.6, 300), (-12, 92, 'r', 1.8, -380), (16, 84, 'r', 2.8, 240), (34, 66, 'r', 1.7, 420), (46, 52, 'g', 2.4, 260),
            (-40, 50, 'r', 1.4, -260), (24, 100, 'g', 2.0, -300), (4, 104, 'r', 1.5, 340), (54, 40, 'r', 1.3, 180)]
TGT_BITS = [(-20, 76, 'r', 2.0, 300), (16, 90, 'r', 2.4, -280), (28, 70, 'g', 2.0, 360), (-28, 56, 'r', 1.5, 240), (6, 98, 'g', 1.7, -320),
            (36, 46, 'r', 1.3, 200)]


def eruption(fig, X, tl, back, front, big=False, seed=0):
    """Sous un héros : la terre se soulève en pics de roche (et en grands cristaux pour la spéciale), puis s'effrite."""
    t = tl / 1000.0
    if t < 0:
        return
    grow = min(1.0, t / 0.09)
    sink = 0.0 if t < 0.42 else min(1.0, (t - 0.42) / 0.45)
    op = 1.0 if t < 0.75 else max(0.0, 1 - (t - 0.75) / 0.3)
    if big:
        specs = [(-9, 46, 15, -4, 'grenat', 0), (9, 60, 17, 3, 'grenat', 0), (24, 28, 11, 8, 'grenat', 0),
                 (-24, 34, 15, -7, 'roche', 1), (20, 40, 16, 7, 'roche', 1), (36, 22, 11, 8, 'roche', 1), (-37, 18, 10, -7, 'roche', 1)]
        k = 0.62
    else:
        specs = [(-1, 56, 17, 1, 'roche', 0), (-18, 26, 13, -6, 'roche', 1), (17, 32, 14, 6, 'roche', 1), (31, 16, 10, 7, 'roche', 1)]
        k = 0.78
    if t < 0.5:
        back.append(crack(fig, X - 34, X + 40, min(1.0, t / 0.15), seed=seed + 5, op=1 - max(0.0, (t - 0.3) / 0.2)))
    for i, (dx, h, w, lean, kind, plan) in enumerate(specs):
        lag = 0.025 * (i % 3)
        g_ = min(1.0, max(0.0, (t - lag) / 0.09))
        (back if plan == 0 else front).append(spike(fig, X + dx, h * k * (0.65 + 0.35 * g_) if g_ > 0 else 0, w * k, lean * k,
                                                    sink=sink, kind=kind, op=op, seed=i + seed))
    if t < 0.08:
        front.append(flash(fig, X, GR - 6, 26, 1 - t / 0.08))
    thrown(fig, (X - 2, GR - 14), TGT_BITS, t, front)
    if 0.04 < t < 0.75:
        hol = env(t, 0.04, 0.15, 0.4, 0.75)
        front.append(dust(fig, X - 22, GR - 1, 6 + 8 * min(1, t * 4), hol, seed=seed + 7))
        front.append(dust(fig, X + 28, GR - 1, 5 + 7 * min(1, t * 4), hol, seed=seed + 8))
    if t > 0.35:
        for i, dx in enumerate((-20, -4, 12, 26)):
            front.append(chunk(fig, X + dx, GR - 1.4, 1.2 + 0.4 * (i % 2), i * 50, max(0.0, 1 - (t - 0.8) / 0.3) if t > 0.8 else 1.0))


def fx_idle(T):
    """La respiration : un caillou se détache sous le cristal du coude et tombe (une fois par souffle sur deux)."""
    def f(fig):
        back, front = [], []
        ph = T % (2 * IDLE)
        t = ph - 0.7
        if 0 <= t < 0.6:
            x0, y0 = 30.0, 150.0
            y = y0 + 300 * t * t
            if y < GR - 1.2:
                front.append(chunk(fig, x0 - 2 * t, y, 1.1, 200 * t))
            else:
                front.append(chunk(fig, x0 - 1.2, GR - 1.0, 1.0, 40, max(0.0, 1 - (t - 0.45) / 0.15)))
                front.append(dust(fig, x0 - 1, GR - 0.5, 1.6, max(0.0, 1 - (t - 0.4) / 0.2)))
        return back, front
    return f


def fx_attack(tl):
    def f(fig):
        back, front = [], []
        # le poing lève de la poussière en quittant le sol, des cailloux en tombent
        if 100 < tl < 800:
            k = env(tl, 100, 250, 450, 800)
            back.append(dust(fig, FIST_F[0] - 26, GR - 1, 3 + 5 * min(1, (tl - 100) / 300), k, seed=3))
        for i, (dx, t0) in enumerate(((-6, 330), (6, 420), (14, 560))):
            t = (tl - t0) / 1000
            if 0 <= t < 0.5:
                P, _ = pose_at(0, 'attack', -tl / 1000)
                fx_, fy_ = P['ff']
                x = K.FW0[0] + fx_ + dx
                y = K.FW0[1] + fy_ + 36 + 280 * t * t
                if y < GR - 1.4:
                    front.append(chunk(fig, x, y, 1.0 + 0.3 * (i % 2), 300 * t))
                else:
                    front.append(chunk(fig, x + 4, GR - 1.0, 1.0, 30, max(0.0, 1 - (t - 0.35) / 0.15)))
        # la traînée du poing qui s'abat
        if 770 <= tl < 880:
            op = env(tl, 770, 790, 830, 880)
            front.append(smear(fig, (K.FW0[0] - 4, GR - 46), 34, -70, 20, 9, op))
        t = (tl - ATTACK_HIT) / 1000
        if t >= 0:
            o = (FIST_F[0] + 2, GR - 4)
            if t < 0.1:
                front.append(flash(fig, o[0] + 4, GR - 4, 34, 1 - t / 0.1))
            if t < 0.6:
                hol = env(t, 0, 0.05, 0.25, 0.6)
                back.append(dust(fig, FIST_F[0] - 44 - 10 * t, GR - 1, 8 + 10 * min(1, t * 5), hol, seed=1))
                front.append(dust(fig, FIST_F[0] + 18 + 16 * t, GR - 1, 8 + 10 * min(1, t * 5), hol, seed=2))
                back.append(crack(fig, FIST_F[0] + 6, ENEMY_X - 30, t / 0.28, seed=2, op=1 - max(0.0, (t - 0.4) / 0.2)))
            if 0.05 < t < 0.5:
                # le sol roule : une vague de poussière court vers les héros
                xw = FIST_F[0] + 40 + (ENEMY_X - 70 - FIST_F[0]) * (t - 0.05) / 0.3
                front.append(dust(fig, min(xw, ENEMY_X - 40), GR - 1, 4 + 3 * min(1, t * 6), env(t, 0.05, 0.12, 0.3, 0.5), seed=9))
            thrown(fig, o, HIT_BITS, t, front)
            eruption(fig, ENEMY_X, tl - ATTACK_HIT - 140, back, front, big=False, seed=0)
        return back, front
    return f


SPARK_SPOTS = [(72.0, 40.0), (86.0, 38.0), (154.0, 42.0), (40.0, 132.0), (184.0, 90.0), (170.0, 132.0), (156.0, 174.0)]
LEVITATE = [(-30, 0.0, 2.6), (-14, 0.1, 1.8), (16, 0.05, 2.2), (34, 0.15, 1.6), (150, 0.08, 2.4), (178, 0.12, 1.8), (198, 0.02, 2.0)]


def fx_special(tl):
    def f(fig):
        back, front = [], []
        t = tl / 1000
        # la charge : étincelles de grenat qui montent en volutes des cristaux, blocs soulevés autour de lui
        if 120 < tl < 960:
            amt = env(tl, 120, 500, 880, 960)
            for i, (sx, sy) in enumerate(SPARK_SPOTS):
                for j in range(3):
                    ph = ((t * 1.6 + j / 3 + i * 0.37) % 1)
                    x = sx + 5 * math.sin(ph * 6.0 + i + j)
                    y = sy - 8 - 34 * ph
                    front.append(spark(fig, x, y, 0.9 + 0.4 * (1 - ph), amt * (1 - ph) * min(1, ph * 5)))
            for i, (ox, lag, size) in enumerate(LEVITATE):
                lift = max(0.0, (t - 0.15 - lag)) * 34
                lift = min(lift, 18 + 4 * (i % 3))
                if lift <= 0 or tl > 940:
                    continue
                x = FIST_N[0] + ox
                y = GR - 2 - lift - 1.6 * math.sin(i + t * 6)
                if i % 3 == 2:
                    front.append(shard(fig, x, y, size + 0.6, 30 * t * (1 if i % 2 else -1) + 20))
                else:
                    (back if i % 2 else front).append(chunk(fig, x, y, size, 60 * t * (1 if i % 2 else -1)))
            if tl > 300:
                back.append(dust(fig, FIST_N[0] - 4, GR - 1, 3 + 4 * amt, amt * 0.8, seed=11))
                back.append(dust(fig, FIST_F[0] - 24, GR - 1, 3 + 4 * amt, amt * 0.8, seed=12))
        # les blocs soulevés retombent au choc
        if 940 <= tl < 1300:
            tt = (tl - 940) / 1000
            for i, (ox, lag, size) in enumerate(LEVITATE):
                y0 = GR - 2 - (18 + 4 * (i % 3))
                y = min(GR - 1.4, y0 + 420 * tt * tt)
                op = 1.0 if y < GR - 1.5 else max(0.0, 1 - (tt - 0.25) / 0.1)
                front.append(chunk(fig, FIST_N[0] + ox, y, size, 40, op) if i % 3 != 2 else shard(fig, FIST_N[0] + ox, y, size + 0.6, 170, op))
        # la traînée des deux poings
        if 890 <= tl < 990:
            op = env(tl, 890, 910, 950, 990)
            front.append(smear(fig, (K.FW0[0] - 4, GR - 50), 38, -70, 20, 10, op))
            front.append(smear(fig, (FIST_N[0] + 10, GR - 54), 42, 250, 160, 10, op))
        ts = (tl - SP_SLAM) / 1000
        if ts >= 0:
            if ts < 0.12:
                front.append(flash(fig, FIST_N[0] + 2, GR - 4, 40, 1 - ts / 0.12))
                front.append(flash(fig, FIST_F[0] + 4, GR - 4, 40, 1 - ts / 0.12))
            if ts < 0.9:
                hol = env(ts, 0, 0.06, 0.4, 0.9)
                r = 10 + 12 * min(1, ts * 4)
                back.append(dust(fig, FIST_N[0] - 30 - 14 * ts, GR - 1, r, hol, seed=21))
                front.append(dust(fig, FIST_N[0] + 30 + 10 * ts, GR - 1, r * 0.8, hol, seed=22))
                front.append(dust(fig, FIST_F[0] + 22 + 16 * ts, GR - 1, r, hol, seed=23))
                back.append(crack(fig, FIST_N[0] - 40, FIST_N[0] + 24, ts / 0.12, seed=3, op=1 - max(0.0, (ts - 0.6) / 0.3)))
                back.append(crack(fig, FIST_F[0] + 6, TARGETS[-1] + 30, ts / 0.35, seed=4, op=1 - max(0.0, (ts - 0.6) / 0.3)))
            thrown(fig, (FIST_F[0] + 2, GR - 6), HIT_BITS[:6], ts, front)
            thrown(fig, (FIST_N[0] + 20, GR - 6), HIT_BITS[3:], ts, front)
            # la vague de pics et de cristaux qui court vers les héros
            WAVE = [(262, 22, 13, 3, 'roche'), (278, 30, 11, 4, 'grenat'), (294, 26, 14, 2, 'roche'), (310, 36, 14, 4, 'roche'),
                    (326, 30, 11, 5, 'grenat')]
            for i, (x, h, w, lean, kind) in enumerate(WAVE):
                tw = ts - 0.04 * i
                if tw <= 0:
                    continue
                grow = min(1.0, tw / 0.08)
                sink = 0.0 if tw < 0.2 else min(1.0, (tw - 0.2) / 0.3)
                (front if i % 2 else back).append(spike(fig, x, h * 0.6 * grow, w * 0.6, lean * 0.6, sink, kind, 1.0, seed=i + 3))
            for j, X in enumerate(TARGETS):
                eruption(fig, X, tl - SP_SLAM - 220 - 40 * j, back, front, big=True, seed=10 * j)
        return back, front
    return f


# ======================================================================== la vidéo

def background(w, h, view, floor_y=GR):
    """Le fond : la pierre sombre et calme des menus (raisin), une dalle de pierre d'un bord à l'autre (comme Kael)."""
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


def shadow_layer(w, h, view, floor_y=GR):
    """L'ombre douce au sol sous lui (présentation seulement)."""
    x0, y0, vw, vh = view
    k = w / vw
    fy = (floor_y - y0) * k
    sh = Image.new('RGBA', (w, h))
    cx = (140 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 112 * k, fy - 4.0 * k, cx + 112 * k, fy + 4.0 * k], fill=(10, 4, 24, 150))
    return sh.filter(ImageFilter.GaussianBlur(2.4 * k))


def timeline():
    """La suite de la vidéo : (action, début, fin) en secondes : repos ×2, attaque ×2, spéciale ×1."""
    seq = [('idle', 2 * IDLE + 0.3), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0), ('attack', ATTACK[-1][0] / 1000),
           ('idle', 1.2), ('special', SPECIAL[-1][0] / 1000), ('idle', 1.6)]
    out, T = [], 0.0
    for a, d in seq:
        out.append((a, T, T + d))
        T += d
    return out, T


def shake_of(act, tl):
    """La secousse au choc (le corps tremble, en pixels du dessin)."""
    if act == 'attack':
        t = tl - ATTACK_HIT
        if 0 <= t < 220:
            return 2.2 * math.sin(t / 22.0) * (1 - t / 220)
    if act == 'special':
        t = tl - SP_SLAM
        if 0 <= t < 380:
            return 3.0 * math.sin(t / 20.0) * (1 - t / 380)
    return 0.0


def frame_svg(T, segs, view=VIEW, ow=0.95):
    act, t0 = None, 0.0
    for a, s, e in segs:
        if s <= T < e:
            if a != 'idle':
                act, t0 = a, s
            break
    P, tl = pose_at(T, act, t0)
    if act == 'attack':
        fx = fx_attack(tl)
    elif act == 'special':
        fx = fx_special(tl)
    else:
        fx = fx_idle(T)
    sx = shake_of(act, tl)
    v = (view[0] - sx, view[1], view[2], view[3])
    return K.build(ow=ow, pose=P, fx=[fx], frame=v).svg(), P


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
        moments = extra or [1.0, a_s + 0.47, a_s + 0.77, a_s + 0.8, a_s + 0.84, a_s + 1.1,
                            s_s + 0.49, s_s + 0.85, s_s + 0.93, s_s + 0.96, s_s + 1.2, s_s + 1.5]
        fr = [frame_svg(T, segs) for T in moments]
        pngs = render([f_[0] for f_ in fr], 640, 360, 'p')
        cols = 3
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        bg = background(640, 360, VIEW)
        bg.alpha_composite(shadow_layer(640, 360, VIEW))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            ImageDraw.Draw(im).text((8, 8), '%.2f s' % moments[i], fill=(255, 255, 255, 255))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        out = os.environ.get('TITAN_PLANCHE', os.path.join(TMP, 'planche.png'))
        sheet_.save(out)
        print('planche :', out)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    fr = [frame_svg(i / FPS, segs) for i in range(n)]
    pngs = render([f_[0] for f_ in fr], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
    bg.alpha_composite(shadow_layer(VW, VH, VIEW))
    for i, p in enumerate(pngs):
        im = bg.copy()
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
