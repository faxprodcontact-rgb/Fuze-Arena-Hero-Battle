# Le léviathan vectoriel ANIMÉ : les mêmes animations que son pixel art (refonte-graphique/pixel/hd/anim/leviathan/
# build.py) — il ondule hors de son trou d'eau, attaque de base « Tentacule des profondeurs », attaque spéciale
# « Raz-de-marée des abysses » (dégâts à TOUS les héros) — dans le style lisse de l'interface.
#
#   python3 refonte-graphique/ui-moderne/monstres/leviathan/anim.py            # → anim.mp4 + anim.gif
#   python3 refonte-graphique/ui-moderne/monstres/leviathan/anim.py --planche  # quelques images clés (contrôle)
#
# Méthode (comme ../../heros/kael/anim.py) : le dessin (leviathan.py) est redessiné à chaque image dans une POSE : la
# vague qui monte le long de la colonne, le souffle, la tête (bloc rigide : tous ses traits ensemble), la mâchoire du bas
# qui tourne autour de sa charnière, les tentacules qui ondulent depuis leur racine (le bout bouge le plus), les
# nageoires qui frémissent, les taches lumineuses qui battent, l'écume qui bouillonne. Poses clés reliées par des
# courbes douces sans dépassement, 24 images par seconde.
#   - attaque : il rugit, le tentacule de droite plonge dans le trou (gerbe), une flaque s'ouvre sous le héros, le MÊME
#     tentacule en jaillit, fouette vers le haut (gerbe et gouttes au coup), replonge, puis ressort du trou ;
#   - spéciale : la colonne sort de l'eau, il se dresse, les taches des abysses flambent, puis il se jette en avant,
#     gueule ouverte : une grande vague part du trou, roule jusqu'aux héros, déferle sur tous (gerbes, écume), reflue.
# Effets dans le même style : dégradés, un seul contour (bleu nuit), aucun flou ; jamais de rayons droits répétés.
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
import leviathan as L  # noqa: E402
import eau  # noqa: E402
from eau import outlined, drop, foam, sheet, mound, column, env, ballistic, WATER, WINK  # noqa: E402
from atelier import sm, ribbon, ellipse, lock  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'leviathan')
TMP = os.environ.get('LEVIATHAN_TMP', os.path.join(HERE, '_images'))
FPS = 24
VIEW = (-6.0, 6.0, 440.0, 247.5)          # la scène (16/9), en pixels du dessin : le boss et les héros en face
VW, VH = 1280, 720
GR = L.GRD
HERO_X = 383.0                            # le premier héros (même écart qu'au combat, comme le pixel art)


# ======================================================================== interpolation douce, sans dépassement
def monotone(ts, vs, t):
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


NUM = ['rise', 'hx', 'hy', 'tilt', 'jaw', 'glow', 'wamp', 'dive', 'tamp', 'tcurl', 'lean']
BASE = dict(rise=0, hx=0, hy=0, tilt=0, jaw=0, glow=0, wamp=0, dive=0, tamp=0, tcurl=0, lean=0)


def keyed(keys, t):
    ts = [k[0] for k in keys]
    fl = [dict(BASE, **k[1]) for k in keys]
    return {n: monotone(ts, [f_[n] for f_ in fl], t) for n in NUM}


# ======================================================================== les actions (poses clés, ms)
# Attaque « Tentacule des profondeurs » : il rugit en se ramassant, le tentacule de droite plonge (dive), ressort sous le
# héros (voir fx_attack), puis revient.
ATTACK = [
    (0, {}),
    (220, dict(hx=-3, hy=-2, tilt=-4, jaw=7, tcurl=0.12, lean=-1.5)),
    (330, dict(hx=-3.4, hy=-2.2, tilt=-4.6, jaw=8, dive=0.3, lean=-1.8)),
    (520, dict(hx=-2, hy=-1, tilt=-2, jaw=6, dive=1.0, lean=-1)),
    (820, dict(hx=2.4, hy=1.6, tilt=3.4, jaw=13, dive=1.0, lean=1.8)),
    (980, dict(hx=3.0, hy=2.0, tilt=4.0, jaw=15, dive=1.0, lean=2.2)),
    (1200, dict(hx=1.6, hy=1.0, tilt=2.0, jaw=7, dive=1.0, lean=1.2)),
    (1320, dict(hx=0.8, hy=0.4, tilt=1.0, jaw=4, dive=0.85, lean=0.6)),
    (1560, dict(dive=0.0, jaw=1)),
    (1760, {}),
]
A_SINK, A_RISE, A_HIT, A_BACK, A_GONE = 330, 600, 900, 1080, 1300

# Spéciale « Raz-de-marée des abysses » : la colonne sort de l'eau, il se dresse (les taches flambent), puis se jette en
# avant : la vague part du trou et roule jusqu'aux héros.
SPECIAL = [
    (0, {}),
    (420, dict(rise=7, hx=-2, hy=-3, tilt=-6, jaw=10, glow=0.8, wamp=1.6, tamp=3.0, tcurl=0.14, lean=-2)),
    (820, dict(rise=9, hx=-2.6, hy=-3.6, tilt=-7.5, jaw=13, glow=1.0, wamp=2.2, tamp=3.6, tcurl=0.18, lean=-2.6)),
    (980, dict(rise=6, hx=4, hy=2, tilt=6, jaw=18, glow=1.0, wamp=1.2, tamp=2.0, tcurl=-0.05, lean=3.2)),
    (1100, dict(rise=5, hx=4.6, hy=2.6, tilt=7, jaw=19, glow=0.9, wamp=1.0, tamp=1.6, lean=3.6)),
    (1600, dict(rise=4, hx=3.6, hy=2.0, tilt=5, jaw=14, glow=0.7, wamp=1.0, tamp=1.2, lean=2.6)),
    (2100, dict(rise=1.5, hx=1, hy=0.6, tilt=1.5, jaw=4, glow=0.3, lean=0.8)),
    (2600, {}),
]
S_LAUNCH, S_CREST, S_CRASH, S_END = 960, 1380, 1520, 2300
WAVE_X0, WAVE_X1 = 214.0, 404.0


# ======================================================================== la respiration (boucle de 2,4 s)
def idle(T):
    u = 2 * math.pi * T / 2.4
    return dict(br=0.5 - 0.5 * math.cos(u), wph=u, wamp=1.5, head=(0.5 * math.sin(u - 0.6), 0.0), tilt=0.8 * math.sin(u - 1.0),
                jaw=1.6 * (0.5 - 0.5 * math.cos(u - 0.4)), tL=(u, 2.0, 0.03 * math.sin(u)), tB=(u + 1.3, 1.8, 0.0),
                tR=(u + 2.4, 2.0, 0.03 * math.sin(u + 1)))


def pose_at(T, action=None, t0=0.0):
    I = idle(T)
    w = 1.0
    act = None
    tl = 0.0
    if action:
        keys = ATTACK if action == 'attack' else SPECIAL
        tl = (T - t0) * 1000
        dur = keys[-1][0]
        act = keyed(keys, tl)
        w = min(1.0, max(0.0, 1 - tl / 260), max(0.0, (tl - (dur - 360)) / 360))
        w = w * w * (3 - 2 * w)
    a = act or dict(BASE)
    k = 0.35 + 0.65 * w                          # les mouvements secondaires ne s'arrêtent jamais tout à fait
    P = dict(br=w * I['br'], wph=I['wph'], wamp=k * I['wamp'] + a['wamp'], rise=a['rise'],
             head=(I['head'][0] * w + a['hx'], I['head'][1] * w + a['hy']), tilt=I['tilt'] * w + a['tilt'],
             jaw=I['jaw'] * w + a['jaw'], glow=a['glow'], gph=T * 3.2 + 4 * a['glow'] * T, fph=T * 2.6 * (1 + a['glow']),
             foam=T * 4.0, dive=a['dive'], lean=a['lean'])
    for key in ('tL', 'tB', 'tR'):
        ph, amp, cu = I[key]
        P[key] = (ph, k * amp + a['tamp'], cu + a['tcurl'])
    P['blink'] = 1.0 if (w > 0.95 and 1.30 <= (T % 4.3) < 1.40) else 0.0
    return P, tl


# ======================================================================== les effets
def at_level(Y, fn, *a, **k):
    """Lance un effet d'eau d'eau.py posé sur une autre ligne d'eau (la surface du trou au lieu du sol)."""
    old = eau.GR
    eau.GR = Y
    try:
        return fn(*a, **k)
    finally:
        eau.GR = old


def puddle(fig, X, r, op=1.0):
    """La flaque qui s'ouvre au sol sous le héros : une eau sombre ovale, bord clair, un reflet."""
    if r < 0.5 or op <= 0.02:
        return ''
    gr = fig.lin(X, GR - 3, X, GR + 3, [(0, L.POOL[2]), (1, L.POOL[0])])
    return outlined([(ellipse(X, GR + 0.4, r, r * 0.17), gr, 1),
                     (ellipse(X + r * 0.25, GR - r * 0.06, r * 0.45, r * 0.04 + 0.3), L.POOL[5], 0.6, 'n')], w=1.2, op=op)


def remote_tentacle(fig, X, e, swing, curl, name='tentX'):
    """Le tentacule de droite qui jaillit de la flaque sous le héros : les MÊMES formes, racine dans la flaque."""
    base = L.TR0
    rx, ry = base[0][0], base[0][1]
    dy = (1 - e) * 80.0
    import math as m_
    a = m_.radians(swing)
    ca, sa = m_.cos(a), m_.sin(a)
    keys = []
    for i, (x, y, w) in enumerate(L.tent_keys(base, (0.0, 0.0, curl))):
        px, py = x - rx, y - ry
        s = i / (len(base) - 1)
        aa = a * (0.4 + 0.6 * s)
        qx = px * m_.cos(aa) - py * m_.sin(aa)
        qy = px * m_.sin(aa) + py * m_.cos(aa)
        keys.append((X - 18 + qx, GR + 4 + qy + dy, w))
    t = L.tentacle(fig, name, keys, L.TENT, GR + 0.2, suckers=1, side=1, cast=1.0)
    L.boil_part(fig, name + 'b', X - 16.0, GR + 1.0, 13.0, 7.0, e * 9, seed=5, cast=0.4)
    return t


def fx_attack(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        # la gerbe dans le trou quand il plonge, puis quand il ressort
        for t0, big in ((A_SINK, 0.9), (A_GONE + 60, 0.7)):
            k = (tl - t0) / 520.0
            if 0 < k < 1:
                b_, f_ = at_level(L.TCUT['R'] + 1.0, eau.splash_crown, fig, 196.0, k, big=big, seed=2)
                back.extend(b_)
                front.extend(f_)
        # la flaque sous le héros
        op = env(tl, A_SINK + 80, A_RISE, A_BACK + 120, A_GONE + 120)
        back.append(puddle(fig, HERO_X - 16, 26 * op, op=min(1, op * 1.6)))
        # le tentacule jaillit, fouette, replonge
        if A_RISE - 80 < tl < A_GONE + 40:
            if tl < A_HIT:
                e = min(1.0, max(0.0, (tl - (A_RISE - 80)) / 240.0))
                e = 1 - (1 - e) ** 3
                sw = -14 * min(1, max(0, (tl - A_RISE) / 200))
                cu = 0.1
            elif tl < A_BACK:
                u = (tl - A_HIT) / (A_BACK - A_HIT)
                e = 1.0
                sw = -14 + 30 * math.sin(math.pi * 0.5 * min(1, u * 1.6))
                cu = 0.1 + 0.6 * math.sin(math.pi * min(1, u))
            else:
                u = (tl - A_BACK) / (A_GONE + 40 - A_BACK)
                e = 1 - u * u
                sw = 16 * (1 - u)
                cu = 0.1
            remote_tentacle(fig, HERO_X, e, sw, cu)
        # au coup : la gerbe sous le héros, des gouttes qui retombent
        for t0, big, X in ((A_RISE - 60, 0.8, HERO_X - 16), (A_HIT + 40, 1.1, HERO_X - 4), (A_GONE - 160, 0.6, HERO_X - 16)):
            k = (tl - t0) / 560.0
            if 0 < k < 1:
                b_, f_ = eau.splash_crown(fig, X, k, big=big, seed=int(t0) % 7)
                back.extend(b_)
                front.extend(f_)
        k = (tl - (A_HIT + 40)) / 700.0
        if 0 < k < 1:
            for j, (vx, vy) in enumerate(((-70, -150), (60, -170), (-120, -100), (110, -120), (10, -200), (150, -70))):
                x, y = ballistic((HERO_X + 4, GR - 40), (vx, vy), 330, k * 0.9)
                if y < GR:
                    front.append(drop(fig, x, y, vx, vy + 330 * k, 1.3 if j % 2 else 1.0, op=min(1, 3 * (1 - k))))
            # la nappe d'eau arrachée par le coup (une courbe, pas des rayons)
            if k < 0.5:
                front.append(eau.stream(fig, [(HERO_X - 26, GR - 30 - 30 * k), (HERO_X - 6, GR - 52 - 20 * k), (HERO_X + 14, GR - 48 - 10 * k),
                                              (HERO_X + 26, GR - 34)], 1.0, 3.2, op=1 - 2 * k))
    return f


def wave(fig, xf, h, curl, op=1.0, t=0.0):
    """La grande vague qui roule vers les héros : dos en pente douce, crête qui s'enroule vers l'avant (lèvre d'écume),
    face creuse plus claire, pied posé au sol. Un seul contour (bleu nuit), dégradés, aucun flou."""
    if h < 2 or op <= 0.02:
        return ''
    G0 = GR + 0.4
    Lb = 70 + 1.3 * h
    xb = xf - Lb
    w1 = 0.6 * math.sin(t * 9)
    pts = [(xb, G0), (xb + 0.3 * Lb, G0 - 0.28 * h), (xb + 0.62 * Lb, G0 - 0.7 * h + w1), (xf - 0.12 * Lb, G0 - 0.98 * h),
           (xf + 0.1 * h, G0 - 1.04 * h), (xf + 0.38 * h * curl, G0 - 0.9 * h), (xf + 0.5 * h * curl, G0 - 0.66 * h),
           (xf + 0.3 * h * curl, G0 - 0.7 * h), (xf + 0.06 * h, G0 - 0.66 * h), (xf - 0.04 * h, G0 - 0.34 * h), (xf + 0.12 * h, G0)]
    body = sm(pts, sharp=(0, 6, len(pts) - 1), t=0.9)
    gr = fig.lin(xf, G0 - h, xb + 0.4 * Lb, G0, [(0, WATER[2]), (0.35, WATER[3]), (0.8, WATER[4]), (1, WATER[5])])
    # la face creuse sous la lèvre (plus claire : la lumière la traverse)
    face = sm([(xf - 0.02 * h, G0 - 0.86 * h), (xf + 0.1 * h * curl, G0 - 0.74 * h), (xf + 0.02 * h, G0 - 0.6 * h),
               (xf - 0.05 * h, G0 - 0.3 * h), (xf + 0.08 * h, G0 - 0.04 * h), (xf - 0.2 * h, G0 - 0.4 * h)], t=0.9)
    gf = fig.lin(xf, G0 - h, xf, G0, [(0, WATER[1]), (1, WATER[3])])
    # l'écume de la crête : une langue blanche le long du haut, jusqu'au bout de la lèvre
    crest = lock((xb + 0.5 * Lb, G0 - 0.58 * h), (xf - 0.3 * Lb, G0 - 0.95 * h), (xf, G0 - 1.04 * h),
                 (xf + 0.48 * h * curl, G0 - 0.7 * h), 0.16 * h, n=14, bulge=0.25)
    glint = ribbon([(xb + 0.2 * Lb, G0 - 0.12 * h), (xb + 0.45 * Lb, G0 - 0.42 * h), (xb + 0.66 * Lb, G0 - 0.68 * h)],
                   [0.2, max(0.6, 0.05 * h), 0.2])
    out = outlined([(body, gr, 1), (face, gf, 0.75, 'n'), (crest, '#ffffff', 0.95, 'n'), (glint, WATER[1], 0.55, 'n')], w=1.6, op=op)
    for j in range(4):
        out += foam(fig, xf - 0.1 * Lb + j * 0.09 * h * curl, G0 - 1.0 * h + j * 0.06 * h + 0.6 * math.sin(t * 8 + j),
                    0.08 * h * (1 - 0.15 * j), op=op, seed=j)
    return out


def fx_special(tl):
    def f(fig, ctx):
        back, front = fig.fx_back, fig.fx_front
        P = ctx['P']
        # pendant la charge : le trou bouillonne (bosses d'écume qui montent), quelques gouttes
        ch = env(tl, 150, 600, 900, 1100)
        if ch > 0:
            for j, X in enumerate((150.0, 172.0, 66.0)):
                front.append(at_level(226.0, mound, fig, X, (3 + 2 * math.sin(tl / 70 + j)) * ch, 9, op=ch))
            for j in range(5):
                k = ((tl / 520.0) + j * 0.21) % 1.0
                x, y = ballistic((80 + 25 * j, 214), ((-1) ** j * 30, -90 - 12 * j), 300, k * 0.6)
                front.append(drop(fig, x, y, (-1) ** j * 30, -90 + 300 * k * 0.6, 0.9, op=ch * (1 - k)))
        # la vague : elle part du trou, grandit en roulant, s'enroule puis déferle sur les héros
        if S_LAUNCH <= tl < S_CRASH + 120:
            u = (tl - S_LAUNCH) / (S_CRASH + 120 - S_LAUNCH)
            xf = WAVE_X0 + (WAVE_X1 - WAVE_X0) * (1 - (1 - u) ** 1.6)
            h = 80 * math.sin(math.pi * 0.5 * min(1, u * 1.25)) * (1 - 0.6 * max(0, (u - 0.8) / 0.2))
            curl = 0.5 + 0.9 * u
            op = 1.0 if u < 0.88 else max(0, 1 - (u - 0.88) / 0.12)
            front.append(wave(fig, xf, h, curl, op=op, t=tl / 1000))
            # l'eau qui file au sol derrière la vague (le trou se vide vers les héros)
            front.append(eau.stream(fig, [(190.0, GR - 4), (xf - 120, GR - 2), (xf - 70 - 0.6 * h, GR - 1)], 2.0, 5.0, op=min(1, 2 * (1 - u))))
        # la déferlante sur tous les héros : trois grandes gerbes, de l'écume, des gouttes
        for j, (X, d) in enumerate(((HERO_X - 40, 0), (HERO_X + 4, 60), (HERO_X + 44, 120))):
            k = (tl - S_CRASH - d) / 780.0
            if 0 < k < 1:
                rise_ = math.sin(math.pi * min(1, k * 1.3))
                top = GR - 56 * rise_ * (1.0 if j == 1 else 0.75)
                front.append(column(fig, X, top, 20, 9, (-1) ** j * 4 * k, tl / 1000, op=min(1, 3 * (1 - k))))
                b_, f_ = eau.splash_crown(fig, X, k, big=1.3, seed=j)
                back.extend(b_)
                front.extend(f_)
        k = (tl - S_CRASH) / 900.0
        if 0 < k < 1:
            for j in range(9):
                vx, vy = -110 + 30 * j, -170 + 25 * (j % 3)
                x, y = ballistic((HERO_X - 30 + 8 * j, GR - 60), (vx, vy), 330, k * 0.85)
                if y < GR:
                    front.append(drop(fig, x, y, vx, vy + 330 * k, 1.4 if j % 2 else 1.1, op=min(1, 3 * (1 - k))))
        # le reflux : une nappe basse qui revient vers le trou
        rf = env(tl, S_CRASH + 300, S_CRASH + 500, S_CRASH + 650, S_END)
        if rf > 0:
            front.append(mound(fig, HERO_X - 60 * (1 - rf), 6 * rf, 60, op=rf, foamy=0.8))
    return f


# ======================================================================== la scène
def background(w, h, view, floor_y=GR):
    x0, y0, vw, vh = view
    k = w / vw
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    fy = int((floor_y - y0) * k)
    for y in range(h):
        if y < fy:
            t = y / max(1, fy)
            c = tuple(int(a + (b - a) * t) for a, b in zip((44, 30, 74), (30, 20, 52)))
        else:
            tt = (y - fy) / max(1, h - fy)
            c = tuple(int(a + (b - a) * tt) for a, b in zip((70, 56, 98), (38, 28, 60)))
        d.line([(0, y), (w, y)], fill=c + (255,))
    d.rectangle([0, fy - 1, w, fy + 2], fill=(98, 82, 132, 255))
    glow = Image.new('RGBA', (w, h))
    ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.7], fill=(120, 90, 170, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.12)))
    sh = Image.new('RGBA', (w, h))
    cx = (126 - x0) * k
    ImageDraw.Draw(sh).ellipse([cx - 124 * k, fy - 5 * k, cx + 124 * k, fy + 5 * k], fill=(10, 4, 24, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * k)))
    return im


def timeline():
    seq = [('idle', 4.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 0.8), ('attack', ATTACK[-1][0] / 1000), ('idle', 1.0),
           ('special', SPECIAL[-1][0] / 1000), ('idle', 1.4)]
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
    return L.build(ow=ow, pose=P, fx=fx, frame=view).svg()


def render(frames_svg, w, h, prefix):
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
        moments = [0.6, 1.8, a_s + 0.25, a_s + 0.45, a_s + 0.7, a_s + 0.92, a_s + 1.0, a_s + 1.2,
                   s_s + 0.8, s_s + 1.1, s_s + 1.3, s_s + 1.45, s_s + 1.6, s_s + 1.9, s_s + 2.2, s_s + 2.5]
        pngs = render([frame_svg(T, segs) for T in moments], 640, 360, 'p')
        bg = background(640, 360, VIEW)
        cols = 4
        sheet_ = Image.new('RGB', (640 * cols, 360 * ((len(pngs) + cols - 1) // cols)))
        for i, p in enumerate(pngs):
            im = bg.copy()
            im.alpha_composite(Image.open(p))
            sheet_.paste(im.convert('RGB'), ((i % cols) * 640, (i // cols) * 360))
        dst = os.path.join(os.environ.get('LEVIATHAN_PLANCHE', TMP), 'planche.png')
        sheet_.save(dst)
        print('planche :', dst)
        return
    n = int(round(total * FPS))
    print('images :', n, '(%.1f s)' % total)
    pngs = render([frame_svg(i / FPS, segs) for i in range(n)], VW, VH, 'a')
    bg = background(VW, VH, VIEW)
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
