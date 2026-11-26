# Soyane (myths-10, terre, assassin, légendaire ; ancien nom : Arachné) redessinée en VECTORIEL lisse, dans le style
# moderne de l'interface (même outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/soyane/soyane.py      # → soyane.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/arachne.txt) : une FEMME-ARAIGNÉE. En haut, une femme
# fine (peau très pâle, chignon noir piqué de deux aiguilles d'acier en X à perles rouges, pierre rouge au front, yeux
# en amande au trait noir, iris rouge sang, sourire de prédatrice aux petits crocs), haut rouge ajusté au décolleté
# bordé de chitine, corset et basque de chitine à pointes rouges, épaulières de chitine (la proche avec un crochet),
# deux dagues courbes d'acier à garde d'or ; bras proche levé (coude sur le côté, dague dressée), bras lointain tendu
# bas vers l'ennemi. En bas, une grande araignée noire laquée : gros abdomen rond (marque rouge inventée : un losange
# entre deux crochets), céphalothorax sous la basque, huit pattes aux genoux pointus et aux anneaux rouges, pointes
# posées au sol (quatre lointaines derrière, plus sombres ; quatre proches devant).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides, bez, resample  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fff6ec', '#fbe2d6', '#efc8bc', '#cf96a0', '#8e5a74')
HAIR = Mat('#8a86c4', '#4e4880', '#332d56', '#231e3e', '#17142a', glint='#c8c6f0')
CHIT = Mat('#9a96cc', '#5e5a8c', '#403a64', '#2c2646', '#1d1730', glint='#e4e6ff')      # chitine (devant)
CHITF = Mat('#6e6a9e', '#46416e', '#322c50', '#241e3a', '#17122a', glint='#b8b8e0')     # chitine des pattes du fond
RED = Mat('#ffb486', '#f45e40', '#c62c32', '#8a1a30', '#4a0e28')
STEEL = Mat('#ffffff', '#e2ecf8', '#a6b6d4', '#5f6c94', '#2c2e4c')
GOLD = Mat('#fff2a8', '#f6cc58', '#c4862e', '#7a3e1a', '#3e1c12')
LIPS = ('#7a1a3a', '#b23a52', '#d45a6a')

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (0, -6, 130, 125)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (le buste monte, la poitrine se gonfle) ; sp : déplacement du corps de l'araignée (les
#   pointes des pattes restent plantées) ; lean : la femme se penche en avant (+) depuis la taille ; head / tilt :
#   la tête ; abd : l'abdomen palpite ; legs : {nom: [hanche, genou, cheville, pointe]} (sinon la pose de repos,
#   hanche portée par le corps) ; hand / ang : le poing proche et l'angle de sa dague ; handF / angF : le poing
#   lointain et sa dague ; blink : yeux fermés ; ear : balancement de la boucle d'oreille.
S0 = (62.5, 56.6)          # l'épaule proche
SF0 = (91.0, 56.6)         # l'épaule lointaine
LU, LF = 16.4, 13.2        # bras proche : bras, avant-bras (jusqu'au poignet)
LUF, LFF = 9.6, 11.2       # bras lointain (raccourci par le trois-quarts)
HAND0 = (46.6, 41.6)       # le poing proche (point de prise)
ANG0 = -82.0               # sa dague, dressée (un peu vers l'avant)
HANDF0 = (105.4, 61.6)     # le poing lointain
ANGF0 = -16.0              # sa dague, pointée vers l'ennemi

LEGS0 = {
    # côté lointain (derrière le corps, plus sombres)
    'L1': [(38.0, 70.0), (25.0, 54.2), (12.6, 92.0), (6.6, 116.0)],
    'R4': [(97.0, 80.0), (113.4, 66.0), (121.2, 92.6), (123.6, 116.0)],
    'R2': [(86.0, 84.0), (98.6, 70.2), (103.4, 95.0), (103.2, 116.0)],
    'L3': [(52.0, 92.0), (44.0, 96.4), (41.4, 106.0), (39.2, 116.0)],
    'L4': [(62.0, 94.0), (57.8, 99.0), (56.8, 106.4), (55.6, 116.0)],
    # côté proche (devant le corps)
    'L2': [(67.0, 97.0), (31.0, 80.6), (21.0, 98.4), (16.2, 116.0)],
    'R3': [(86.0, 87.0), (104.0, 73.2), (114.6, 96.6), (116.6, 116.0)],
    'R1': [(80.0, 88.0), (88.2, 80.6), (93.2, 99.0), (93.0, 116.0)],
}
BACK_LEGS = ['L1', 'R4', 'R2', 'L3', 'L4']
FRONT_LEGS = ['L2', 'R3', 'R1']          # L2 passe devant l'abdomen mais sous le céphalothorax
# largeurs : hanche, genou (fin de la cuisse), cheville, pointe
LEGW = {'L1': (4.6, 3.6, 2.6, 0.5), 'R4': (4.6, 3.5, 2.5, 0.5), 'R2': (4.6, 3.5, 2.6, 0.5), 'L3': (4.4, 3.4, 2.5, 0.5),
        'L4': (4.2, 3.2, 2.4, 0.5), 'L2': (5.4, 4.0, 2.9, 0.55), 'R3': (5.4, 4.0, 2.9, 0.55), 'R1': (5.0, 3.8, 2.8, 0.55)}

REST = dict(breath=0.0, sp=(0.0, 0.0), lean=0.0, head=(0.0, 0.0), tilt=0.0, abd=0.0, legs=None, hand=HAND0, ang=ANG0,
            bend=-1.0, handF=HANDF0, angF=ANGF0, bendF=1.0, blink=0.0, ear=0.0, grin=0.0, smear=0.0, smearF=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def ik(S, W, L1, L2, bend):
    """Le coude d'un bras (épaule S, poignet W, longueurs), plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


# ---------- une patte d'araignée : UNE seule forme de la hanche à la pointe ----------

def _qcurve(a, b, bulge, n):
    """Des points sur un arc doux de a à b, bombé de `bulge` (vers la gauche de a→b)."""
    v = (b[0] - a[0], b[1] - a[1])
    L = math.hypot(*v) or 1
    nrm = (-v[1] / L, v[0] / L)
    c = ((a[0] + b[0]) / 2 + nrm[0] * bulge * 2, (a[1] + b[1]) / 2 + nrm[1] * bulge * 2)
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
    return out


def leg_geom(pts, ws, spike=1.5, bulge=0.9):
    """La patte : cuisse (hanche → genou, un peu bombée vers le haut), jambe (genou → cheville), tarse (cheville →
    pointe). Le genou est POINTU du côté extérieur, creusé en douceur à l'intérieur ; tout le reste est lisse.
    Rend (forme, ligne médiane, abscisses du genou et de la cheville dans la ligne, côté extérieur au genou)."""
    hip, knee, ank, tip = pts
    w0, wk, wa, wt = ws
    u1 = norm((knee[0] - hip[0], knee[1] - hip[1]))
    u2 = norm((ank[0] - knee[0], ank[1] - knee[1]))
    out = norm((u1[0] - u2[0], u1[1] - u2[1]))
    # la cuisse se bombe vers l'extérieur du genou (vers le haut), la jambe un peu aussi
    def bulge_sign(a, b):
        v = (b[0] - a[0], b[1] - a[1])
        n = (-v[1], v[0])
        return 1 if n[0] * out[0] + n[1] * out[1] > 0 else -1
    s1 = _qcurve(hip, knee, bulge * bulge_sign(hip, knee), 8)
    s2 = _qcurve(knee, ank, 0.35 * bulge_sign(knee, ank), 7)
    s3 = _qcurve(ank, tip, -0.25 * bulge_sign(knee, ank), 6)
    c = s1 + s2[1:] + s3[1:]
    ik_, ia = len(s1) - 1, len(s1) - 1 + len(s2) - 1
    n = len(c)
    ws_ = []
    for i in range(n):
        if i <= ik_:
            t = i / ik_
            ws_.append(w0 + (wk - w0) * t)
        elif i <= ia:
            t = (i - ik_) / (ia - ik_)
            ws_.append(wk * 0.92 + (wa - wk * 0.92) * t + 0.35 * math.sin(math.pi * t))
        else:
            t = (i - ia) / (n - 1 - ia)
            ws_.append(wa + (wt - wa) * t ** 0.9)
    left, right = [], []
    for i, p in enumerate(c):
        if i == ik_:
            nl = (-u1[1], u1[0])
            sgn = 1 if nl[0] * out[0] + nl[1] * out[1] > 0 else -1
            # le côté extérieur : une pointe ; l'intérieur : un creux doux
            po = (p[0] + out[0] * (ws_[i] / 2 + spike), p[1] + out[1] * (ws_[i] / 2 + spike))
            pi_ = (p[0] - out[0] * ws_[i] * 0.42, p[1] - out[1] * ws_[i] * 0.42)
            (left if sgn > 0 else right).append(po)
            (right if sgn > 0 else left).append(pi_)
            continue
        a = c[max(0, i - 1)]
        b = c[min(n - 1, i + 1)]
        if i == ik_ - 1 or i == ik_ + 1:
            a, b = (c[i - 1], c[i]) if i == ik_ - 1 else (c[i], c[i + 1])
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = ws_[i] / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    # le bout de la hanche arrondi (il est caché sous le corps), la pointe effilée
    hip_cap = [(hip[0] - u1[0] * w0 * 0.45, hip[1] - u1[1] * w0 * 0.45)]
    poly = hip_cap + left + [(tip[0] + u2[0] * 0.0, tip[1])] + right[::-1]
    # indices des coins vifs : la pointe du genou (côté extérieur) et la pointe de la patte
    ko = 1 + ik_ if _is_left_outer(u1, out) else len(hip_cap) + len(left) + 1 + (len(right) - 1 - ik_)
    tip_i = len(hip_cap) + len(left)
    shape = sm(poly, sharp=(ko, tip_i), t=0.85)
    return shape, c, ik_, ia, out


def _is_left_outer(u1, out):
    nl = (-u1[1], u1[0])
    return nl[0] * out[0] + nl[1] * out[1] > 0


def band_at(c, i, w, ws=7.0, k=0.0):
    """Un anneau en travers de la patte au point i de sa ligne (largeur le long de la patte : w ; assez large pour être
    découpé par la patte)."""
    n = len(c)
    a = c[max(0, i - 1)]
    b = c[min(n - 1, i + 1)]
    u = norm((b[0] - a[0], b[1] - a[1]))
    nv = (-u[1], u[0])
    p = (c[i][0] + u[0] * k, c[i][1] + u[1] * k)
    h = ws / 2
    pts = [(p[0] - u[0] * w / 2 + nv[0] * h, p[1] - u[1] * w / 2 + nv[1] * h),
           (p[0] + u[0] * w / 2 + nv[0] * h, p[1] + u[1] * w / 2 + nv[1] * h),
           (p[0] + u[0] * w / 2 - nv[0] * h, p[1] + u[1] * w / 2 - nv[1] * h),
           (p[0] - u[0] * w / 2 - nv[0] * h, p[1] - u[1] * w / 2 - nv[1] * h)]
    return sm(pts, sharp=(0, 1, 2, 3), t=0.2), u


def leg_part(fig, name, pts, far, spines=False):
    mat = CHITF if far else CHIT
    ws = LEGW[name]
    shape, c, ik_, ia, out = leg_geom(pts, ws, spike=1.4 if not far else 1.2)
    n = len(c)
    det = []
    # la lumière : un liseré clair le long de l'arête du dessus de la cuisse et de la jambe (côté haut-droit)
    hi_pts = []
    for i in range(1, n - 2):
        a, b = c[i - 1], c[i + 1]
        u = norm((b[0] - a[0], b[1] - a[1]))
        nv = (-u[1], u[0])
        if nv[0] * 0.6 - nv[1] * 0.8 < 0:
            nv = (-nv[0], -nv[1])
        w = (LEGW[name][0] if i <= ik_ else LEGW[name][1]) * 0.22
        hi_pts.append((c[i][0] + nv[0] * w, c[i][1] + nv[1] * w))
    seg1 = hi_pts[:ik_ - 1]
    seg2 = hi_pts[ik_:ia - 1]
    if len(seg1) > 2:
        det.append((ribbon(seg1, [0.1] + [0.9 if not far else 0.6] * (len(seg1) - 2) + [0.1]), mat.light, 0.85))
    if len(seg2) > 2:
        det.append((ribbon(seg2, [0.1] + [0.7 if not far else 0.5] * (len(seg2) - 2) + [0.1]), mat.light, 0.8))
    # les anneaux rouges : au genou (juste sous la pointe) et à la cheville
    for i, wv, k in ((ik_ + 1, 1.9, 0.0), (ia, 1.6, 0.2)):
        bd, u = band_at(c, i, wv, ws=9, k=k)
        hi_ = band_at(c, i, wv * 0.4, ws=9, k=k - wv * 0.2)[0]
        rr = RED if not far else Mat(RED.hi, '#d84a3a', '#a8242e', '#6e142a', '#3e0a22')
        det += [(bd, rr.base, 1), (hi_, rr.light, 0.85)]
    # un éclat net sur la cuisse
    if not far:
        p = lerp(c[ik_ // 2], c[ik_ // 2 + 1], 0.5)
        det.append((ellipse(p[0] + out[0] * 0.6, p[1] + out[1] * 0.6, 0.9, 0.42,
                            math.degrees(math.atan2(c[ik_][1] - c[0][1], c[ik_][0] - c[0][0]))), mat.glint, 0.85))
    if spines:
        # de petites épines sur la jambe, côté intérieur (vers le bas)
        for j in (ik_ + 3, ik_ + 5):
            if j < ia:
                a, b = c[j - 1], c[j + 1]
                u = norm((b[0] - a[0], b[1] - a[1]))
                nv = (-u[1], u[0])
                if nv[0] * out[0] + nv[1] * out[1] > 0:
                    nv = (-nv[0], -nv[1])
                w = ws[1] * 0.45
                base = (c[j][0] + nv[0] * w * 0.6, c[j][1] + nv[1] * w * 0.6)
                sp = sm([add(base, u, -0.8), add(add(base, nv, 2.2), u, 0.9), add(base, u, 0.9)], sharp=(0, 1, 2), t=0.5)
                fig.part(name + 'sp%d' % j, sp, mat, cel=0, rim=0, cast=0)
    fig.part(name, shape, mat, cel=1.0 if not far else 0.8, rim=0.45 if not far else 0.3, cast=0.9 if not far else 0.6,
             details=det)
    return c[-1]


# ---------- la dague courbe ----------

def dagger_parts(fig, pre, G, ang, length=17.0, flip=1, smear=0.0):
    """Une dague courbe : lame d'acier (dos sombre, fil clair, éclat), garde d'or, poignée rouge, tenue en G (point de
    prise au milieu de la poignée), lame vers `ang`. flip retourne la courbe."""
    def L(sh):
        return xf(sh, G[0], G[1], ang, 1, flip)
    st = 1 + 0.03 * smear
    def Lb(sh):
        return xf(sh, G[0], G[1], ang, st, flip)
    g0 = 3.2      # la garde, à 3,2 du point de prise
    # la lame : un croc courbe (le dos bombé vers -y, le fil creusé)
    back = [(g0 + 0.2, -1.5), (g0 + length * 0.35, -2.1), (g0 + length * 0.7, -2.6), (g0 + length, -4.4)]
    edge = [(g0 + length * 0.78, -1.4), (g0 + length * 0.45, 0.4), (g0 + 0.2, 1.5)]
    blade = Lb(sm(back + edge, sharp=(0, 3, 6), t=0.7))
    fil = Lb(sm([(g0 + 0.2, 0.3), (g0 + length * 0.45, -0.7), (g0 + length * 0.78, -2.3), (g0 + length, -4.4),
                 (g0 + length * 0.78, -1.4), (g0 + length * 0.45, 0.4), (g0 + 0.2, 1.5)], sharp=(0, 3, 6), t=0.7))
    dos = Lb(ribbon([(g0 + 0.6, -1.1), (g0 + length * 0.4, -1.7), (g0 + length * 0.75, -2.4)], [0.1, 0.7, 0.1]))
    glint = Lb(ellipse(g0 + length * 0.5, -1.0, 1.6, 0.32, -6))
    fig.part(pre + 'blade', blade, STEEL, grad=None, cel=0.5, rim=0.35, cast=0,
             details=[(fil, STEEL.hi, 0.95), (dos, STEEL.shadow, 0.8), (glint, '#ffffff', 0.95)])
    grip = L(rpoly([(-3.6, -1.15), (3.0, -1.15), (3.0, 1.15), (-3.6, 1.15)], 0.8))
    fig.part(pre + 'grip', grip, RED, cel=0.4, rim=0.3, cast=0.4,
             details=[(L(ribbon([(-3, -0.4), (2.6, -0.4)], [0.1, 0.1])), RED.light, 0.6)])
    pom = L(ellipse(-4.2, 0, 1.25, 1.25))
    fig.part(pre + 'pom', pom, GOLD, cel=0.4, rim=0.3, cast=0.3)
    guard = L(rpoly([(g0 - 0.9, -2.7), (g0 + 0.9, -2.7), (g0 + 0.9, 2.7), (g0 - 0.9, 2.7)], 0.7))
    fig.part(pre + 'guard', guard, GOLD, cel=0.45, rim=0.4, cast=0.5,
             details=[(L(ellipse(g0 + 0.2, -1.3, 0.35, 0.6)), GOLD.hi, 0.9)])
    tip = mapp(mchain(mT(G[0], G[1]), mR(ang)), (g0 + length * st, -4.4 * flip))
    return tip


def fist_part(fig, name, W, G, ang, far=False, flip=1):
    """Un poing fermé sur la poignée : le dos de la main, quatre doigts repliés, le pouce dessus."""
    def L(sh):
        return xf(sh, G[0], G[1], ang, 1, flip)
    fist = L(sm([(2.4, -2.4), (-1.4, -2.9), (-3.4, -1.0), (-3.2, 1.8), (-1.2, 3.2), (2.2, 3.0), (3.2, 0.6)]))
    det = []
    for u0, u1 in ((2.3, 0.8), (0.8, -0.7), (-0.7, -2.2)):
        det.append((L(ribbon([(u1 + 0.1, 0.9), (u1, 1.9), (u1 + 0.15, 2.8)], [0.1, 0.42, 0.1])), SKIN.shadow, 0.75))
    det.append((L(ellipse(0.4, -1.6, 2.2, 0.8)), SKIN.hi, 0.5))
    fig.part(name, fist, SKIN, cel=0.7, rim=0.45, cast=0.7, details=det)
    thumb = L(limb([(-1.8, -1.9), (0.4, -2.1), (2.4, -1.4)], [1.7, 1.6, 1.4]))
    fig.part(name + 'th', thumb, SKIN, cel=0.4, rim=0.35, cast=0.5, cast_on=[name])


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    sp = P['sp']
    BODY = mT(*sp)                                                        # le corps de l'araignée
    ABD = mchain(BODY, mS(1 + 0.025 * P['abd'], 1 + 0.035 * P['abd'], 26, 86))
    W0 = (77.0, 84.0)                                                     # la taille (pivot du buste)
    U = mchain(BODY, mR(P['lean'] * 1.0, W0[0], W0[1]))                  # la femme (depuis la taille)
    UC = mchain(U, mT(0, -0.6 * br))                                      # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 78, 76))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 82, 47), mS(1.1, 1.1, 82, 47.5))

    # ---- les pattes : celles du fond, puis le corps, puis celles de devant ----
    legs = {k: list(v) for k, v in LEGS0.items()}
    for k in legs:
        legs[k][0] = mapp(BODY, legs[k][0])
        if (P['legs'] or {}).get(k) is None:
            # le genou suit un peu le corps (les pointes restent plantées)
            legs[k][1] = add(legs[k][1], sp, 0.6)
            legs[k][2] = add(legs[k][2], sp, 0.2)
    for k, v in (P['legs'] or {}).items():
        if v is not None:
            legs[k] = [mapp(BODY, v[0])] + list(v[1:])
    tips = {}
    for k in BACK_LEGS:
        tips[k] = leg_part(fig, k, legs[k], far=True)

    # ---- l'abdomen : chitine laquée, une marque rouge, des épines, les filières à l'arrière ----
    for i, (bx, by, a) in enumerate(((37.5, 62.2, -100), (44.0, 61.4, -80), (30.8, 64.6, -118))):
        spn = xf(sm([(0, -1.1), (3.4, 0), (0, 1.1)], sharp=(1,), t=0.6), bx, by + 1.5, a)
        fig.part('aspine%d' % i, spn, CHIT, cel=0, rim=0.3, cast=0)
    spin = sm([(24.4, 82.0), (19.6, 83.2), (18.2, 86.4), (20.0, 89.2), (24.6, 89.8)])
    fig.part('spinner', spin, CHIT, cel=0.6, rim=0.4, cast=0,
             details=[(ellipse(19.6, 86.0, 0.8, 1.6, 10), CHIT.deep, 0.8)])
    abd = sm([(42, 61.6), (54, 63.4), (63.4, 70.4), (67, 80.4), (64.6, 91.2), (56, 98.6), (43, 100.6), (31, 97.8),
              (23.6, 90.4), (22.0, 80.0), (26.4, 69.6), (33.6, 63.6)])
    det = []
    # le volume laqué : une grande lumière douce en haut à droite, le bas dans l'ombre
    det.append((abd, ('rad', 52, 70, 34, 30, [(0, '#6a669a', 0.9), (0.5, CHIT.base, 0.4), (1, CHIT.base, 0)]), 1))
    # la marque rouge : un losange entre deux crochets (comme la face d'une araignée)
    dia = sm([(43.6, 64.8), (47.0, 69.8), (43.8, 75.6), (40.6, 70.0)], sharp=(0, 1, 2, 3), t=0.5)
    det += [(dia.scale(1.22, 1.16, 43.8, 70.2), RED.deep, 0.75), (dia, ('lin', 47, 65, 41, 75, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]), 1),
            (sm([(43.7, 65.6), (46.4, 69.8), (43.9, 70.4)], sharp=(0, 1, 2), t=0.5), '#ffd0b0', 0.55)]
    for sgn, cx in ((-1, 36.0), (1, 51.4)):
        hook = ribbon([(cx + 1.6 * sgn, 64.6), (cx - 0.6 * sgn, 68.6), (cx + 0.2 * sgn, 72.6), (cx + 2.4 * sgn, 75.0)], [0.4, 1.6, 1.5, 0.3])
        det += [(hook.move(-0.25, 0.35), RED.deep, 0.7), (hook, ('lin', cx + 2, 64, cx - 2, 75, [(0, RED.light), (0.6, RED.base), (1, RED.shadow)]), 1)]
    # le reflet net (un seul), et un liseré clair sur le bord haut-droit
    det += [(sm([(51.2, 66.4), (56.4, 66.8), (59.6, 69.6), (57.0, 70.6), (52.2, 69.4)]), '#c4c2ec', 0.85),
            (ellipse(56.6, 68.0, 1.4, 0.7, 25), '#f4f4ff', 0.95)]
    fig.part('abd', abd, CHIT, grad=(60, 64, 30, 98, [(0, '#56527e'), (0.45, CHIT.base), (1, '#221c38')]),
             cel=2.2, rim=0.8, cast=0, details=det, occl=(CHIT.deep, 0.3, 3.6))

    tips['L2'] = leg_part(fig, 'L2', legs['L2'], far=False, spines=True)
    # ---- le céphalothorax (sous la basque, entre les pattes) ----
    ceph = sm([(64.4, 86.4), (74, 84.4), (86, 85.2), (92.6, 90.4), (91.4, 98.6), (83, 103.6), (72, 104.2), (64.8, 99.6), (62.6, 92.6)])
    fig.part('ceph', ceph, CHIT, grad=(90, 86, 66, 104, [(0, '#5a5688'), (0.5, CHIT.base), (1, '#241e3a')]),
             cel=1.6, rim=0.6, cast=1.0, cast_on=['abd'],
             details=[(ellipse(84, 89.6, 3.4, 1.4, -12), CHIT.light, 0.45)])

    for k in ('R3', 'R1'):
        tips[k] = leg_part(fig, k, legs[k], far=False, spines=(k in ('R3', 'R1', 'L2')))

    # ---- le bras lointain (gauche), tendu bas vers l'ennemi, sa dague pointée en avant ----
    SF = mapp(UC, SF0)
    angF = P['angF'] + P['lean']
    GF = mapp(U, P['handF']) if P['handF'] is not HANDF0 else mapp(U, HANDF0)
    WF = add(GF, rot((-3.4, 0.4), angF))
    EF = ik(SF, WF, LUF, LFF, P['bendF'])
    fa = math.degrees(math.atan2(WF[1] - EF[1], WF[0] - EF[0]))
    Lf = math.dist(EF, WF)
    # le bras d'un seul tenant (épaule → coude arrondi → poignet) : pas de jointure visible au coude
    fig.part('farm', arm_shape(SF, EF, WF, (4.4, 3.7, 3.1)), SKIN, cel=0.9, rim=0.4, cast=0)
    brac = xf(rpoly([(Lf * 0.22, -2.5), (Lf + 0.6, -2.3), (Lf + 0.6, 2.3), (Lf * 0.22, 2.5)], 1.0), EF[0], EF[1], fa)
    fig.part('fbrac', brac, CHIT, cel=0.8, rim=0.5, cast=0.6, cast_on=['farm'],
             details=[(xf(ribbon([(Lf * 0.2, -1.4), (Lf * 0.6, -1.6), (Lf, -1.4)], [0.1, 0.6, 0.1]), EF[0], EF[1], fa), CHIT.light, 0.8),
                      (xf(rpoly([(Lf - 0.4, -3), (Lf + 0.7, -3), (Lf + 0.7, 3), (Lf - 0.4, 3)], 0.2), EF[0], EF[1], fa), RED.base, 1)])
    tipF = dagger_parts(fig, 'fd', GF, angF, length=15.5, flip=-1, smear=P['smearF'])
    fist_part(fig, 'ffist', WF, GF, angF, far=True, flip=-1)

    # ---- l'épaulière lointaine ----
    fpad = sm([(87.6, 52.4), (91.2, 49.4), (95.6, 49.8), (97.6, 53.4), (96.6, 57.2), (92.4, 58.4), (88.6, 57.0)])
    fig.part('fpad', fpad, CHIT, cel=0.9, rim=0.6, cast=0.8,
             details=[(ellipse(94.6, 51.6, 1.6, 0.8, -20), CHIT.glint, 0.75)])

    # ---- le buste : cou et décolleté de peau, le haut rouge ajusté, le corset de chitine, la basque ----
    torso = sm([(78.6, 42), (79.0, 48.4), (73.4, 51.6), (66.6, 54.0), (64.4, 58.6), (66.0, 64.6), (70.4, 69.6), (72.6, 74),
                (84.6, 74), (86.4, 69.6), (91.6, 64.4), (93.4, 58.4), (92.2, 54.0), (88.2, 51.6), (86.6, 48.6), (86.6, 42)])
    tdet = [(sm([(80.6, 49.6), (83.0, 52.0), (81.6, 55.4), (79.6, 52.4)]), SKIN.shadow, 0.35),
            (ribbon([(73.2, 54.4), (77.6, 55.8), (81.2, 54.6)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.5),   # clavicule
            (ribbon([(84.0, 54.4), (87.4, 55.2), (90.0, 54.0)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.4),
            (ellipse(85.6, 57.4, 2.6, 1.2, -10), SKIN.hi, 0.6)]
    fig.part('torso', torso, SKIN, grad=(92, 48, 68, 70, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.5, cast=1.0, details=tdet)
    # le ras-du-cou de chitine (fait le tour du cou), une petite pierre rouge devant
    chok = sm([(78.4, 46.4), (82.6, 47.6), (86.8, 46.4), (86.9, 48.8), (82.6, 50.2), (78.3, 48.9)], sharp=(0, 2, 3, 5), t=0.8)
    fig.part('choker', chok, CHIT, cel=0.5, rim=0.4, cast=0.7, cast_on=['torso'],
             details=[(ribbon([(79.0, 47.1), (82.6, 48.2), (86.2, 47.1)], [0.1, 0.45, 0.1]), CHIT.light, 0.8)])
    fig.part('chokgem', sm([(83.6, 48.4), (84.7, 49.6), (83.6, 51.2), (82.5, 49.6)], sharp=(0, 1, 2, 3), t=0.4), RED,
             cel=0.3, rim=0.3, cast=0.4, details=[(ellipse(83.9, 49.3, 0.3, 0.4), '#ffe0c8', 0.9)])
    # le haut rouge : décolleté en V, poitrine modelée (deux volumes, le lointain plus petit)
    top = sm([(65.0, 57.6), (70.6, 56.6), (75.6, 58.0), (79.4, 63.4), (83.2, 58.2), (87.4, 56.4), (92.6, 57.4), (92.8, 62.4),
              (90.2, 67.8), (87.6, 71.6), (70.4, 71.8), (67.0, 66.8), (64.8, 62.0)], sharp=(6,))
    rdet = [(sm([(65.6, 62.2), (70.6, 60.0), (76.2, 61.2), (78.4, 66.0), (75.6, 69.2), (69.6, 68.8), (66.4, 66.0)]), RED.light, 0.35),
            (ribbon([(66.8, 66.8), (71.6, 69.6), (77.2, 69.0), (79.2, 66.6)], [0.2, 1.4, 1.2, 0.2]), RED.shadow, 0.8),
            (ribbon([(80.4, 66.6), (84.2, 69.0), (88.6, 67.6), (90.6, 64.8)], [0.2, 1.1, 0.9, 0.2]), RED.shadow, 0.75),
            (ellipse(71.6, 62.8, 2.4, 1.2, -18), RED.hi, 0.5), (ellipse(86.6, 61.2, 2.0, 1.0, -18), RED.hi, 0.6),
            (ribbon([(79.4, 64.2), (79.6, 67.6), (79.2, 71.0)], [0.1, 0.8, 0.2]), RED.deep, 0.5)]
    fig.part('top', top, RED, grad=(92, 56, 68, 72, [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
             cel=1.0, rim=0.6, cast=0.9, cast_on=['torso'], details=rdet)
    # la bordure de chitine du décolleté (fait le bord du V d'un côté à l'autre)
    vb = sm([(64.8, 57.0), (70.6, 55.8), (75.8, 57.2), (79.4, 62.2), (83.0, 57.4), (87.4, 55.6), (93.0, 56.6), (93.0, 58.4),
             (87.6, 57.6), (83.8, 59.8), (79.4, 65.0), (75.0, 59.4), (70.6, 58.0), (65.0, 59.2)], sharp=(0, 3, 6, 7, 10, 13))
    fig.part('vborder', vb, CHIT, cel=0.4, rim=0.4, cast=0.7, cast_on=['torso', 'top'])
    # le corset : deux plaques de chitine qui serrent la taille
    cor = sm([(69.4, 70.0), (79.4, 71.2), (88.8, 69.6), (86.4, 74.2), (86.8, 79.0), (78.6, 80.0), (70.6, 79.0), (71.6, 74.4)])
    fig.part('corset', cor, CHIT, cel=1.0, rim=0.6, cast=1.0, cast_on=['top', 'torso'],
             details=[(ribbon([(79.2, 71.2), (79.0, 75.2), (79.0, 79.4)], [0.2, 0.9, 0.2]), CHIT.deep, 0.75),
                      (sm([(80.4, 71.2), (87.6, 70.4), (86.8, 74.0), (80.6, 74.6)]), CHIT.light, 0.55),
                      (ellipse(84.6, 72.2, 1.6, 0.6, -6), CHIT.glint, 0.8)])
    # la basque : trois plaques pointues à pointes rouges, la jonction avec l'araignée
    for name, pts, tipc in (
            ('bq1', [(65.0, 78.6), (72.6, 77.6), (73.4, 82.8), (70.4, 89.4), (66.0, 84.6), (63.4, 81.4)], (70.4, 89.4)),
            ('bq3', [(83.4, 77.6), (90.8, 77.4), (93.4, 80.6), (91.4, 84.8), (86.8, 89.0), (84.6, 83.4)], (86.8, 89.0)),
            ('bq2', [(71.6, 77.6), (79.0, 78.6), (86.4, 77.4), (86.0, 83.0), (79.4, 91.6), (72.8, 83.4)], (79.4, 91.6))):
        sh = sm(pts, sharp=(4 if name != 'bq2' else 4,) if name != 'bq1' else (3,), t=0.9)
        tri = sm([add(tipc, (-2.8, -4.0)), add(tipc, (2.8, -4.4)), tipc], sharp=(0, 1, 2), t=0.5)
        fig.part(name, sh, CHIT, cel=1.0, rim=0.6, cast=1.0,
                 details=[(sh, ('lin', pts[1][0] + 3, pts[1][1], pts[0][0], tipc[1], [(0, CHIT.light, 0.55), (1, CHIT.light, 0)]), 1),
                          (tri, ('lin', tipc[0] + 2, tipc[1] - 4, tipc[0] - 1, tipc[1], [(0, RED.light), (1, RED.shadow)]), 1)])

    # ---- le bras proche (droit), levé : bras vers l'arrière, coude sur le côté, avant-bras dressé ----
    S = mapp(UC, S0)
    ang = P['ang'] + P['lean']
    G = mapp(U, P['hand'])
    W = add(G, rot((-3.4, -0.4), ang))
    E = ik(S, W, LU, LF, P['bend'])
    fa_ = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
    Ln = math.dist(E, W)
    # le bras d'un seul tenant (épaule → coude arrondi → poignet) : pas de jointure visible au coude
    fig.part('narm', arm_shape(S, E, W, (5.0, 4.2, 3.4)), SKIN,
             grad=(S[0] + 2, S[1] - 4, E[0] - 2, E[1] + 3, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.shadow)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=['abd', 'torso', 'top', 'L1', 'L2'],
             details=[(limb([lerp(S, E, 0.2), lerp(S, E, 0.8)], [1.0, 0.8]).move(0.3, -1.3), SKIN.hi, 0.4)])
    sg = 1 if math.cos(math.radians(fa_)) > 0 else -1
    nbrac = xf(rpoly([(Ln * 0.18, -2.9), (Ln + 0.7, -2.5), (Ln + 0.7, 2.5), (Ln * 0.18, 2.9)], 1.1), E[0], E[1], fa_)
    fig.part('nbrac', nbrac, CHIT, cel=0.9, rim=0.55, cast=0.8, cast_on=['narm', 'abd', 'L1'],
             details=[(xf(ribbon([(Ln * 0.25, 1.6 * sg), (Ln * 0.6, 1.8 * sg), (Ln, 1.5 * sg)], [0.1, 0.7, 0.1]), E[0], E[1], fa_), CHIT.light, 0.85),
                      (xf(ellipse(Ln * 0.5, 1.4 * sg, 1.3, 0.4), E[0], E[1], fa_), CHIT.glint, 0.8),
                      (xf(rpoly([(Ln - 0.5, -3.2), (Ln + 0.8, -3.2), (Ln + 0.8, 3.2), (Ln - 0.5, 3.2)], 0.2), E[0], E[1], fa_), RED.base, 1)])

    # ---- l'épaulière proche : deux plaques de chitine et un crochet qui remonte ----
    hook = sm([(56.0, 51.6), (54.6, 48.4), (53.8, 45.0), (55.8, 47.0), (58.8, 50.4)], sharp=(2,), t=0.9)
    pad2 = sm([(53.2, 55.0), (58.4, 53.6), (65.4, 55.0), (70.6, 56.6), (69.8, 60.2), (63.4, 61.6), (57.0, 60.6), (53.0, 58.4)])
    pad1 = sm([(54.0, 51.6), (58.6, 48.4), (65.2, 47.6), (70.6, 49.6), (72.6, 53.4), (70.0, 56.6), (62.6, 57.2), (55.6, 56.4)])
    fig.part('padhook', hook, CHIT, cel=0.5, rim=0.5, cast=0)
    fig.part('pad2', pad2, CHIT, cel=0.9, rim=0.6, cast=1.0)
    fig.part('pad1', pad1, CHIT, cel=1.0, rim=0.8, cast=1.0,
             details=[(sm([(56.6, 51.4), (60.6, 49.2), (66.4, 48.8), (70.2, 50.6), (65.8, 51.0), (60.4, 52.4)]), CHIT.light, 0.75),
                      (ellipse(65.6, 50.0, 2.2, 0.75, -6), CHIT.glint, 0.9)])

    # ---- le poing proche et sa dague dressée ----
    tipN = dagger_parts(fig, 'nd', G, ang, length=17.0, flip=1, smear=P['smear'])
    fist_part(fig, 'nfist', W, G, ang)

    # ---- la tête ----
    head_parts = head(fig, P)

    # ---- chaque groupe prend sa pose ----
    fig.pose(['torso', 'top', 'vborder', 'choker', 'chokgem'], TOR)
    fig.pose(['corset', 'bq1', 'bq2', 'bq3'], U)
    fig.pose(['fpad', 'padhook', 'pad2', 'pad1'], UC)
    fig.pose(['abd', 'spinner', 'aspine0', 'aspine1', 'aspine2'], ABD)
    fig.pose(['ceph'], BODY)
    fig.pose(head_parts, HEAD)
    fig.ctx = dict(P=P, tipN=tipN, tipF=tipF, G=G, GF=GF, ang=ang, angF=angF, tips=tips, legs=legs,
                   spinner=mapp(ABD, (19.0, 86.0)), head=mapp(HEAD, (86, 34)), chest=mapp(TOR, (79, 64)), U=U, HEAD=HEAD)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def head(fig, P):
    """Le visage fin de femme, le chignon et ses aiguilles ; rend la liste des morceaux (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- les aiguilles en X (derrière le chignon), perles rouges au bout ----
    C = (72.6, 9.6)                       # le croisement, juste au-dessus du chignon
    for nm, p0 in (('pinA', (66.2, 2.4)), ('pinB', (79.4, 2.8))):
        p1 = (C[0] + (C[0] - p0[0]) * 1.35, C[1] + (C[1] - p0[1]) * 1.35)
        sh = limb([p0, lerp(p0, p1, 0.5), p1], [0.95, 1.0, 1.0])
        part(nm, sh, STEEL, cel=0.3, rim=0.3, cast=0,
             details=[(limb([lerp(p0, p1, 0.02), lerp(p0, p1, 0.9)], [0.3, 0.3]).move(0.2, -0.2), STEEL.hi, 0.8)])
        part(nm + 'b', ellipse(p0[0], p0[1], 1.45, 1.45), RED, cel=0.4, rim=0.35, cast=0.4,
             details=[(ellipse(p0[0] + 0.45, p0[1] - 0.45, 0.45, 0.4), '#fff0e0', 0.95)])
    # ---- le chignon serré, sur l'arrière du crâne ----
    bun = sm([(65.0, 18.6), (67.6, 14.4), (72.4, 12.8), (77.0, 14.6), (78.6, 18.4), (76.4, 22.2), (70.6, 23.6), (66.2, 22.0)])
    part('bun', bun, HAIR, cel=1.0, rim=0.6, cast=0,
         details=[(ribbon([(66.4, 17.4), (70.4, 14.0), (75.6, 14.4)], [0.2, 1.0, 0.2]), HAIR.light, 0.8),
                  (ribbon([(67.0, 20.4), (71.4, 19.8), (76.2, 17.0)], [0.2, 0.7, 0.2]), HAIR.deep, 0.6),
                  (ellipse(74.2, 14.2, 1.3, 0.5, 20), HAIR.glint, 0.7)])

    # ---- le visage ----
    face = sm([(70.0, 30.0), (74.0, 22.0), (81.0, 18.6), (88.2, 20.0), (92.4, 23.6), (94.2, 27.6), (94.4, 31.4),
               (94.0, 33.8), (95.8, 37.2), (96.2, 38.6), (94.6, 39.6), (94.6, 41.0), (94.0, 42.8), (93.2, 45.6),
               (91.2, 47.8), (87.6, 48.8), (83.0, 47.8), (78.6, 45.0), (73.2, 41.0), (70.2, 36.0)], sharp=(9,))
    fd = []
    # les plans du visage : la joue proche et la tempe dans une ombre douce, le plan de face éclairé
    fd += [(sm([(76.0, 30.0), (79.6, 36.6), (81.6, 41.6), (85.4, 46.6), (83.0, 47.8), (78.6, 45.0), (74.0, 40.0)]), SKIN.shadow, 0.55),
           (sm([(87.6, 25.4), (92.4, 25.6), (93.8, 30.2), (92.6, 33.4), (89.6, 31.2)]), SKIN.hi, 0.55),
           (ellipse(90.8, 42.0, 2.2, 1.4, -20), SKIN.hi, 0.25),
           (ellipse(81.6, 40.4, 2.6, 1.5, 10), '#ee9ca4', 0.22),            # la pommette proche (un peu de rose)
           (ellipse(92.0, 39.8, 1.2, 0.9), '#ee9ca4', 0.25)]
    # l'ombre sous le menton (portée par la mâchoire sur le cou : peinte ici en bas du visage)
    fd += [(sm([(84.6, 47.0), (90.4, 46.8), (92.6, 45.4), (91.4, 47.8), (87.6, 48.8), (83.0, 47.8)]), SKIN.shadow, 0.5)]
    blink = P['blink'] > 0.5
    # les sourcils fins et obliques, froncés vers le nez
    fd += [(sm([(77.4, 30.8), (80.6, 30.0), (84.8, 31.7), (85.0, 32.3), (80.8, 31.0), (77.8, 31.5)], sharp=(0, 3), t=0.8), HAIR.base, 1),
           (sm([(88.0, 32.3), (90.6, 30.6), (93.0, 30.0), (93.2, 30.6), (90.8, 31.3), (88.2, 32.8)], sharp=(0, 3), t=0.8), HAIR.base, 1)]
    # les yeux en amande : le trait noir étiré en pointe vers l'arrière, le blanc, l'iris rouge sang, la pupille, l'éclat
    eyes = (
        # (amande, trait du haut étiré, centre de l'iris, rayon de l'iris)
        (sm([(77.6, 34.0), (80.4, 32.9), (84.4, 33.4), (85.4, 35.2), (82.6, 36.8), (79.6, 36.4)], sharp=(0, 3), t=0.9),
         sm([(76.2, 32.6), (80.4, 32.2), (84.6, 32.8), (85.8, 35.2), (84.4, 34.4), (80.4, 33.9), (77.6, 34.2)], sharp=(0, 3), t=0.8),
         (82.6, 34.9), 1.55),
        (sm([(88.4, 34.6), (90.4, 33.2), (92.6, 33.0), (93.2, 34.2), (91.6, 35.8), (89.6, 35.8)], sharp=(0, 3), t=0.9),
         sm([(88.2, 34.4), (90.4, 32.6), (92.8, 32.3), (94.0, 33.2), (92.8, 33.6), (90.6, 33.8), (88.6, 35.0)], sharp=(0, 3), t=0.8),
         (91.4, 34.5), 1.2),
    )
    for almond, liner, (ix, iy), ir in eyes:
        if blink:
            # paupière fermée : la peau, et le trait noir qui reste (un arc)
            fd += [(almond, SKIN.base, 1),
                   (ribbon([lerp(almond_pt(almond, 0), almond_pt(almond, 3), t_) for t_ in (0, 0.5, 1)], [0.2, 0.9, 0.3]).move(0, 1.2), '#2a0a1e', 0.95)]
        else:
            fd += [(almond.scale(1.06, 1.18, ix, iy + 0.2), SKIN.shadow, 0.6), (almond, '#f8eef0', 1)]
            fd += [(clip_ellipse(ix, iy, ir, ir * 1.08), ('rad', ix + 0.3, iy - 0.4, ir * 1.1, ir * 1.1,
                                                            [(0, '#ff7a6a'), (0.45, '#e0303a'), (1, '#8a1630')]), 1),
                   (ellipse(ix - 0.05, iy + 0.05, ir * 0.42, ir * 0.62), '#2a0a1e', 1),
                   (sm([(almond_pt(almond, 0)[0], almond_pt(almond, 0)[1]), almond_pt(almond, 1), almond_pt(almond, 2),
                        almond_pt(almond, 3), lerp(almond_pt(almond, 2), (ix, iy), 0.35), lerp(almond_pt(almond, 1), (ix, iy), 0.4)], t=0.8),
                    SKIN.shadow, 0.35),            # l'ombre de la paupière du haut sur l'œil
                   (ellipse(ix + ir * 0.4, iy - ir * 0.45, ir * 0.28, ir * 0.24), '#fff6ea', 1)]
        fd += [(liner, '#22091c', 1)]
    # les deux petites perles rouges et la pierre taillée au milieu du front (des yeux d'araignée en plus)
    gem = sm([(88.0, 25.9), (89.3, 27.9), (88.0, 30.0), (86.7, 27.9)], sharp=(0, 1, 2, 3), t=0.4)
    fd += [(gem.scale(1.3, 1.2, 88, 28), RED.deep, 0.55), (gem, ('lin', 89.4, 25.4, 86.6, 29.6, [(0, RED.hi), (0.4, RED.light), (1, RED.shadow)]), 1),
           (sm([(88.0, 26.1), (89.1, 27.9), (88.0, 28.1)], sharp=(0, 1, 2), t=0.4), '#ffe0c8', 0.8)]
    for (px_, py_, r_) in ((85.4, 29.2, 0.6), (90.7, 29.0, 0.52)):
        fd += [(ellipse(px_, py_, r_ * 1.25, r_ * 1.25), RED.deep, 0.5), (ellipse(px_, py_, r_, r_), RED.base, 1),
               (ellipse(px_ + 0.18, py_ - 0.2, r_ * 0.4, r_ * 0.36), '#ffd8c0', 0.95)]
    # le petit nez net : lumière sur l'arête, ombre douce en diagonale côté proche, narine, ombre dessous
    fd += [(sm([(87.8, 36.6), (91.4, 38.0), (93.4, 39.6), (91.2, 40.0), (89.0, 39.0)]), SKIN.shadow, 0.5),
           (ribbon([(88.4, 36.4), (92.2, 37.2), (95.0, 38.0)], [0.1, 0.45, 0.3]), SKIN.hi, 0.9),
           (ellipse(93.0, 39.3, 0.65, 0.35, 15), SKIN.deep, 0.85),
           (ribbon([(91.4, 40.2), (93.4, 40.5), (95.0, 40.0)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.5)]
    # le sourire de prédatrice, relevé du côté proche : la gorge rouge sombre, les dents, deux petits crocs
    g = P['grin']
    mouth = sm([(86.4, 41.4 - 0.4 * g), (88.6, 42.0), (91.4, 41.8), (94.0, 41.2), (93.2, 42.8 + 0.4 * g), (90.4, 43.8 + 0.6 * g),
                (88.0, 43.2 + 0.3 * g)], sharp=(0, 3), t=0.9)
    fd += [(mouth.scale(1.05, 1.25, 90.4, 42.6), LIPS[0], 0.75), (mouth, '#5a1028', 1)]
    teeth = sm([(87.2, 41.7), (88.6, 42.15), (91.4, 41.95), (93.6, 41.35), (93.2, 42.2), (91.2, 42.8), (88.4, 42.7)], sharp=(0, 3), t=0.8)
    fd += [(teeth, '#fffaf4', 1),
           (sm([(88.3, 42.4), (88.9, 42.4), (88.65, 43.5)], sharp=(0, 1, 2), t=0.4), '#fffaf4', 1),
           (sm([(92.2, 42.15), (92.8, 42.0), (92.55, 43.0)], sharp=(0, 1, 2), t=0.4), '#fffaf4', 1),
           (ribbon([(90.0, 42.2), (90.1, 42.75)], [0.12, 0.08]), '#d8c8c8', 0.7)]
    # les lèvres : l'arc du haut fin, la lèvre du bas pleine (rouge sombre, reflet)
    fd += [(ribbon([(86.0, 40.9 - 0.4 * g), (88.6, 41.6), (91.2, 41.5), (94.4, 40.9)], [0.1, 0.55, 0.5, 0.1]), LIPS[1], 0.95),
           (sm([(88.0, 43.5 + 0.3 * g), (90.4, 44.0 + 0.6 * g), (92.8, 43.1 + 0.4 * g), (92.2, 44.2), (90.2, 44.7), (88.4, 44.2)], t=0.9), LIPS[1], 0.85),
           (ellipse(91.0, 44.3, 0.9, 0.3, -8), LIPS[2], 0.8),
           (ribbon([(85.6, 40.6 - 0.4 * g), (86.6, 41.4)], [0.1, 0.3]), SKIN.deep, 0.7)]       # la fossette du coin relevé
    part('face', face, SKIN, grad=(94, 24, 74, 46, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, details=fd)

    # ---- la boucle d'oreille rouge (son attache passe sous la chevelure) ----
    e = P['ear']
    ex, ey = 76.6 + 0.5 * e, 46.0
    part('earring', sm([(ex - 0.2, ey - 2.6), (ex + 1.0, ey + 0.6), (ex + 0.1 * e, ey + 2.6), (ex - 1.0, ey + 0.6)], sharp=(0, 2), t=0.9),
         RED, cel=0.4, rim=0.35, cast=0.5, details=[(ellipse(ex + 0.3, ey + 0.1, 0.35, 0.45), '#ffd8c0', 0.9)])
    # ---- la chevelure : une seule forme lisse, plaquée sur le crâne, front haut dégagé ----
    hair = sm([(63.4, 27.6), (66.0, 19.6), (72.0, 15.6), (80.4, 15.8), (87.8, 18.0), (92.6, 21.8), (94.2, 25.6),
               (90.8, 24.4), (86.4, 24.6), (82.0, 26.6), (78.6, 30.4), (76.6, 35.0), (76.8, 40.2), (78.4, 44.4),
               (75.0, 45.6), (70.6, 44.6), (66.4, 40.4), (63.8, 34.4)], sharp=(6, 13), t=0.95)
    # les mèches plaquées partent du front et filent vers le chignon (arcs doux, inégaux)
    hd = [(ribbon([(91.6, 22.6), (85.4, 18.6), (77.6, 17.2), (70.6, 18.6)], [0.2, 1.5, 1.2, 0.2]), HAIR.light, 0.75),
          (ribbon([(88.6, 20.0), (82.4, 17.8), (76.0, 17.8)], [0.1, 0.55, 0.1]), HAIR.glint, 0.6),
          (ribbon([(84.6, 25.6), (78.0, 23.0), (71.4, 22.6), (66.4, 25.0)], [0.1, 0.9, 0.8, 0.1]), HAIR.light, 0.45),
          (ribbon([(78.4, 31.8), (73.4, 28.6), (68.0, 29.2)], [0.1, 0.8, 0.1]), HAIR.deep, 0.5),
          (ribbon([(76.6, 39.6), (71.6, 36.2), (66.6, 35.6)], [0.1, 0.7, 0.1]), HAIR.deep, 0.45)]
    part('hair', hair, HAIR, grad=(92, 16, 66, 42, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]),
         cel=1.1, rim=0.6, cast=1.0, cast_on=['face'], details=hd)
    return names


def arm_shape(S, E, W, ws):
    """Un bras d'un seul tenant : la ligne passe par l'épaule, tourne en douceur au coude, finit au poignet ; la largeur
    s'affine de l'épaule au poignet (le coude reste plein)."""
    l1, l2 = math.dist(S, E), math.dist(E, W)
    r = min(2.4, 0.3 * l1, 0.3 * l2)
    a = lerp(E, S, r / l1)
    b = lerp(E, W, r / l2)
    c = []
    for i in range(6):
        c.append(lerp(S, a, i / 6))
    for i in range(7):
        t = i / 6
        c.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * E[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * E[1] + t * t * b[1]))
    for i in range(1, 6):
        c.append(lerp(b, W, i / 5))
    n = len(c)
    w0, we, ww = ws
    widths = []
    for i in range(n):
        if i <= 9:
            widths.append(w0 + (we - w0) * i / 9)
        else:
            widths.append(we + (ww - we) * (i - 9) / (n - 1 - 9))
    return limb(c, widths)


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


def clip_ellipse(cx, cy, rx, ry):
    return ellipse(cx, cy, rx, ry)


def main():
    """soyane.svg (grand) et soyane-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-10.webp (512 px de haut) et myths-10-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('soyane', 0.95, 512, 'myths-10'), ('soyane-petit', 1.35, 160, 'myths-10-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
