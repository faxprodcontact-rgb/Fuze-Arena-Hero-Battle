# Lenore (knights-9, feu, épique, guerrier) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte
# de tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/lenore/lenore.py      # → lenore.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/lenore.txt) : l'oni rouge, une brute sûre de sa force.
# Trois quarts vers la droite, garde moyenne, pieds nus à plat, genoux un peu fléchis. Bras proche (droit) qui pend, le
# poing serré sur le manche du kanabō tenu bas le long de la jambe (pommeau, poing, manche et tête de fer sur UNE ligne
# droite) ; bras lointain qui pend derrière le flanc, poing serré. Grosse tête : deux cornes d'ivoire (la proche plus
# grosse), crinière noir-bleuté en grosses mèches couchées vers l'arrière, sourcils froncés en V, yeux jaunes à petite
# pupille, gros nez, gueule ouverte en rictus (dents, crocs, deux défenses d'ivoire), oreille pointue à l'anneau d'or.
# Collier de grosses perles d'ivoire, bracelets d'or, pagne en peau de tigre, corde torsadée nouée côté lointain.
#
# Coordonnées = pixels du dessin pixel art (même toile : le pixel (x, y) couvre [x, x+1] × [y, y+1], le point « sol »
# (64, 116) est le même), pour se poser au même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul
# contour (atelier.py) ; les membres sont d'un seul tenant (épaule → coude → poignet, hanche → genou → cheville → pied) :
# aucune jointure visible.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import (Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp,  # noqa: E402
                     resample)
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-9'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffa860', '#ee6236', '#c93c2e', '#8c2236', '#561232')
MANE = Mat('#9a8cc8', '#62578a', '#3c3158', '#251c3e', '#150f26')
IVORY = Mat('#fffcee', '#f6ead0', '#e2cfac', '#a88c7e', '#5e4248')
GOLD = Mat('#fff4b4', '#f8c640', '#d8961e', '#8e5216', '#5a2c0e', glint='#ffffff')
IRON = Mat('#dce2f6', '#8690b0', '#575e80', '#33374f', '#1d1b2e', glint='#ffffff')
TIGER = Mat('#ffd885', '#f4a83c', '#d88026', '#9a4a18', '#5a2a12')
ROPE = Mat('#fff2c0', '#ecd08c', '#bc904c', '#70482a', '#42281a')
STRIPE = '#3a1418'
GORGE = '#3e0a1c'
GUMS = '#86203a'
EYE_Y, EYE_K, PUPIL = '#ffe24c', '#c8801a', '#1a0810'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (11.0, 4.0, 98.0, 115.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse (les genoux plient, pieds au sol) ; lean : il se penche en avant (+) ;
#   head : décalage de la tête ; tilt : la tête tourne ; jaw : la gueule s'ouvre (0..3) ; ph : phase des mèches ;
#   ml / mu : retard des mèches basses / des pointes hautes ; pg : le pagne se balance ; blink : yeux fermés ;
#   G : le point du manche serré au milieu du poing ; ang : la direction poing → tête de fer ; bend : sens du coude ;
#   wr : le poignet dans le repère de la massue ; length : la massue raccourcie (vue de face, en plein élan) ;
#   shs : l'épaule proche avancée ; rn / rf : épaules soulevées ; far / far_rot : le bras lointain ;
#   lift / shift : tout le corps en l'air / avancé ; glow : la peau s'embrase (0..2) ; hot : le fer chauffe (0..2).
G0 = (44.4, 88.4)
ANG0 = 139.5                              # la massue descend vers l'arrière (pente -0,78 du pixel art)
WR0 = (-5.0, 5.0)
S0 = (49.0, 61.4)                         # l'épaule proche (articulation)
L1, L2 = 13.6, 10.6                       # bras, avant-bras (jusqu'au poignet)
R_FS = 5.8                                # le rayon de la boule de l'épaule lointaine
R_SH = 7.4                                # le rayon de la boule de l'épaule proche (bras et buste la partagent)
FS0 = (93.0, 61.4)                        # l'épaule lointaine
HIP = (72.0, 89.0)                        # le pivot du buste
NECK = (82.0, 55.0)                       # le pivot (et le centre d'agrandissement) de la tête
HINGE = (69.0, 47.0)                      # la charnière de la mâchoire

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, ph=0.0, ml=0.0, mu=0.0, pg=0.0,
            blink=0.0, G=G0, ang=ANG0, bend=1.0, wr=WR0, length=1.0, shs=(0.0, 0.0), rn=0.0, rf=0.0, far=(0.0, 0.0),
            far_rot=0.0, lift=0.0, shift=0.0, glow=0.0, hot=0.0, tuck=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def matmix(m, hot, t):
    if t <= 0:
        return m
    return Mat(*(hexmix(getattr(m, k), getattr(hot, k), min(1, t)) for k in ('hi', 'light', 'base', 'shadow', 'deep')),
               glint=m.glint)


SKIN_HOT = Mat('#fff0a8', '#ffa040', '#f05a26', '#b8302a', '#78182a')
IRON_HOT = Mat('#fff6c8', '#ffb43a', '#f2701a', '#b8301a', '#6a1410', glint='#fffbe4')


# ---------- formes : un membre d'un seul tenant, épaisseurs différentes de chaque côté ----------

def _seg_x(p, q, r, s):
    """Le point où les segments [p q] et [r s] se croisent, sinon None."""
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-9:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if 0 < t < 1 and 0 < u < 1:
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    return None


def unloop(pts, win=14):
    """Retire les petites boucles d'un bord (l'intérieur d'un coude plié) : le bord passe par le croisement."""
    out = list(pts)
    i = 0
    while i < len(out) - 3:
        hit = None
        for j in range(min(len(out) - 2, i + win), i + 1, -1):
            ip = _seg_x(out[i], out[i + 1], out[j], out[j + 1])
            if ip:
                hit = (j, ip)
                break
        if hit:
            j, ip = hit
            out = out[:i + 1] + [ip] + out[j + 1:]
        i += 1
    return out


def stations(center, keys, n):
    """La ligne du membre rééchantillonnée en n+1 points, et les demi-épaisseurs (dos, devant) en chaque point.
    keys : [(t, dos, devant)…], t = la fraction de longueur (0 = départ, 1 = bout)."""
    c = resample(center, n)
    ws = []
    for i in range(n + 1):
        t = i / n
        for k in range(len(keys) - 1):
            if keys[k][0] <= t <= keys[k + 1][0]:
                u = (t - keys[k][0]) / ((keys[k + 1][0] - keys[k][0]) or 1)
                u = u * u * (3 - 2 * u)
                ws.append((keys[k][1] + (keys[k + 1][1] - keys[k][1]) * u, keys[k][2] + (keys[k + 1][2] - keys[k][2]) * u))
                break
        else:
            ws.append(keys[-1][1:] if t > keys[-1][0] else keys[0][1:])
    return c, ws


def edges(c, ws):
    """Les deux bords : « dos » (à gauche quand le membre descend) et « devant »."""
    n = len(c)
    back, front = [], []
    for i, p in enumerate(c):
        a = c[max(0, i - 1)]
        b = c[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        back.append((p[0] + nx * ws[i][0], p[1] + ny * ws[i][0]))
        front.append((p[0] - nx * ws[i][1], p[1] - ny * ws[i][1]))
    return unloop(back), unloop(front)


def cap(ctr, frm, to, r, k=3):
    """Un bout arrondi : un arc autour de ctr, du point frm au point to (par le côté extérieur)."""
    a0 = math.atan2(frm[1] - ctr[1], frm[0] - ctr[0])
    a1 = math.atan2(to[1] - ctr[1], to[0] - ctr[0])
    da = (a1 - a0) % (2 * math.pi)
    if da > math.pi:
        da -= 2 * math.pi
    return [(ctr[0] + r * math.cos(a0 + da * j / (k + 1)), ctr[1] + r * math.sin(a0 + da * j / (k + 1))) for j in range(1, k + 1)]


def ball_arc(ctr, r, a_from, a_to, step=12):
    """Les points d'un arc de cercle (angles en degrés, de a_from à a_to, dans un sens ou dans l'autre)."""
    k = max(2, int(abs(a_to - a_from) / step))
    return [(ctr[0] + r * math.cos(math.radians(a_from + (a_to - a_from) * j / k)),
             ctr[1] + r * math.sin(math.radians(a_from + (a_to - a_from) * j / k))) for j in range(k + 1)]


def body_limb(center, keys, n=24, end_cap=True, round_start=False):
    """Un membre d'un seul tenant le long d'une ligne brisée (épaule, coude, poignet), bouts arrondis.
    round_start : le départ est une vraie boule (l'épaule, centrée sur l'articulation) : elle reste la même quand le bras
    tourne, et le buste porte la même boule (le raccord épaule / buste est ainsi continu, sans marche)."""
    c, ws = stations(center, keys, n)
    back, front = edges(c, ws)
    if round_start:
        r0 = (ws[0][0] + ws[0][1]) / 2
        a_f = math.degrees(math.atan2(front[0][1] - c[0][1], front[0][0] - c[0][0]))
        a_b = math.degrees(math.atan2(back[0][1] - c[0][1], back[0][0] - c[0][0]))
        a_up = math.degrees(math.atan2(c[0][1] - c[1][1], c[0][0] - c[1][0]))     # à l'opposé du membre
        # du bord « devant » au bord « dos » en passant par l'opposé du membre
        while a_b > a_f:
            a_b -= 360
        if not (a_b <= a_up <= a_f or a_b <= a_up - 360 <= a_f or a_b <= a_up + 360 <= a_f):
            a_b += 360
        d = (c[-1][0] - c[-2][0], c[-1][1] - c[-2][1])
        L = math.hypot(*d) or 1
        tip = (c[-1][0] + d[0] / L * (ws[-1][0] + ws[-1][1]) / 2, c[-1][1] + d[1] / L * (ws[-1][0] + ws[-1][1]) / 2)
        end = [lerp(back[-1], tip, 0.55), tip, lerp(front[-1], tip, 0.55)] if end_cap else []
        arc = ball_arc(c[0], r0, a_f, a_b)[1:-1]
        return sm(back + end + front[::-1] + arc, t=0.9)
    # le bout : un arc qui va du bord « dos » au bord « devant » en passant par l'avant du membre
    d = (c[-1][0] - c[-2][0], c[-1][1] - c[-2][1])
    L = math.hypot(*d) or 1
    tip = (c[-1][0] + d[0] / L * (ws[-1][0] + ws[-1][1]) / 2, c[-1][1] + d[1] / L * (ws[-1][0] + ws[-1][1]) / 2)
    end = [lerp(back[-1], tip, 0.55), tip, lerp(front[-1], tip, 0.55)] if end_cap else []
    d0 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    L0 = math.hypot(*d0) or 1
    r0 = (ws[0][0] + ws[0][1]) / 2
    top = (c[0][0] - d0[0] / L0 * r0, c[0][1] - d0[1] / L0 * r0)
    start = [lerp(front[0], top, 0.6), top, lerp(back[0], top, 0.6)]
    return sm(back + end + front[::-1] + start, t=0.9)


def ik(S, W, L1_, L2_, bend):
    d = math.dist(S, W)
    dd = max(abs(L1_ - L2_) + 0.01, min(L1_ + L2_ - 0.01, d))
    al = math.acos(max(-1, min(1, (L1_ * L1_ + dd * dd - L2_ * L2_) / (2 * L1_ * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * al
    E = (S[0] + L1_ * math.cos(th), S[1] + L1_ * math.sin(th))
    if d > L1_ + L2_:                       # trop loin : le bras est tendu, le poignet suit la direction
        W = (S[0] + (W[0] - S[0]) / d * (L1_ + L2_), S[1] + (W[1] - S[1]) / d * (L1_ + L2_))
    return E, W


class Seg:
    """Le repère d'un segment de membre : a le long (0 → longueur), b en travers (+ = côté « devant »)."""

    def __init__(self, p, q):
        self.p = p
        self.L = math.dist(p, q) or 1
        self.u = ((q[0] - p[0]) / self.L, (q[1] - p[1]) / self.L)
        self.v = (self.u[1], -self.u[0])          # « devant » (à droite quand le membre descend)

    def __call__(self, a, b=0.0):
        return (self.p[0] + self.u[0] * a + self.v[0] * b, self.p[1] + self.u[1] * a + self.v[1] * b)

    def at(self, t, b=0.0):
        return self(t * self.L, b)


def sm_under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche : la mèche moins elle-même décalée vers le haut (le haut reste éclairé)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    glow, hot = P['glow'], P['hot']
    skin = matmix(SKIN, SKIN_HOT, 0.42 * glow)
    iron = matmix(IRON, IRON_HOT, 0.5 * hot)

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(P['shift'], -P['lift'])
    dyb = P['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(P['lean'] * 0.35, 0), mR(P['lean'] * 1.1, *HIP))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.6 * br))                                           # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 72, 84))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    FARM = mchain(UC, mT(P['far'][0], P['far'][1] - 0.8 * P['rf']), mR(P['far_rot'], *FS0))
    CLO = mchain(PEL, mskx(-0.05 * P['pg'], 84))

    # ======================================================================== la crinière (derrière tout)
    ph = P['ph']
    ml, mu = P['ml'], P['mu']
    # (nom, racine, c1, c2, pointe, largeur) ; de la plus basse (la nuque) à la plus haute ; les racines passent
    # sous la tête. Chaque mèche ondule un peu (la vague court vers la pointe) et traîne en retard (ml, mu).
    LOCKS = [
        ('m4', (66.5, 47.6), (62.6, 47.4), (58.8, 49.2), (55.4, 53.2), 7.2),
        ('m3', (66.0, 40.6), (59.6, 38.0), (50.6, 40.4), (43.8, 49.8), 12.6),
        ('m2', (68.6, 30.4), (61.4, 26.8), (51.6, 27.6), (43.6, 32.8), 10.2),
        ('m1', (70.6, 22.8), (65.4, 19.0), (59.2, 17.4), (52.6, 18.0), 7.6),
        ('tA', (78.0, 27.6), (76.4, 24.4), (73.8, 21.2), (70.4, 17.8), 5.8),
        ('tB', (83.4, 28.0), (83.0, 24.4), (82.2, 21.4), (81.0, 17.6), 5.2),
    ]
    for i, (name, p0, p1, p2, p3, w0) in enumerate(LOCKS):
        k = (0.5 + 0.14 * i) if i < 4 else 0.45
        w = ph - 0.8 * i
        lag = ml if i < 2 else mu
        p2 = (p2[0] + 0.4 * k * math.sin(2 * w + 1.0), p2[1] + 0.6 * k * math.sin(w) + 0.5 * lag)
        p3 = (p3[0] + 0.8 * k * math.sin(w + 0.8) - 0.3 * lag, p3[1] + 0.9 * k * math.cos(w) + 1.1 * lag)
        sh = lock(p0, p1, p2, p3, w0, n=12, bulge=0.28)
        x0_, y0_, x1_, y1_ = sh.bbox()
        fig.part(name, sh, MANE, grad=(x1_, y0_, x0_ + (x1_ - x0_) * 0.35, y1_, [(0, '#6a5e94'), (0.45, MANE.base), (1, MANE.shadow)]),
                 cel=0, rim=0.75, cast=1.3, cast_on=[q[0] for q in LOCKS[:i]],
                 details=[(sm_under(sh), ('lin', 0, y0_, 0, y1_, [(0, MANE.shadow), (1, MANE.deep)]), 0.85),
                          (lock(lerp(p0, p1, 0.3), lerp(p1, p2, 0.3), lerp(p2, p3, 0.2), lerp(p2, p3, 0.75), w0 * 0.22, n=8, bulge=0.1)
                           .move(0.3 + 0.03 * w0, -0.12 * w0), MANE.light, 0.55)])

    # ======================================================================== le bras lointain (gauche), derrière le flanc
    FE, FW = (94.4, 71.2), (94.9, 79.4)
    farm = body_limb([FS0, FE, FW], [(0, R_FS, R_FS), (0.25, 5.2, 5.3), (0.52, 4.4, 4.6), (0.7, 4.8, 4.9), (1, 4.0, 4.1)], n=20,
                     round_start=True)
    s1 = Seg(FS0, FE)
    fig.part('farm', farm, skin, cel=1.6, rim=0.6, cast=0,
             details=[(ellipse(*s1.at(0.55, 1.6), 1.8, 3.4, math.degrees(math.atan2(s1.u[1], s1.u[0])) - 90), skin.light, 0.45),
                      (ribbon([s1.at(0.15, -1.0), s1.at(0.36, 0.6), s1.at(0.42, 3.2)], [0.1, 0.8, 0.1]), skin.shadow, 0.6)])
    ffist = sm([(91.2, 81.0), (95.4, 80.2), (98.6, 81.2), (99.4, 85.0), (99.0, 89.6), (97.0, 92.9), (93.6, 93.3), (91.2, 90.8), (90.6, 85.6)])
    fd = [(sm([(94.6, 81.4), (98.4, 81.6), (99.0, 85), (98.6, 89.4), (96.8, 92.2), (95.6, 88), (95.0, 84)]), skin.light, 0.5)]
    for yy in (84.8, 87.4, 89.9):
        fd.append((ribbon([(96.0, yy - 0.1), (97.6, yy + 0.15), (99.0, yy - 0.2)], [0.1, 0.55, 0.1]), skin.deep, 0.45))
    for yy in (83.4, 86.1, 88.7):
        fd.append((ellipse(98.0, yy, 0.8, 0.5, -10), skin.hi, 0.45))
    fig.part('ffist', ffist, skin, cel=1.3, rim=0.6, cast=0.8, details=fd)
    fbr = rpoly([(90.0, 78.2), (99.8, 78.0), (100.0, 81.4), (90.2, 81.6)], 1.2)
    fig.part('fbrac', fbr, GOLD, cel=0.7, rim=0.6, cast=0.7,
             details=[(ribbon([(91.4, 78.9), (95, 78.7), (98.8, 78.8)], [0.1, 0.6, 0.1]), GOLD.hi, 0.9),
                      (ellipse(97.2, 79.2, 1.0, 0.4), GOLD.glint, 0.9)])

    # ======================================================================== les jambes : hanche → genou → cheville → pied,
    # d'un seul tenant (aucune couture au genou ni à la cheville) ; les pieds restent à plat au sol
    def foot(dx):
        """Le pied nu (talon à gauche, orteils vers l'ennemi) : son contour, et les orteils (plis, ongles d'ivoire en
        griffes courtes)."""
        P_ = lambda pts: [(x + dx, y) for x, y in pts]
        out = P_([(43.6, 110.6), (41.0, 112.4), (40.6, 115.0), (41.4, 116.4), (59.6, 116.4), (62.4, 116.2), (63.0, 114.4),
                  (62.2, 112.6), (60.6, 112.2), (59.4, 111.5), (57.6, 111.7), (56.2, 111.0), (53.2, 110.2)])
        toes = [(ribbon(P_([(60.5, 112.4), (60.9, 113.6), (60.7, 114.8)]), [0.1, 0.6, 0.1]), SKIN.deep, 0.6),
                (ribbon(P_([(57.7, 111.9), (58.1, 113.0), (57.9, 113.8)]), [0.1, 0.5, 0.1]), SKIN.deep, 0.5),
                (sm(P_([(61.3, 112.9), (62.5, 113.1), (63.1, 114.4), (62.6, 115.4), (61.7, 114.8)]), sharp=(3,)), IVORY.base, 1),
                (ellipse(62.3 + dx, 113.6, 0.45, 0.32, 20), IVORY.hi, 1),
                (sm(P_([(58.6, 112.2), (59.6, 111.9), (60.3, 112.5), (60.0, 113.4)]), sharp=(3,)), IVORY.base, 0.95),
                (sm(P_([(56.0, 111.5), (56.9, 111.3), (57.5, 111.9), (57.2, 112.7)]), sharp=(3,)), IVORY.shadow, 0.95),
                (ribbon(P_([(53.0, 111.0), (57.0, 111.9), (60.6, 113.0)]), [0.1, 0.7, 0.1]), SKIN.hi, 0.45),
                (ribbon(P_([(42.0, 114.4), (50.0, 115.0), (60.0, 115.0)]), [0.1, 0.9, 0.1]), SKIN.deep, 0.35)]
        return out, toes

    def leg(name, Hr, A, L1_, L2_, bend, keys, dx, cast_on):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, A)
        fo, toes = foot(dx)
        fo = [mapp(ROOTM, p) for p in fo]
        toes = [(sh.map(lambda q: mapp(ROOTM, q)), c_, o_) for sh, c_, o_ in toes]
        tk = P['tuck']
        if tk:                                  # en l'air : les pieds remontent un peu sous lui (genoux pliés)
            A = (A[0] - 0.4 * tk, A[1] - tk)
            fo = [(x - 0.4 * tk, y - tk) for x, y in fo]
            toes = [(sh.move(-0.4 * tk, -tk), c_, o_) for sh, c_, o_ in toes]
        # quand il se tasse, le genou part vers l'avant (vers nous, trois quarts) : à l'écran la jambe se raccourcit
        # au lieu de plier en grenouille ; elle garde toujours un léger pli
        sc = min(1.0, math.dist(H, A) * 1.06 / (L1_ + L2_))
        K, A2 = ik(H, A, L1_ * sc, L2_ * sc, bend)
        if math.dist(A2, A) > 0.01:             # jambe trop tendue : le pied suit la cheville (il pend)
            dA = (A2[0] - A[0], A2[1] - A[1])
            A = A2
            fo = [(x + dA[0], y + dA[1]) for x, y in fo]
            toes = [(sh.move(*dA), c_, o_) for sh, c_, o_ in toes]
        c, ws = stations([H, K, A], keys, 22)
        back, front = edges(c, ws)
        r0 = (ws[0][0] + ws[0][1]) / 2
        d0 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
        L0 = math.hypot(*d0) or 1
        top = (c[0][0] - d0[0] / L0 * r0, c[0][1] - d0[1] / L0 * r0)
        pts = back + fo + front[::-1] + [lerp(front[0], top, 0.6), top, lerp(back[0], top, 0.6)]
        nb = len(back)
        sh = sm(pts, sharp=(nb + 3, nb + 5), t=0.85)
        th = Seg(H, K)
        sn = Seg(K, A)
        ta, sa = math.degrees(math.atan2(th.u[1], th.u[0])), math.degrees(math.atan2(sn.u[1], sn.u[0]))
        det = []
        # la cuisse : le muscle de devant éclairé ; la rotule (un relief doux) ; le tibia éclairé ; le pli du jarret
        det += [(ellipse(*th.at(0.55, 2.2), 2.6, 4.8, ta - 90), skin.light, 0.45),
                (ellipse(*sn.at(0.04, 2.4), 1.6, 2.6, sa - 90), skin.light, 0.5),
                (ellipse(*sn.at(0.0, 3.0), 0.6, 1.1, sa - 90), skin.hi, 0.45),
                (ribbon([sn.at(0.2, 3.0), sn.at(0.6, 3.2), sn.at(0.95, 2.4)], [0.1, 1.0, 0.1]), skin.light, 0.55),
                (ribbon([th.at(0.9, -2.6), sn.at(0.1, -1.6), sn.at(0.28, -2.6)], [0.1, 0.6, 0.1]), skin.deep, 0.4)]
        det += toes
        fig.part(name, sh, skin, cel=1.7, rim=0.6, cast=1.0, cast_on=cast_on, details=det)
        return K

    # les deux genoux plient vers l'avant (vers l'ennemi, à droite) : bend = -1 pour les deux jambes
    leg('fleg', (85.6, 89.0), (89.0, 110.2), 12.6, 10.0, -1,
        [(0, 6.4, 6.4), (0.48, 5.4, 5.4), (0.62, 5.8, 4.8), (0.82, 5.5, 4.4), (1, 4.9, 4.9)], 41.6, None)
    leg('nleg', (57.0, 89.0), (48.0, 110.2), 13.8, 10.2, -1,
        [(0, 7.2, 7.2), (0.5, 5.8, 5.8), (0.64, 6.3, 5.0), (0.84, 6.0, 4.7), (1, 5.2, 4.8)], 0.0, ['fleg'])

    # ======================================================================== le buste (avec le cou)
    # l'épaule proche : une boule centrée sur l'articulation (la même que le départ du bras) ; le trapèze descend du cou
    # en ligne douce jusqu'à elle (tangente) : le raccord épaule / buste est continu, sans marche ni coin
    S = mapp(UC, (S0[0] + P['shs'][0], S0[1] + P['shs'][1] - 0.8 * P['rn']))
    Su = mapp(_inv(U), S)                                  # dans le repère du haut du corps (le bras y est posé)
    NK = (60.6, 50.8)
    dk = math.dist(Su, NK)
    a_t = math.degrees(math.atan2(NK[1] - Su[1], NK[0] - Su[0]) - math.acos(min(1.0, R_SH / dk)))
    sh_ball = ball_arc(Su, R_SH, a_t, -190, step=10)
    trap = [lerp(NK, sh_ball[0], 0.33), lerp(NK, sh_ball[0], 0.7)]
    # l'épaule lointaine : la même idée (le bras lointain, derrière, part d'une boule de même rayon) ; le trapèze
    # descend jusqu'à elle en tangente, le bord du buste ne la quitte que plus bas, vers l'aisselle
    FB = (FS0[0] + P['far'][0], FS0[1] + P['far'][1] - 0.8 * P['rf'] - 0.6 * br)
    NKF = (86.8, 52.6)
    dkf = math.dist(FB, NKF)
    a_tf = math.degrees(math.atan2(NKF[1] - FB[1], NKF[0] - FB[0]) + math.acos(min(1.0, R_FS / dkf)))
    TF = (FB[0] + R_FS * math.cos(math.radians(a_tf)), FB[1] + R_FS * math.sin(math.radians(a_tf)))
    # le flanc du buste remonte en courbe pleine (le grand dorsal) devant l'épaule lointaine jusqu'à la tangente
    far_sh = [(FB[0] + 0.9, FB[1] - 0.6), (FB[0] + 1.9, FB[1] - 3.4), TF, lerp(NKF, TF, 0.5), NKF]
    torso = sm([(66.0, 48.0), NK] + trap + sh_ball + [(Su[0] - 3.0, Su[1] + 5.4), (51.8, 68.6),
                (53.8, 72.6), (54.6, 77.0), (54.2, 81.4), (53.4, 86.0), (56.0, 90.6), (70.0, 91.6), (85.0, 90.6),
                (88.6, 86.4), (87.2, 82.0), (87.0, 78.0), (88.4, 73.0), (89.6, 68.0), (91.4, 63.2)] + far_sh +
               [(82.0, 50.6), (80.0, 47.6)])
    det = [(torso, ('lin', 56, 70, 70, 66, [(0, skin.deep, 0.45), (1, skin.deep, 0)]), 1)]
    # les pectoraux : la plaque éclairée, l'ombre dessous (le proche plus large, trois quarts)
    det += [(sm([(57.4, 56.2), (64.8, 54.8), (72.0, 56.0), (73.4, 60.8), (71.4, 64.4), (64.4, 64.6), (58.6, 61.8)]), skin.light, 0.5),
            (sm([(57.0, 62.6), (63.4, 65.4), (70.6, 65.6), (73.6, 62.4), (74.0, 65.8), (70.8, 67.8), (63.2, 67.6), (56.4, 64.6)]), skin.shadow, 0.8),
            (sm([(75.6, 57.0), (82.0, 55.6), (88.6, 57.8), (88.4, 62.4), (83.4, 64.2), (76.6, 63.6)]), skin.hi, 0.4),
            (sm([(75.4, 63.6), (82.6, 64.8), (88.4, 62.6), (87.6, 65.4), (82.6, 67.0), (75.6, 66.4)]), skin.shadow, 0.75),
            (ribbon([(74.4, 56.6), (74.8, 61.4), (74.6, 66.2)], [0.1, 1.2, 0.2]), skin.shadow, 0.6)]
    # les abdominaux : trois paires de blocs (la ligne du milieu décalée vers la droite, trois quarts), qui rétrécissent
    # vers le bas ; des creux doux, le haut de chaque bloc éclairé — jamais des cases
    det += [(ribbon([(74.8, 66.6), (74.4, 72.6), (74.7, 78.4), (75.2, 81.0)], [0.2, 1.1, 1.0, 0.2]), skin.shadow, 0.75),
            (ribbon([(61.8, 70.6), (67.8, 71.4), (73.8, 71.0)], [0.1, 1.0, 0.3]), skin.shadow, 0.7),
            (ribbon([(63.0, 75.6), (68.4, 76.0), (73.8, 75.5)], [0.1, 0.9, 0.3]), skin.shadow, 0.65),
            (ribbon([(75.6, 71.0), (80.4, 71.3), (84.8, 70.2)], [0.3, 0.8, 0.1]), skin.shadow, 0.6),
            (ribbon([(75.6, 75.5), (79.8, 75.8), (83.8, 74.8)], [0.3, 0.7, 0.1]), skin.shadow, 0.55),
            (rpoly([(62.4, 67.6), (73.6, 67.2), (73.4, 70.2), (62.8, 70.0)], 1.4), skin.light, 0.22),
            (rpoly([(63.4, 72.2), (73.6, 71.9), (73.4, 74.7), (63.8, 74.6)], 1.3), skin.light, 0.18),
            (rpoly([(64.4, 76.7), (73.6, 76.4), (73.6, 79.2), (65.2, 79.0)], 1.3), skin.light, 0.15),
            (rpoly([(75.8, 67.4), (84.6, 67.0), (84.2, 69.9), (75.8, 70.2)], 1.3), skin.hi, 0.2),
            (rpoly([(75.8, 72.0), (83.8, 71.8), (83.4, 74.4), (75.8, 74.7)], 1.2), skin.hi, 0.17),
            (rpoly([(75.9, 76.5), (83.0, 76.2), (82.6, 78.8), (76.0, 79.2)], 1.2), skin.hi, 0.14)]
    det += [(ribbon([(56.2, 68.6), (58.4, 74.0), (57.6, 80.6)], [0.1, 1.0, 0.1]), skin.shadow, 0.5),
            (ribbon([(86.6, 68.4), (85.6, 74.4), (85.2, 80.2)], [0.1, 0.9, 0.1]), skin.shadow, 0.55)]
    # la cordelette du collier (les perles se posent dessus)
    beads = [(57.6, 56.6, 1.8), (60.9, 59.6, 2.0), (64.7, 61.9, 2.1), (68.9, 63.1, 2.15), (73.3, 63.5, 2.15),
             (77.7, 63.0, 2.05), (81.8, 61.8, 1.95), (85.6, 59.6, 1.85)]
    det += [(ribbon([(56.0, 55.0)] + [(x, y) for x, y, _ in beads] + [(88.6, 57.0), (90.4, 55.0)], [0.2] + [0.7] * len(beads) + [0.7, 0.2]), ROPE.shadow, 0.9)]
    fig.part('torso', torso, skin, cel=2.0, rim=0.7, cast=1.2, details=det, occl=(skin.deep, 0.22, 3.2))

    # ---- les perles d'ivoire du collier (chacune pose son ombre douce sur la poitrine) ----
    for i, (x, y, r) in enumerate(beads):
        b_ = sm([(x - 1.12 * r, y), (x - 0.5 * r, y - 0.92 * r), (x + 0.6 * r, y - 0.9 * r), (x + 1.12 * r, y - 0.05 * r),
                 (x + 0.55 * r, y + 0.95 * r), (x - 0.55 * r, y + 0.92 * r)])
        fig.part('bead%d' % i, b_, IVORY, cel=0.55, rim=0.45, cast=0.7, cast_on=['torso'],
                 details=[(ellipse(x + 0.35 * r, y - 0.35 * r, 0.45 * r, 0.3 * r, -25), IVORY.hi, 0.95)])

    # ======================================================================== le pagne en peau de tigre, la corde
    cloth = sm([(52.4, 82.4), (60.0, 83.4), (70.0, 84.0), (80.0, 83.6), (89.8, 82.0), (90.6, 86.0), (89.8, 90.2),
                (88.4, 92.6), (86.6, 91.6), (85.2, 94.4), (83.2, 92.8), (81.6, 96.4), (79.8, 94.6), (78.2, 99.0),
                (76.6, 96.8), (75.2, 102.4), (73.6, 97.6), (71.6, 100.6), (70.0, 96.6), (67.8, 99.2), (66.4, 95.8),
                (64.0, 97.4), (62.4, 94.4), (60.0, 95.2), (58.6, 92.6), (56.2, 93.4), (55.0, 90.6), (53.2, 88.2), (52.2, 85.0)],
               sharp=(7, 9, 11, 13, 15, 17, 19, 21, 23, 25), t=0.8)
    # quelques grosses rayures effilées qui suivent la chute du tissu (les unes tombent de la corde, les autres montent
    # des touffes du bas), de longueurs et d'écarts inégaux
    stripes = [([(58.2, 84.0), (59.4, 86.6), (58.8, 89.4)], 1.5), ([(63.8, 96.4), (63.0, 93.0), (63.8, 89.6)], 1.7),
               ([(68.4, 84.6), (69.6, 88.2), (68.8, 91.8)], 1.6), ([(75.0, 101.2), (74.0, 96.8), (74.6, 92.8)], 1.6),
               ([(85.8, 84.2), (86.6, 87.4), (86.0, 90.2)], 1.4), ([(81.0, 95.6), (80.2, 92.8), (80.6, 90.8)], 1.1)]
    cd = []
    for pts, w in stripes:
        cd.append((ribbon(pts, [0.35, w * 1.1, 0.15]), STRIPE, 0.85))
    cd += [(ribbon([(60.8, 85.0), (61.2, 89.6), (60.6, 94.0)], [0.1, 1.1, 0.1]), TIGER.hi, 0.5),
           (ribbon([(72.2, 86.0), (72.6, 92.4), (72.2, 99.0)], [0.1, 1.3, 0.1]), TIGER.hi, 0.55),
           (ribbon([(77.2, 86.4), (77.6, 91.6), (77.0, 96.0)], [0.1, 1.0, 0.1]), TIGER.shadow, 0.55),
           (ribbon([(66.0, 86.0), (65.8, 91.0), (65.4, 95.4)], [0.1, 0.9, 0.1]), TIGER.shadow, 0.5)]
    fig.part('cloth', cloth, TIGER, cel=1.4, rim=0.7, cast=1.2, details=cd)
    rope_c = [(51.2, 81.8), (60.0, 82.8), (70.0, 83.4), (80.0, 83.0), (90.6, 81.6)]
    rope = limb(rope_c, [3.0, 3.0], n=16)
    rd = []
    for i in range(1, 18):
        t = i / 18
        c_ = resample(rope_c, 18)[i]
        rd.append((ellipse(c_[0] + 0.2, c_[1] - 0.25, 0.95, 0.42, -52), ROPE.hi, 0.55))
        rd.append((ellipse(c_[0] - 0.55, c_[1] + 0.6, 0.7, 0.32, -52), ROPE.shadow, 0.5))
    fig.part('rope', rope, ROPE, cel=0.8, rim=0.5, cast=1.0, details=rd)
    # le noeud côté lointain et ses deux bouts effilochés
    end1 = sm([(79.0, 83.6), (80.4, 84.0), (79.8, 88.0), (79.4, 90.6), (79.8, 92.4), (78.6, 91.4), (77.8, 92.6), (78.0, 89.6), (78.2, 86.4)],
              sharp=(4, 5, 6))
    end2 = sm([(81.8, 83.6), (83.2, 83.8), (83.6, 87.4), (84.2, 90.0), (83.8, 91.6), (83.2, 90.6), (82.4, 91.4), (82.6, 88.6), (82.0, 86.0)],
              sharp=(4, 5, 6))
    fig.part('end1', end1, ROPE, cel=0.6, rim=0.4, cast=0.8,
             details=[(ribbon([(79.4, 85.0), (79.2, 88.0)], [0.6, 0.1]), ROPE.hi, 0.6)])
    fig.part('end2', end2, ROPE, cel=0.6, rim=0.4, cast=0.8,
             details=[(ribbon([(82.8, 85.0), (83.2, 88.2)], [0.6, 0.1]), ROPE.hi, 0.6)])
    knot = sm([(78.4, 82.0), (79.6, 80.2), (81.4, 80.0), (82.6, 80.9), (84.0, 80.6), (84.8, 82.4), (83.8, 84.4),
               (81.6, 84.9), (79.6, 84.6)])
    fig.part('knot', knot, ROPE, cel=0.8, rim=0.6, cast=1.0,
             details=[(ribbon([(80.6, 80.3), (81.2, 82.6), (82.2, 84.7)], [0.1, 0.8, 0.1]), ROPE.shadow, 0.75),
                      (ellipse(80.0, 81.6, 0.9, 0.6, -30), ROPE.hi, 0.85), (ellipse(83.4, 81.8, 0.8, 0.55, -30), ROPE.hi, 0.8)])

    # ======================================================================== le kanabō (repère : G, u vers la tête de fer)
    G, ang = P['G'], P['ang']
    lk = P['length']

    def C(sh):
        return xf(sh, G[0], G[1], ang, lk, 1)
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    nv = (-u[1], u[0])
    lit_plus = (nv[0] * 0.6 - nv[1] * 0.8) > 0          # le pan « +t » regarde-t-il la lumière ?
    sgn = 1 if lit_plus else -1
    HW0, HW1, SA, SB = 4.6, 6.6, 12.8, 33.4
    head_c = C(sm([(SA, -HW0), (SB - 0.8, -HW1), (SB, -HW1 + 1.2), (SB, HW1 - 1.2), (SB - 0.8, HW1), (SA, HW0)],
                  sharp=(0, 1, 2, 3, 4, 5), t=0.5))
    # les trois pans visibles du fer à huit pans (le pan éclairé, le pan du milieu, le pan dans l'ombre)
    face_lit = C(sm([(SA, 0.36 * HW0 * sgn), (SB, 0.36 * HW1 * sgn), (SB, HW1 * sgn), (SA, HW0 * sgn)], sharp=(0, 1, 2, 3), t=0.3))
    face_dark = C(sm([(SA, -0.36 * HW0 * sgn), (SB, -0.36 * HW1 * sgn), (SB, -HW1 * sgn), (SA, -HW0 * sgn)], sharp=(0, 1, 2, 3), t=0.3))
    hd_ = [(face_lit, iron.light, 0.85), (face_dark, iron.deep, 0.5),
           (C(ribbon([(SA + 1, 0.36 * HW0 * sgn), ((SA + SB) / 2, 0.36 * (HW0 + HW1) / 2 * sgn), (SB - 0.6, 0.36 * HW1 * sgn)], [0.1, 0.6, 0.1])), iron.hi, 0.8),
           (C(ribbon([(SA + 1, -0.36 * HW0 * sgn), ((SA + SB) / 2, -0.36 * (HW0 + HW1) / 2 * sgn), (SB - 0.6, -0.36 * HW1 * sgn)], [0.1, 0.5, 0.1])), iron.deep, 0.6),
           (C(sm([(SB - 1.2, -HW1), (SB, -HW1 + 1.2), (SB, HW1 - 1.2), (SB - 1.2, HW1)], sharp=(0, 1, 2, 3), t=0.3)), iron.shadow, 0.55)]
    if hot > 0:
        hd_.append((head_c, ('lin', *C(Shape([((SA, 0), [])])).subs[0][0], *C(Shape([((SB, 0), [])])).subs[0][0],
                             [(0, LAVA[4], 0.25 * hot), (1, LAVA[2], 0.45 * hot)]), 1))
    fig.part('chead', head_c, iron, cel=1.0, rim=0.7, cast=0, details=hd_)
    # les clous : rangées décalées ; ceux du bord dépassent de la silhouette
    STUDS = [(16.2, (-1.0, -0.36, 0.36, 1.0)), (20.8, (-0.68, 0.0, 0.68)), (25.4, (-1.0, -0.36, 0.36, 1.0)), (30.0, (-0.68, 0.0, 0.68))]
    k_ = 0
    for s_, ts in STUDS:
        hw = HW0 + (HW1 - HW0) * (s_ - SA) / (SB - SA)
        for tt in ts:
            t_ = tt * hw * (0.96 if abs(tt) == 1 else 1)
            r = 1.25 if abs(tt) == 1 else 1.05
            st = C(sm([(s_ - r, t_), (s_, t_ - r), (s_ + r, t_), (s_, t_ + r)], t=0.6))
            cx_, cy_ = C(Shape([((s_, t_), [])])).subs[0][0]
            fig.part('stud%d' % k_, st, iron, cel=0.35, rim=0.3, cast=0.5, cast_on=['chead'],
                     details=[(ellipse(cx_ + 0.3, cy_ - 0.35, 0.42, 0.32), iron.glint, 0.85)])
            k_ += 1
    # le collier d'or évasé, le manche de fer, la bague d'or et le pommeau rond
    collar = C(sm([(9.0, -2.3), (12.9, -HW0 - 0.6), (13.6, -HW0 - 0.2), (13.6, HW0 + 0.2), (12.9, HW0 + 0.6), (9.0, 2.3)], sharp=(0, 5), t=0.7))
    fig.part('collar', collar, GOLD, cel=0.7, rim=0.6, cast=0.8, cast_on=['chead'],
             details=[(C(ribbon([(9.6, 1.6 * sgn), (12.0, 3.6 * sgn), (13.2, 4.6 * sgn)], [0.1, 0.6, 0.1])), GOLD.hi, 0.9)])
    handle = C(sm([(-13.2, -1.35), (9.4, -1.35), (9.4, 1.35), (-13.2, 1.35)], sharp=(0, 1, 2, 3), t=0.3))
    fig.part('handle', handle, iron, cel=0.5, rim=0.4, cast=0, details=[(C(ribbon([(-12, 0.7 * sgn), (0, 0.75 * sgn), (9, 0.7 * sgn)], [0.1, 0.5, 0.1])), iron.hi, 0.7)])
    ring_ = C(rpoly([(-14.4, -1.9), (-12.6, -1.9), (-12.6, 1.9), (-14.4, 1.9)], 0.5))
    fig.part('cring', ring_, GOLD, cel=0.4, rim=0.4, cast=0.5)
    pom = C(ellipse(-15.6, 0, 1.75, 1.95))
    pc = C(Shape([((-15.6, 0), [])])).subs[0][0]
    fig.part('pommel', pom, iron, cel=0.5, rim=0.5, cast=0.5, details=[(ellipse(pc[0] + 0.5, pc[1] - 0.55, 0.6, 0.45), iron.glint, 0.9)])

    # ======================================================================== le bras proche (droit) : épaule → coude → poignet
    # d'un seul tenant ; le coude est placé par le squelette (le poignet suit le poing, qui suit la massue)
    wr = P['wr']
    W = (G[0] + u[0] * wr[0] + nv[0] * wr[1], G[1] + u[1] * wr[0] + nv[1] * wr[1])
    E, W2 = ik(Su, W, L1, L2, P['bend'])
    arm = body_limb([Su, E, W2], [(0, R_SH, R_SH), (0.22, 6.7, 6.9), (0.42, 6.3, 6.6), (0.57, 5.3, 5.5),
                                   (0.67, 5.8, 5.9), (0.86, 5.0, 5.1), (1, 4.6, 4.6)], n=26, round_start=True)
    a1, a2 = Seg(Su, E), Seg(E, W2)
    aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
    aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
    ad = [
        # le deltoïde éclairé (le haut de l'épaule), sa limite douce en V sur le bras
        (ellipse(*a1.at(0.08, 1.4), 4.6, 5.2, aa1), skin.light, 0.45),
        (ribbon([a1.at(0.2, -5.0), a1.at(0.4, -1.2), a1.at(0.32, 4.2)], [0.1, 0.8, 0.1]), skin.shadow, 0.4),
        # le biceps devant (éclairé), le triceps dans l'ombre (bande du dos)
        (ellipse(*a1.at(0.64, 2.6), 2.6, 4.8, aa1 - 90), skin.light, 0.38),
        (ribbon([a1.at(0.45, 4.6), a1.at(0.66, 5.0), a1.at(0.86, 4.4)], [0.1, 0.8, 0.1]), skin.hi, 0.35),
        # l'avant-bras qui s'affine : le muscle près du coude éclairé
        (ellipse(*a2.at(0.3, 1.8), 2.2, 3.6, aa2 - 90), skin.light, 0.45),
    ]
    # le liseré de lumière du bras : partout, SAUF sur le bord de la boule d'épaule qui passe sur le buste (là, le bras
    # et le buste ne font qu'un : aucune ligne claire entre eux)
    RIM = 0.7
    a_, b_, c_, d_ = U[:4]
    det_ = a_ * d_ - b_ * c_ or 1
    rdx, rdy = -RIM * 0.75, RIM
    rim_d = arm.d() + arm.move((d_ * rdx - c_ * rdy) / det_, (-b_ * rdx + a_ * rdy) / det_).d()
    big = 'M-200 -200H400V400H-200Z'
    # la zone : la part de la boule qui passe sur le buste (de la tangente du trapèze au creux de l'aisselle)
    zone = sm([Su] + ball_arc(Su, R_SH + 3.2, a_t, 95, step=15), sharp=(0,), t=0.2).d()
    tor_u = torso.map(lambda q: mapp(mS(1, 1 + 0.014 * br, 72, 84), q)).d()
    cz, czn, ctn = fig.uid('c'), fig.uid('c'), fig.uid('c')
    fig.defs += ['<clipPath id="%s"><path d="%s"/></clipPath>' % (cz, zone),
                 '<clipPath id="%s"><path clip-rule="evenodd" d="%s%s"/></clipPath>' % (czn, big, zone),
                 '<clipPath id="%s"><path clip-rule="evenodd" d="%s%s"/></clipPath>' % (ctn, big, tor_u)]
    rim_p = '<path d="%s" fill-rule="evenodd" fill="FILL" opacity="0.85"%s/>'
    ad.append((rim_p % (rim_d, ' clip-path="url(#%s)"' % czn) +
               '<g clip-path="url(#%s)">%s</g>' % (cz, rim_p % (rim_d, ' clip-path="url(#%s)"' % ctn)), skin.hi, 1))
    fig.part('narm', arm, skin, cel=1.8, rim=0, cast=1.3, cast_on=['torso', 'cloth', 'rope', 'nleg', 'bead0', 'bead1', 'chead', 'collar', 'handle'],
             details=ad)

    # ---- le poing proche, serré sur le manche : le dos de la main, la rangée des jointures, quatre doigts repliés ----
    def F(sh):
        return xf(sh, G[0], G[1], ang)
    fist = F(sm([(-6.6, 4.6), (-7.0, -0.8), (-5.8, -5.8), (-1.0, -7.4), (4.2, -6.6), (6.6, -3.0), (6.4, 2.4), (3.4, 5.4), (-2.4, 6.4)]))
    fdet = [(F(sm([(-6.2, 4.2), (-6.4, -0.6), (-2.0, -2.0), (4.4, -1.4), (6.0, 2.2), (3.2, 5.0), (-2.4, 5.8)])), skin.light, 0.35)]
    for u0, u1 in ((-6.0, -3.0), (-3.0, 0.0), (0.0, 3.0), (3.0, 5.9)):
        seg = F(rpoly([(u0 + 0.15, -2.2), (u1 - 0.15, -2.2), (u1 - 0.3, -6.8 + abs(u0 + u1) * 0.12), (u0 + 0.3, -6.8 + abs(u0 + u1) * 0.12)], [0.7, 0.7, 1.4, 1.4]))
        fdet += [(seg, skin.base, 0.9),
                 (F(ellipse((u0 + u1) / 2 + 0.2, -3.0, abs(u1 - u0) * 0.36, 0.7)), skin.hi, 0.5),
                 (F(ribbon([(u1, -2.6), (u1 - 0.05, -4.6), (u1 + 0.1, -6.2)], [0.1, 0.55, 0.1])), skin.deep, 0.55)]
    fig.part('fist', fist, skin, cel=1.3, rim=0.7, cast=1.1, details=fdet)
    thumb = F(limb([(-2.0, 3.6), (1.6, 2.6), (4.6, 0.6)], [3.6, 3.3, 2.9]))
    fig.part('thumb', thumb, skin, cel=0.8, rim=0.6, cast=0.8, cast_on=['fist', 'handle', 'collar'])
    # le bracelet d'or au poignet, en travers de l'avant-bras (il cache le raccord du poing)
    bw = add(W2, a2.u, -0.9)
    brac = xf(rpoly([(-1.3, -5.3), (1.3, -5.3), (1.3, 5.3), (-1.3, 5.3)], 1.0), bw[0], bw[1], aa2)
    fig.part('nbrac', brac, GOLD, cel=0.6, rim=0.6, cast=0.8,
             details=[(xf(ribbon([(-0.6, -4.4), (-0.7, 0), (-0.6, 4.4)], [0.1, 0.6, 0.1]), bw[0], bw[1], aa2), GOLD.hi, 0.9)])

    # ======================================================================== la tête
    ja = P['jaw'] * 2.6

    def J(p, w=1.0):
        """Un point de la mâchoire du bas, qui tourne autour de la charnière quand la gueule s'ouvre."""
        if not ja:
            return p
        r = rot((p[0] - HINGE[0], p[1] - HINGE[1]), ja * w)
        return (HINGE[0] + r[0], HINGE[1] + r[1])

    head = sm([(62.6, 33.2), (65.6, 28.4), (71.0, 26.0), (78.6, 25.2), (85.8, 26.0), (90.0, 28.6), (92.0, 32.2),
               (92.9, 35.6), (92.3, 38.4), (93.2, 40.0), (95.2, 41.0), (97.4, 41.9), (98.4, 43.8), (97.8, 45.7), (95.8, 46.8), (93.4, 46.8),
               (92.6, 48.2), (92.3, 49.8), J((92.5, 51.4)), J((92.5, 53.8)), J((91.0, 55.8)), J((85.0, 56.6)), J((78.0, 56.2)),
               J((72.0, 54.4), 0.6), (67.2, 51.0), (63.2, 46.6), (61.8, 40.0)])
    hd = []
    # le plan de côté (vers l'oreille) dans l'ombre ; la joue proche à mi-ton ; le plan de face éclairé
    hd += [(sm([(61.6, 36.0), (66.6, 35.4), (71.6, 38.6), (74.0, 44.0), (75.6, 49.8), J((76.8, 55.6)), J((72.0, 54.4), 0.6),
                (67.2, 51.0), (63.2, 46.6)]), skin.shadow, 0.55),
           (sm([(84.0, 41.6), (90.6, 40.6), (92.4, 42.4), (92.4, 46.2), (88.0, 46.6), (84.6, 45.2)]), skin.light, 0.55),
           (sm([(77.0, 26.4), (85.0, 26.4), (88.4, 29.4), (86.8, 33.4), (80.0, 34.0), (76.0, 31.0)]), skin.hi, 0.35)]
    # le gros nez (avant les yeux) : le flanc dans l'ombre, le bulbe rond éclairé qui dépasse, l'aile, la narine
    hd += [(sm([(85.6, 40.0), (87.4, 42.0), (90.6, 43.0), (93.2, 45.6), (91.4, 46.9), (88.4, 46.0), (85.8, 43.4)]), skin.shadow, 0.5),
           (sm([(90.8, 41.8), (95.2, 41.4), (97.6, 42.4), (98.2, 44.4), (97.0, 46.2), (94.0, 46.4), (91.4, 44.8)]), skin.light, 0.85),
           (ellipse(96.3, 42.7, 1.2, 0.7, 18), skin.hi, 0.95),
           (sm([(89.8, 43.8), (92.6, 43.4), (94.2, 45.2), (92.6, 46.7), (89.8, 46.3)]), skin.base, 0.92),
           (ribbon([(90.0, 44.0), (89.6, 45.4), (91.0, 46.7)], [0.1, 0.6, 0.1]), skin.deep, 0.65),
           (ellipse(93.4, 46.1, 1.0, 0.45, 10), '#2a0b24', 0.9),
           (ribbon([(89.6, 47.1), (93.0, 47.4), (96.6, 46.6)], [0.1, 0.8, 0.1]), skin.deep, 0.5)]
    # les orbites, creusées sous les arcades
    hd += [(sm([(72.0, 37.6), (79.0, 37.2), (85.0, 39.0), (83.0, 42.4), (77.4, 43.0), (73.2, 41.4)]), skin.deep, 0.5),
           (sm([(86.4, 38.6), (91.6, 37.2), (92.4, 39.4), (90.6, 42.0), (87.0, 42.2)]), skin.deep, 0.45)]
    # les yeux jaunes féroces : même ligne, le lointain plus étroit (son coin intérieur caché par l'arête du nez)
    eyeN = sm([(74.8, 39.4), (78.4, 39.6), (82.0, 40.8), (80.6, 42.1), (77.2, 42.2), (75.4, 41.2)], sharp=(0, 2))
    eyeF = sm([(86.8, 39.8), (89.0, 39.6), (90.6, 40.2), (89.8, 41.6), (87.6, 41.7)], sharp=(0, 2))
    eye_hot = glow > 0.5
    for e, (cx, cy), pr in ((eyeN, (78.6, 40.8), 0.85), (eyeF, (88.9, 40.6), 0.62)):
        if P['blink'] > 0.5:
            hd += [(e.scale(1.12, 1.25, cx, cy), skin.deep, 0.7), (e, skin.shadow, 1),
                   (ribbon([(cx - 3.6 * pr / 0.85, cy - 0.2), (cx, cy + 0.6), (cx + 3.4 * pr / 0.85, cy + 0.2)], [0.1, 0.7, 0.1]), '#2a0b24', 0.9)]
        else:
            yc = ('rad', cx + 0.4, cy - 0.3, 3.6, 2.2, [(0, '#fffbe4'), (0.4, '#fff2a0'), (1, LAVA[1])]) if eye_hot else \
                 ('rad', cx + 0.4, cy - 0.3, 3.6, 2.2, [(0, '#fff6a8'), (0.5, EYE_Y), (1, '#f2b830')])
            hd += [(e.scale(1.14, 1.34, cx - 0.2, cy), '#2a0b24', 0.92), (e, yc, 1),
                   (ribbon([(cx - 3.4 * pr / 0.85, cy + 0.9), (cx, cy + 1.35), (cx + 2.6 * pr / 0.85, cy + 1.0)], [0.1, 0.5, 0.1]), EYE_K, 0.7)]
            if not eye_hot:
                hd += [(ellipse(cx + 0.9 * pr, cy, 0.62 * pr, 0.95 * pr), PUPIL, 1),
                       (ellipse(cx + 1.15 * pr, cy - 0.45 * pr, 0.3 * pr, 0.26 * pr), '#ffffff', 1)]
    # l'arête du nez, claire, qui descend d'entre les yeux et cache le coin intérieur de l'oeil lointain
    hd += [(ribbon([(85.9, 38.4), (86.5, 40.4), (88.2, 42.0), (91.6, 42.4)], [0.4, 1.3, 1.1, 0.3]), skin.light, 1),
           (ribbon([(86.3, 38.8), (86.8, 40.4), (88.4, 41.6)], [0.1, 0.5, 0.1]), skin.hi, 0.6)]
    # les sourcils noirs épais froncés en V (le bout intérieur plus bas), le dessus bleuté
    browN = sm([(69.8, 36.6), (73.0, 35.2), (78.4, 35.8), (83.2, 37.2), (86.4, 38.9), (85.6, 40.1), (81.0, 39.4), (76.0, 38.5), (71.4, 38.4)], sharp=(0, 4))
    browF = sm([(86.6, 38.6), (88.8, 36.6), (91.2, 35.0), (92.7, 35.1), (92.3, 36.4), (89.8, 38.0), (87.6, 39.6)], sharp=(0, 3))
    hd += [(browN, ('lin', 78, 35, 78, 40, [(0, MANE.light), (0.4, MANE.base), (1, MANE.deep)]), 1),
           (browF, ('lin', 90, 35, 90, 39.6, [(0, MANE.light), (0.4, MANE.base), (1, MANE.deep)]), 1),
           (ribbon([(71.0, 36.4), (76.0, 35.8), (82.6, 37.4)], [0.1, 0.6, 0.1]), MANE.hi, 0.7),
           (ribbon([(88.4, 37.2), (90.4, 35.8), (92.2, 35.4)], [0.1, 0.45, 0.1]), MANE.hi, 0.6)]
    # les plis de colère : au front et entre les sourcils
    hd += [(ribbon([(85.0, 34.0), (85.6, 35.8), (86.2, 37.6)], [0.1, 0.8, 0.1]), skin.deep, 0.6),
           (ribbon([(86.6, 33.6), (87.4, 35.4)], [0.6, 0.1]), skin.shadow, 0.6),
           (ribbon([(77.6, 31.6), (81.2, 30.8), (85.0, 31.4)], [0.1, 0.8, 0.1]), skin.shadow, 0.5),
           (ribbon([(77.8, 30.7), (81.2, 29.9), (84.8, 30.5)], [0.1, 0.5, 0.1]), skin.hi, 0.5),
           (ribbon([(79.0, 33.8), (82.0, 33.2), (84.4, 33.6)], [0.1, 0.6, 0.1]), skin.shadow, 0.45)]
    # la pommette sous l'oeil proche ; le pli du rictus qui descend du nez au coin de la gueule
    hd += [(ribbon([(75.6, 43.8), (79.6, 43.6), (83.6, 44.6)], [0.1, 1.1, 0.1]), skin.light, 0.6),
           (ribbon([(89.6, 45.6), (85.6, 46.4), (80.6, 47.2), (77.0, 49.2)], [0.1, 0.9, 0.9, 0.1]), skin.deep, 0.55)]
    # la gueule ouverte : la gorge rouge sombre, les gencives, les dents, deux crocs en haut, deux petits en bas
    up_edge = [(77.0, 49.4), (80.0, 48.8), (86.0, 48.6), (90.6, 48.7), (92.6, 49.6)]
    lo_edge = [J((92.6, 50.4)), J((90.2, 53.0)), J((85.0, 53.7)), J((80.0, 53.3)), J((77.4, 51.6))]
    mouth = sm(up_edge + lo_edge, sharp=(0, 4), t=0.8)
    mc = lerp(up_edge[2], lo_edge[2], 0.5)
    hd += [(mouth.scale(1.05, 1.12, mc[0], mc[1]), '#2a0b24', 0.95),
           (mouth, ('rad', mc[0] + 1, mc[1] + 0.6, 7.0, 3.2, [(0, '#7a1a30'), (0.6, GORGE), (1, '#24061a')]), 1)]
    tongue_ = sm([J((80.0, 53.0)), J((84.0, 51.6)), J((89.0, 52.0)), J((90.6, 53.0)), J((85.0, 53.6))])
    hd += [(tongue_, '#a02a40', 0.75)]
    # les dents du haut (une rangée), les gencives au-dessus des coins
    hd += [(ribbon([(78.2, 49.4), (83.0, 49.0), (88.0, 49.0), (91.8, 49.6)], [0.4, 1.5, 1.5, 0.4]), IVORY.base, 1),
           (ribbon([(78.6, 49.2), (83.0, 48.85), (88.0, 48.85), (91.4, 49.3)], [0.2, 0.6, 0.6, 0.2]), IVORY.hi, 0.9)]
    for xg in (80.6, 84.4, 86.6):
        hd.append((ribbon([(xg, 48.9), (xg - 0.1, 50.0)], [0.35, 0.1]), IVORY.shadow, 0.7))
    # les crocs du haut (le proche plus gros)
    hd += [(sm([(80.4, 49.4), (83.0, 49.2), (82.0, 52.6)], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
           (sm([(81.8, 49.4), (83.0, 49.2), (82.0, 52.4)], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.8),
           (sm([(88.2, 49.3), (90.2, 49.4), (89.0, 51.9)], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
           (sm([(89.2, 49.3), (90.2, 49.4), (89.0, 51.7)], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.7)]
    # les dents du bas et les deux petits crocs
    lt = [J(p) for p in [(79.0, 52.8), (84.0, 53.3), (89.6, 52.6)]]
    hd += [(ribbon(lt, [0.3, 1.3, 0.3]), IVORY.shadow, 1),
           (sm([J((82.0, 53.4)), J((84.0, 53.4)), J((83.2, 50.6))], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
           (sm([J((86.8, 53.2)), J((88.6, 52.8)), J((87.4, 50.4))], sharp=(0, 1, 2), t=0.7), IVORY.base, 1)]
    # les lèvres : la ligne sombre au-dessus des dents, la lèvre du bas éclairée, le menton carré éclairé
    hd += [(ribbon([(76.8, 49.2), (80.0, 48.0), (86.0, 47.8), (91.0, 47.9), (92.6, 49.0)], [0.1, 0.8, 0.9, 0.7, 0.1]), skin.deep, 0.6),
           (ribbon([J((78.0, 54.4)), J((84.6, 54.9)), J((91.4, 53.8))], [0.1, 1.0, 0.1]), skin.light, 0.65),
           (sm([J((84.0, 55.0)), J((91.6, 54.2)), J((91.2, 56.0)), J((85.0, 56.4))]), skin.hi, 0.35),
           (ribbon([J((72.6, 53.4)), J((78.0, 55.6)), J((86.0, 56.2))], [0.1, 0.8, 0.1]), skin.deep, 0.45)]
    fig.part('head', head, skin, grad=(96, 30, 66, 54, [(0, skin.light), (0.5, skin.base), (1, skin.shadow)]),
             cel=1.3, rim=0.65, cast=1.4, details=hd)
    # les deux défenses d'ivoire qui montent de la mâchoire (la proche devant la lèvre)
    tN = sm([J(p) for p in [(75.8, 54.2), (76.4, 51.0), (77.0, 48.2), (78.6, 45.8), (79.0, 48.4), (78.8, 51.4), (78.6, 54.0)]], sharp=(3,))
    fig.part('tuskN', tN, IVORY, cel=0.6, rim=0.5, cast=0.7, cast_on=['head'],
             details=[(ribbon([J(p) for p in [(78.2, 53.0), (78.4, 49.6), (78.7, 46.8)]], [0.6, 0.5, 0.1]), IVORY.hi, 0.9)])
    tF = sm([J(p) for p in [(90.6, 52.8), (90.6, 50.4), (91.6, 48.2), (92.6, 47.4), (92.6, 49.8), (92.4, 52.6)]], sharp=(3,))
    fig.part('tuskF', tF, IVORY, cel=0.5, rim=0.45, cast=0.6, cast_on=['head'])
    # la calotte de cheveux sur l'arrière du crâne (de la corne proche à la nuque) : elle rejoint les mèches du dos,
    # la crinière est ainsi une seule masse qui pousse du crâne ; la limite du front finit en petite pointe
    capc = sm([(73.4, 26.4), (67.6, 26.2), (63.2, 29.0), (60.8, 34.2), (61.0, 39.6), (62.2, 42.0), (63.0, 38.6),
               (64.6, 36.6), (66.8, 35.4), (69.4, 33.6), (71.2, 30.0)], sharp=(5,))
    fig.part('capc', capc, MANE, grad=(72, 26, 62, 40, [(0, '#6a5e94'), (0.5, MANE.base), (1, MANE.shadow)]),
             cel=0.9, rim=0.7, cast=1.1, cast_on=['head'],
             details=[(ribbon([(70.4, 27.4), (66.0, 28.0), (62.6, 31.4)], [0.1, 0.9, 0.1]), MANE.light, 0.6)])
    # l'oreille pointue (couchée vers l'arrière), son anneau d'or
    ear = sm([(67.6, 40.0), (65.0, 38.2), (61.0, 35.2), (62.2, 39.6), (63.4, 43.8), (65.0, 47.2), (66.8, 47.0), (67.8, 43.6)], sharp=(2,))
    fig.part('ear', ear, skin, cel=0.8, rim=0.5, cast=0.8, cast_on=['head'],
             details=[(sm([(66.6, 41.0), (64.6, 39.6), (63.0, 38.2), (64.2, 41.8), (65.4, 44.8), (66.6, 44.6)], sharp=(2,)), skin.deep, 0.55)])
    ring = ellipse(65.6, 48.8, 1.55, 1.75).hole(ellipse(65.7, 48.9, 0.75, 0.95))
    fig.part('ering', ring, GOLD, cel=0.4, rim=0.4, cast=0.5, cast_on=['head', 'ear'])
    # les cornes d'ivoire : la proche plus grosse ; la base s'enfonce dans la peau
    hornN = sm([(69.4, 35.4), (67.4, 29.0), (66.4, 22.0), (66.8, 16.2), (67.8, 12.2), (69.0, 15.6), (70.8, 21.0),
                (73.4, 26.6), (76.8, 31.2), (76.2, 34.0), (72.8, 35.8)], sharp=(4,))
    fig.part('hornN', hornN, IVORY, grad=(76, 20, 66, 30, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=1.1, rim=0.8, cast=1.2, cast_on=['head', 'capc', 'tA', 'm1', 'm2'],
             details=[(ribbon([(75.0, 31.6), (71.4, 25.4), (69.4, 19.0), (68.2, 14.0)], [0.2, 1.2, 0.8, 0.1]), IVORY.hi, 0.75),
                      (sm([(69.2, 33.0), (76.6, 31.4), (76.2, 34.0), (72.8, 35.8), (69.4, 35.4)]), IVORY.deep, 0.35)])
    # la corne lointaine : plantée à la même hauteur que la proche et symétrique d'elle par rapport à la médiane du
    # crâne (vue de trois quarts : elle part près du bord droit du crâne, au-dessus du bout du sourcil lointain) ;
    # un peu plus courte et plus fine que la proche ; sa pointe s'écarte vers la droite comme la proche vers la gauche
    def HF(pts):
        return [(x + 3.3 + 0.9 * max(0.0, 33.0 - y) / 19.0, y) for x, y in pts]
    hornF = sm(HF([(83.6, 33.4), (82.9, 29.4), (85.2, 24.4), (87.4, 19.2), (89.2, 14.2), (90.4, 18.6), (90.6, 24.6),
                   (89.5, 29.6), (88.6, 33.2), (86.4, 34.4)]), sharp=(4,))
    fig.part('hornF', hornF, IVORY, grad=(95, 20, 86, 30, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=0.9, rim=0.7, cast=1.0, cast_on=['head', 'tB'],
             details=[(ribbon(HF([(88.6, 31.4), (89.4, 24.4), (89.4, 16.4)]), [0.2, 0.9, 0.1]), IVORY.hi, 0.7),
                      (sm(HF([(83.2, 32.0), (89.2, 31.6), (88.8, 33.4), (86.4, 34.4), (83.4, 33.4)])), IVORY.deep, 0.3)])

    # ---- chaque groupe de morceaux prend sa pose ----
    heads = ['m4', 'm3', 'm2', 'm1', 'tA', 'tB', 'head', 'capc', 'tuskN', 'tuskF', 'ear', 'ering', 'hornN', 'hornF']
    fig.pose(heads, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['bead%d' % i for i in range(len(beads))], UC)
    fig.pose(['farm', 'ffist', 'fbrac'], FARM)
    fig.pose(['cloth', 'end1', 'end2'], CLO)
    fig.pose(['rope', 'knot'], PEL)
    club = ['chead', 'collar', 'handle', 'cring', 'pommel'] + ['stud%d' % i for i in range(k_)]
    fig.pose(club + ['narm', 'fist', 'thumb', 'nbrac'], U)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(U=U, G=mapp(U, G), ang=ang + P['lean'] * 1.1, P=P, S=mapp(U, Su),
                   tip=mapp(U, (G[0] + u[0] * SB * lk, G[1] + u[1] * SB * lk)),
                   chest=mapp(TOR, (72, 66)), head=mapp(HEAD, (80, 40)), mouth=mapp(HEAD, (88, 51)),
                   nostril=mapp(HEAD, (93.4, 46.2)), HEAD=HEAD, ROOT=ROOTM)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def _inv(M):
    a, b, c, d, e, f_ = M
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f_ - d * e) / det, (b * e - a * f_) / det)


def main():
    """lenore.svg (grand) et lenore-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-9.webp (512 px de haut) et knights-9-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('lenore', 0.95, 512, ID_JEU), ('lenore-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [round(w, 2), round(h, 2), round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])


if __name__ == '__main__':
    main()
